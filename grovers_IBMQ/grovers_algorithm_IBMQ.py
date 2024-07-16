"""
!!! IMPORTANT !!!
----------------------------------------------------------------------------------------------------------------
| Run this script only if you have access to IBMQ's quantum hardware. Otherwise, the script will not execute.  |
| IBMQ compute resources are limited and may require queuing for execution, not to mention wildly expensive.   |
|                                                                                                              |                                   
| Run the './grover_Aer/grovers_algorithm_aer.py' script instead, which uses the qiskit's                      |
| AerSimulator for local execution.                                                                            |
----------------------------------------------------------------------------------------------------------------

This script demonstrates the implementation of Grover's Algorithm to break a simple AES encryption using quantum computing.
Grover's Algorithm is a quantum search algorithm that provides a quadratic speedup over classical algorithms for unstructured search problems.

This script includes:
1. AES encryption function in C, interfaced with Python using ctypes.
2. Grover's Algorithm implemented using Qiskit, a quantum computing framework.
3. Execution of the quantum circuit on IBMQ's quantum hardware.
4. Visualization of the results.

Components:
- AES Encryption: Uses a shared library (DLL) for AES encryption. The AES key and plaintext are provided as inputs, and the ciphertext is generated.
- Grover's Algorithm: Quantum search algorithm that searches for the correct AES key in a superposition of possible keys.
- Qiskit: A Python library for quantum computing. Used here to create and execute the quantum circuit.
- IBMQ: IBM's quantum cloud platform, used to run the quantum circuit on real quantum hardware.

Functions:
- aes_encrypt: Encrypts plaintext using AES with the provided key.
- hex_to_bin: Converts a hexadecimal string to a binary string.
- create_oracle: Creates the oracle part of the Grover's circuit, which marks the correct key.
- create_diffuser: Creates the diffuser part of the Grover's circuit, which amplifies the probability of the correct key.
- grovers_algorithm: Assembles the full Grover's algorithm circuit.
- execute_grover: Executes the Grover's circuit on IBMQ's least busy backend.

Usage:
1. Ensure the AES shared library (DLL) is in the same directory as this script.
2. If you are not running Python3.12.4 or below, create a virtual environment with Python3.12.4. Instructions are detailed in the README.md.
3. Install necessary Python packages: Qiskit, numpy, matplotlib.
4. Replace the placeholder in IBMQ.save_account('YOUR_API_TOKEN') with your actual IBMQ API token.
5. Run the script.
"""

import ctypes
import os
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Load the AES shared library
aes_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__),"..",'aes.dll'), winmode=0)

# Define the C function interface for the AES encryption
aes_lib.encrypt.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
aes_lib.encrypt.restype = None

def aes_encrypt(key, plaintext):
    """
    Encrypts the given plaintext with the provided key using the AES encryption.

    :param key: The encryption key in hexadecimal format (32 hex characters)
    :param plaintext: The plaintext to be encrypted
    :return: The ciphertext resulting from the encryption
    """
    key_bytes = bytes.fromhex(key)
    plaintext_bytes = plaintext.encode('utf-8')
    ciphertext = (ctypes.c_ubyte * 16)()  # Assuming 128-bit AES

    # Ensure key and plaintext are correctly padded/truncated to 16 bytes
    if len(key_bytes) != 16:
        raise ValueError("Key must be 16 bytes (32 hex characters)")
    if len(plaintext_bytes) > 16:
        raise ValueError("Plaintext must be at most 16 bytes")
    if len(plaintext_bytes) < 16:
        plaintext_bytes += b'\x00' * (16 - len(plaintext_bytes))  # Pad with null bytes if necessary

    # Convert key and plaintext to ctypes arrays
    key_array = (ctypes.c_ubyte * 16).from_buffer_copy(key_bytes)
    plaintext_array = (ctypes.c_ubyte * 16).from_buffer_copy(plaintext_bytes)

    # Call the AES encryption function from the shared library
    aes_lib.encrypt(key_array, plaintext_array, ciphertext)
    return bytes(ciphertext)

def hex_to_bin(hex_string):
    """
    Converts a hexadecimal string to a binary string.

    :param hex_string: The hexadecimal string to be converted
    :return: The binary representation of the hexadecimal string
    """
    return bin(int(hex_string, 16))[2:].zfill(128)  # 128-bit key

