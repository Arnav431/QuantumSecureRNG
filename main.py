from quantum.qrng import quantum_bits_from_job, validate_quantum_bits
from crypto.key_manager import derive_key
from crypto.aes_cipher import encrypt, decrypt
from utils.helpers import save_to_file
import os

JOB_ID = "d5421bhsmlfc739fbpm0"

def main():
    try:
        print("[+] Fetching quantum randomness from IBM Quantum job...")
        quantum_bits = quantum_bits_from_job(JOB_ID)
        
        # Validate the quantum randomness
        validate_quantum_bits(quantum_bits)
        
        # Derive encryption key
        print("[+] Deriving cryptographic key from quantum bits...")
        key = derive_key(quantum_bits)
        
        # Encrypt message
        message = "Quantum-secure cryptography using IBM Quantum"
        print(f"[+] Encrypting message: '{message}'")
        ciphertext = encrypt(message, key)
        
        print("[✓] Encryption complete")
        
        # Demonstrate decryption
        print("[+] Verifying decryption...")
        decrypted = decrypt(ciphertext, key)
        
        if decrypted == message:
            print("[✓] Decryption successful - message integrity verified")
        else:
            print("[✗] Decryption failed - message mismatch!")
            return 1
        
        # Save outputs
        os.makedirs("output", exist_ok=True)
        
        key_info = f"""Quantum-Secure Encryption Key
================================
Job ID: {JOB_ID}
Quantum Bits: {len(quantum_bits)} bits
Key Length: {len(key)} bytes ({len(key) * 8} bits)
Key (hex): {key.hex()}

Message: {message}
Ciphertext Length: {len(ciphertext)} bytes
"""
        
        save_to_file("output/keys.txt", key_info)
        save_to_file("output/encrypted.bin", ciphertext, binary=True)
        
        print(f"\n[+] Key information saved to output/keys.txt")
        print(f"[+] Ciphertext saved to output/encrypted.bin")
        print(f"\n{'='*50}")
        print(f"Summary:")
        print(f"  • Quantum entropy: {len(quantum_bits)} bits")
        print(f"  • Key strength: AES-{len(key) * 8}")
        print(f"  • Message length: {len(message)} characters")
        print(f"  • Ciphertext size: {len(ciphertext)} bytes")
        print(f"{'='*50}\n")
        
        return 0
        
    except Exception as e:
        print(f"[✗] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())