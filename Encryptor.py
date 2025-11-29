import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from typing import Callable
from typing import Optional
import secrets


HEADER = "MYENC1\n"

ITERATIONS = 100_000
class Encryptor:
    def __init__(self):
        self.wasEncrypted = False
    def derive_key(self, password: str) -> bytes:        
        password_bytes = password.encode("utf-8")
        salt = secrets.token_bytes(32) 
        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password_bytes,
            salt=salt,
            iterations=ITERATIONS,
            dklen=32
        )
        return base64.urlsafe_b64encode(key)

    def encrypt(self, text: str, key: bytes):
        print("started encryption")
        f = Fernet(key)
        token = f.encrypt(text.encode("utf-8"))
        self.wasEncrypted
        print("encrypted")
        return HEADER + token.decode("utf-8")
    
    def decrypt(self, text: str, key: bytes):
        print("decrypted")
        f = Fernet(key)
        decrypted = f.decrypt(text.encode("utf-8"))
        return decrypted.decode("utf-8")
    def decryptIfNeeded(self, text: str, hashCallBacl: Callable[..., Optional[bytes|None]]):
        if text.startswith(HEADER):
            text = text[len(HEADER):]  
            decrypted = None
            try:
                key: bytes|None = hashCallBacl(reset = True)
                if (key != None): 
                    decrypted = self.decrypt(text, key)
                else:
                    return None
                self.wasEncrypted = True
            except InvalidToken:
                print("failed to dycrypt")
                return None
            return decrypted
        self.wasEncrypted = False
        return text