def create_oracle(nqubits, target_key_bin):
    """
    Creates the oracle circuit for Grover's algorithm.

    :param nqubits: The number of qubits
    :param target_key_bin: The target key in binary format
    :return: The oracle gate
    """
    oracle = QuantumCircuit(nqubits + 1)  # +1 for the ancilla qubit

    # Apply X gates to qubits corresponding to '0' in the target key binary string
    for i, bit in enumerate(target_key_bin):
        if bit == '0':
            oracle.x(i)

    # Add Hadamard gate to the ancilla qubit and perform the multi-controlled Toffoli gate
    oracle.h(nqubits)
    oracle.mcx(list(range(nqubits)), nqubits)
    oracle.h(nqubits)

    # Apply X gates again to qubits corresponding to '0' in the target key binary string
    for i, bit in enumerate(target_key_bin):
        if bit == '0':
            oracle.x(i)

    oracle_gate = oracle.to_gate()
    oracle_gate.name = "Oracle"
    return oracle_gate

def create_diffuser(nqubits):
    """
    Creates the diffuser circuit for Grover's algorithm.

    :param nqubits: The number of qubits
    :return: The diffuser gate
    """
    diffuser = QuantumCircuit(nqubits)
    diffuser.h(range(nqubits))
    diffuser.x(range(nqubits))
    diffuser.h(nqubits - 1)
    diffuser.mcx(list(range(nqubits - 1)), nqubits - 1)
    diffuser.h(nqubits - 1)
    diffuser.x(range(nqubits))
    diffuser.h(range(nqubits))
    diffuser_gate = diffuser.to_gate()
    diffuser_gate.name = "Diffuser"
    return diffuser_gate

def grovers_algorithm(nqubits, target_key_bin):
    """
    Implements Grover's algorithm to search for the target key.

    :param nqubits: The number of qubits
    :param target_key_bin: The target key in binary format
    :return: The Grover circuit
    """
    grover = QuantumCircuit(nqubits + 1, nqubits)  # +1 for the ancilla qubit
    grover.h(range(nqubits))  # Apply Hadamard gates to all qubits to create superposition
    grover.x(nqubits)  # Initialize ancilla qubit to |1>
    grover.h(nqubits)

    oracle_gate = create_oracle(nqubits, target_key_bin)
    diffuser_gate = create_diffuser(nqubits)

    # Determine the number of iterations for Grover's algorithm
    num_iterations = int(np.pi / 4 * np.sqrt(float(2**nqubits)))
    for _ in range(num_iterations):
        grover.append(oracle_gate, range(nqubits + 1))
        grover.append(diffuser_gate, range(nqubits))

    grover.measure(range(nqubits), range(nqubits))
    return grover

def execute_grover(grover_circuit):
    """
    Executes the Grover circuit on the least busy IBM Q backend.

    :param grover_circuit: The Grover circuit to be executed
    :return: The result counts from the execution
    """
    service = QiskitRuntimeService()
    backend = service.least_busy_backend(minimum_qubits=nqubits, simulator=False)

    with Session(service=service, backend=backend) as session:
        sampler = Sampler(session=session)
        job = sampler.run(circuits=[grover_circuit])
        result = job.result()
        counts = result.get_counts(grover_circuit)
        return counts

nqubits = 128  # Number of qubits for a 128-bit key
plaintext = "This is a test"  # Example plaintext (16 bytes)
key = "00112233445566778899aabbccddeeff"  # The correct key (16 bytes)
expected_ciphertext = bytes.fromhex('3c86e7ec17bb967b9da2f2242d94a634')

# Encrypt the plaintext using the provided key
ciphertext = aes_encrypt(key, plaintext)

# Verify if the produced ciphertext matches the expected ciphertext
if ciphertext != expected_ciphertext:
    print(f"Error: The AES encryption function did not produce the expected ciphertext.")
else:
    print("Success: The AES encryption function produced the expected ciphertext")

# Convert the target key to binary format
target_key_bin = hex_to_bin(key)

# Create the Grover circuit
grover_circuit = grovers_algorithm(nqubits, target_key_bin)

# Execute the Grover circuit
counts = execute_grover(grover_circuit)

# Display the result counts
print("Counts:", counts)
plot_histogram(counts).show()

# Keep the plot window open
plt.show()
