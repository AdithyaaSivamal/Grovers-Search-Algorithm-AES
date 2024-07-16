# Grover's Search Algorithm for AES

This repository contains implementations of Grover's Search Algorithm for exploring how it can be used to potentially break an AES key. There are two scripts provided:

- `grovers_algorithm_aer.py`: Uses Qiskit Aer for local simulations.
- `grovers_algorithm_IBMQ.py`: Uses IBM Quantum runtime for cloud-based quantum computations.

## Setup

### Prerequisites

Make sure you have Python 3.9 and Python 3.12.4 installed on your system.

### Environment Setup for `grovers_algorithm_aer.py`

1. Create a virtual environment with Python 3.9:
    ```bash
    python -m venv env3.9
    ```

2. Activate the virtual environment:
    - On Windows:
      ```bash
      .\env3.9\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source env3.9/bin/activate
      ```

3. Install the required packages:
    ```bash
    pip install qiskit qiskit-aer matplotlib
    ```

### Environment Setup for `grovers_algorithm_IBMQ.py`

1. Create a virtual environment with Python 3.12.4:
    ```bash
    python3 -m venv env3.12.4
    ```

2. Activate the virtual environment:
    - On Windows:
      ```bash
      .\env3.12.4\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source env3.12.4/bin/activate
      ```

3. Install the required packages:
    ```bash
    pip install qiskit qiskit-ibm-runtime matplotlib
    ```


## Tests

This repository includes some test scripts to verify the accessibility of required resources and environments.

### Test Scripts

- `test_aes_dll_3.9.py`: Tests the accessibility of `aes.dll` using Python 3.9.
- `test_aes_dll_3.12.4.py`: Tests the accessibility of `aes.dll` using Python 3.12.4.
- `test_aer_simulator.py`: Tests the accessibility of the Qiskit AerSimulator backend.

### Running the Test Scripts


#### Testing `aes.dll` with Python 3.9

1. Activate the Python 3.9 environment:
    ```bash
    .\env3.9\Scripts\activate
    ```

2. Run the test script:
    ```bash
    python tests/test_aes_dll_3.9.py
    ```

#### Testing `aes.dll` with Python 3.12.4

1. Activate the Python 3.12.4 environment:
    ```bash
    .\env3.12.4\Scripts\activate
    ```

2. Run the test script:
    ```bash
    python tests/test_aes_dll_3.12.4.py
    ```

#### Testing the AerSimulator Backend

1. Activate the Python 3.9 environment:
    ```bash
    .\env3.9\Scripts\activate
    ```

2. Run the test script:
    ```bash
    python tests/test_aer_simulator.py
    ```

These test scripts help ensure that your environment is correctly set up and that all necessary resources are accessible.

## Running the Scripts

### Running `grovers_algorithm_aer.py`

1. Activate the Python 3.9 environment:
    - On Windows:
      ```bash
      .\env3.9\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source env3.9/bin/activate
      ```

2. Run the script:
    ```bash
    python grovers_algorithm_aer.py
    ```

### Running `grovers_algorithm_IBMQ.py`

1. Activate the Python 3.12.4 environment:
    - On Windows:
      ```bash
      .\env3.12.4\Scripts\activate
      ```
    - On macOS and Linux:
      ```bash
      source env3.12.4/bin/activate
      ```

2. Run the script:
    ```bash
    python grovers_algorithm_IBMQ.py
    ```

## Notes

- Ensure you have your `aes.dll` file in the appropriate directory as mentioned in the scripts.
- Make sure you have access to IBM Quantum runtime for running the `grovers_algorithm_IBMQ.py` script.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
