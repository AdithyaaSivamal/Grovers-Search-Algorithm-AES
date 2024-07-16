from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# Create a simple quantum circuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

# Use the AerSimulator backend
backend = AerSimulator()
compiled_circuit = transpile(qc, backend)
result = backend.run(compiled_circuit, shots=1024).result()

# Print the backend information and the result counts
print(backend)
counts = result.get_counts(qc)
print("Counts:", counts)
