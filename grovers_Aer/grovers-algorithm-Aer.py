"""
This script demonstrates the implementation of Grover's Algorithm to break a simple AES encryption using quantum computing.
Grover's Algorithm is a quantum search algorithm that provides a quadratic speedup over classical algorithms for unstructured search problems.

This script includes:
1. AES encryption function in C, interfaced with Python using ctypes.
2. Grover's Algorithm implemented using Qiskit, a quantum computing framework.
3. Execution of the quantum circuit on the AerSimulator (Qiskit's simulator).
4. Visualization of the results.

Components:
- AES Encryption: Uses a shared library (DLL) for AES encryption. The AES key and plaintext are provided as inputs, and the ciphertext is generated.
- Grover's Algorithm: Quantum search algorithm that searches for the correct AES key in a superposition of possible keys.
- Qiskit: A Python library for quantum computing. Used here to create and execute the quantum circuit.
- AerSimulator: Qiskit's simulator for running quantum circuits.

Functions:
- aes_encrypt: Encrypts plaintext using AES with the provided key.
- hex_to_bin: Converts a hexadecimal string to a binary string.
- create_oracle: Creates the oracle part of the Grover's circuit, which marks the correct key.
- create_diffuser: Creates the diffuser part of the Grover's circuit, which amplifies the probability of the correct key.
- grovers_algorithm: Assembles the full Grover's algorithm circuit.
- execute_grover: Executes the Grover's circuit on AerSimulator.

Usage:
1. Ensure the AES shared library (DLL) is in the same directory as this script.
2. If you are not running Python3.9.0 or below, create a virtual environment with Python3.9.0. Instructions are detailed in the README.md file.
3. Install necessary Python packages: qiskit, qiskit-aer, numpy, matplotlib.
5. Run the script.
"""

import ctypes
import os
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
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

def create_oracle(nqubits, plaintext, expected_ciphertext):
    """
    Creates the oracle circuit for Grover's algorithm.

    :param nqubits: The number of qubits
    :param plaintext: The plaintext to be encrypted
    :param expected_ciphertext: The expected ciphertext to compare against
    :return: The oracle gate
    """
    oracle = QuantumCircuit(nqubits + 1)  # +1 for the ancilla qubit

    def check_key(key_bits):
        """
        Checks if the given key bits produce the expected ciphertext.

        :param key_bits: The key bits to check
        :return: True if the key produces the expected ciphertext, False otherwise
        """
        key = ''.join(map(str, key_bits))
        encrypted = aes_encrypt(key, plaintext)
        return encrypted == expected_ciphertext

    # For simplicity, let's assume the target state is all '1's
    target_state = '1' * nqubits  # Update this as necessary

    # Apply X gates to qubits corresponding to '0' in the target state
    for i, bit in enumerate(target_state):
        if bit == '0':
            oracle.x(i)

    # Add Hadamard gate to the ancilla qubit and perform the multi-controlled Toffoli gate
    oracle.h(nqubits)  # Hadamard on ancilla
    oracle.mcx(list(range(nqubits)), nqubits)  # Multi-controlled Toffoli
    oracle.h(nqubits)  # Hadamard on ancilla

    # Apply X gates again to qubits corresponding to '0' in the target state
    for i, bit in enumerate(target_state):
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

def grovers_algorithm(nqubits, plaintext, expected_ciphertext):
    """
    Implements Grover's algorithm to search for the target key.

    :param nqubits: The number of qubits
    :param plaintext: The plaintext to be encrypted
    :param expected_ciphertext: The expected ciphertext to compare against
    :return: The Grover circuit
    """
    grover = QuantumCircuit(nqubits + 1, nqubits)  # +1 for the ancilla qubit
    grover.h(range(nqubits))  # Apply Hadamard gates to all qubits to create superposition
    grover.x(nqubits)  # Initialize ancilla qubit to |1>
    grover.h(nqubits)

    oracle_gate = create_oracle(nqubits, plaintext, expected_ciphertext)
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
    Executes the Grover circuit on the AerSimulator.

    :param grover_circuit: The Grover circuit to be executed
    :return: The result counts from the execution
    """
    backend = AerSimulator()
    compiled_circuit = transpile(grover_circuit, backend)
    result = backend.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts(grover_circuit)
    return counts

nqubits = 4  # Number of qubits for an intermediate test case
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

# Create the Grover circuit
grover_circuit = grovers_algorithm(nqubits, plaintext, expected_ciphertext)

# Execute the Grover circuit
counts = execute_grover(grover_circuit)

# Display the result counts
print("Counts:", counts)
plot_histogram(counts).show()

# Keep the plot window open
plt.show()
