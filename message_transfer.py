import binascii

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class Message:
    def __init__(self, key):
        self.key = key
        self.symmetric_byte_key = binascii.unhexlify(key)

    def encrypt_message(self, message):
        iv = get_random_bytes(16)  # 16 bytes IV for AES
        cipher = AES.new(self.symmetric_byte_key, AES.MODE_CBC, iv)
        encrypted_message = iv + cipher.encrypt(pad(message.encode(), AES.block_size))
        return encrypted_message.hex()

    def decrypt_message(self, encrypted_message):
        byte_encrypted_message = binascii.unhexlify(encrypted_message)
        iv = byte_encrypted_message[
            :16
        ]  # Extract IV from the start of the encrypted message
        cipher = AES.new(self.symmetric_byte_key, AES.MODE_CBC, iv)
        decrypted_message = unpad(
            cipher.decrypt(byte_encrypted_message[16:]), AES.block_size
        )
        return decrypted_message.decode()
        return decrypted_message.decode()
