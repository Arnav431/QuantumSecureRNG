from qiskit_ibm_runtime import QiskitRuntimeService
import os
from dotenv import load_dotenv

load_dotenv()

def get_backend():
    service = QiskitRuntimeService(
    channel="ibm_quantum_platform",
    token=os.getenv("IBM_QUANTUM_TOKEN")
    )
    return service.backend("ibm_torino")
