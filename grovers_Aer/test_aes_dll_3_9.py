import ctypes
import os

# Full path to the shared library
#aes_lib = ctypes.CDLL('C:/Path/to/Grovers-Search_Algorithm/aes.dll', winmode=0)
aes_lib = ctypes.CDLL(os.path.join(os.path.dirname(__file__),"..",'aes.dll'), winmode=0)

# Define the C function interface
aes_lib.encrypt.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_ubyte)]
aes_lib.encrypt.restype = None

def aes_encrypt(key, plaintext):
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

    key_array = (ctypes.c_ubyte * 16).from_buffer_copy(key_bytes)
    plaintext_array = (ctypes.c_ubyte * 16).from_buffer_copy(plaintext_bytes)

    aes_lib.encrypt(key_array, plaintext_array, ciphertext)
    return bytes(ciphertext)

#test inputs
key = "00112233445566778899aabbccddeeff"
plaintext = "This is a test"
expected_ciphertext = bytes.fromhex('3c86e7ec17bb967b9da2f2242d94a634')

# Encrypt plaintext using the provided key
ciphertext = aes_encrypt(key, plaintext)

print(f"Ciphertext: {ciphertext}")
print(f"Expected ciphertext: {expected_ciphertext}")

# Check if the ciphertext matches the expected value
if ciphertext != expected_ciphertext:
    print(f"Error: The AES encryption function did not produce the expected ciphertext.")
else:
    print("Success: The AES encryption function produced the expected ciphertext.")
