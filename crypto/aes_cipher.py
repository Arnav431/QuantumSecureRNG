from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def encrypt(message, key):
    """
    Encrypt a message using AES-256 in CBC mode.
    
    Args:
        message: String to encrypt
        key: 32-byte encryption key
        
    Returns:
        bytes: IV + ciphertext (IV is prepended to the ciphertext)
    """
    cipher = AES.new(key, AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))

    return iv + ciphertext

def decrypt(ciphertext, key):
    """
    Decrypt a message that was encrypted with AES-256 CBC mode.
    
    Args:
        ciphertext: bytes containing IV + encrypted data
        key: 32-byte encryption key
        
    Returns:
        str: Decrypted message
    """

    iv = ciphertext[:AES.block_size]
    actual_ciphertext = ciphertext[AES.block_size:]
    
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decrypted = unpad(cipher.decrypt(actual_ciphertext), AES.block_size)
    return decrypted.decode()