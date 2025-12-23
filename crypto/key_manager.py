from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

def derive_key(quantum_bits, key_length=32):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=None,
        info=b'quantum-rng-key',
    )
    key = hkdf.derive(quantum_bits.encode())
    return key