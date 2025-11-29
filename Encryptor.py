import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from typing import Callable
from typing import Optional

MAGIC_HEADER = "MYENC1\n"

class Encryptor:
    def __init__(self):
        self.wasEncrypted = False
    def derive_key(self, password: str) -> bytes:        
        hash_bytes = hashlib.sha256(password.encode("utf-8")).digest()  
        return base64.urlsafe_b64encode(hash_bytes)  

    def encrypt(self, text: str, key: bytes):
        print("started encryption")
        f = Fernet(key)
        token = f.encrypt(text.encode("utf-8"))
        self.wasEncrypted
        print("encrypted")
        return MAGIC_HEADER + token.decode("utf-8")
    
    def decrypt(self, text: str, key: bytes):
        print("decrypted")
        f = Fernet(key)
        decrypted = f.decrypt(text.encode("utf-8"))
        return decrypted.decode("utf-8")
    def decryptIfNeeded(self, text: str, hashCallBacl: Callable[..., Optional[bytes|None]]):
        if text.startswith(MAGIC_HEADER):
            text = text[len(MAGIC_HEADER):]  # убираем MAGIC_HEADER правильно
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