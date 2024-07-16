# Description: Save the IBMQ token to the local system (IBMQ account required: https://quantum.ibm.com/api/login?provider=ibmid&redirectTo=https%3A%2F%2Fquantum.ibm.com%2Flogin)
from qiskit_ibm_runtime import QiskitRuntimeService

# Replace 'YOUR_API_TOKEN' with your actual API token
QiskitRuntimeService.save_account(channel="ibm_quantum", token="{COPY_TOKEN_HERE}")
