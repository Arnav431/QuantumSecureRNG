# QuantumSecureRNG

QuantumSecureRNG is a Python project that demonstrates quantum-secure cryptography by fetching true random numbers from IBM Quantum jobs and using them for cryptographic key generation and encryption.

## How It Works

1. **Fetch Quantum Randomness**
   - Uses IBM Quantum's Qiskit Runtime to retrieve measurement results from a completed quantum job (specified by `JOB_ID`).
   - Extracts random bitstrings from the quantum job result.

2. **Key Derivation**
   - Derives a cryptographic key from the quantum-generated random bits using SHA-256.

3. **Encryption**
   - Encrypts a message using the derived quantum-secure key with AES encryption.

## Main Components

- `main.py`: Entry point. Fetches quantum randomness, derives a key, and encrypts a sample message.
- `quantum/qrng.py`: Contains logic to interface with IBM Quantum and extract random bits from a quantum job.
- `crypto/key_manager.py`: Handles key derivation from quantum bits.
- `crypto/aes_cipher.py`: Performs AES encryption.

## Setup

1. **Install Dependencies**
   - Python 3.8+
   - Install required packages:
     ```bash
     pip install qiskit qiskit-ibm-runtime python-dotenv
     ```

2. **IBM Quantum API Key**
   - Get your API key from https://quantum-computing.ibm.com/account
   - Save your account using Python:
     ```python
     from qiskit_ibm_runtime import QiskitRuntimeService
     QiskitRuntimeService.save_account(channel="ibm_quantum", token="YOUR_API_KEY")
     ```

3. **Configure JOB_ID**
   - Set the `JOB_ID` variable in `main.py` to the ID of a completed IBM Quantum job containing measurement results.

## Usage

Run the main script:
```bash
python main.py
```

## Output
- Fetches quantum randomness from IBM Quantum.
- Derives a cryptographic key from the quantum bits.
- Encrypts a sample message and prints confirmation.

## Notes for Developers
- The code is modular and can be extended to use different quantum jobs or encryption schemes.
- Error handling for result formats is included in `quantum/qrng.py`.
- For reference or integration with other AI agents, see the structure and flow in `main.py` and `quantum/qrng.py`.
