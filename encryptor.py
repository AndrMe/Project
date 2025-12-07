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
    def __init__(self, psswdCallback: Callable[..., Optional[str]]):
        self.wasEncrypted = False
        self.psswdHash = None
        self.salt = None
        self.psswdCallback = psswdCallback

    def reset(self):
        self.psswdHash = None
        self.salt = None
    def getKey(self, reset:bool = False) -> bytes|None:
        if (reset): self.reset()
        if (self.psswdHash is not None):
            return self.psswdHash
        password: str|None = self.psswdCallback()
        if (password == None):
            return None
        password_bytes = password.encode("utf-8")
        if self.salt is None:  
            self.salt = secrets.token_bytes(32)
         
        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password_bytes,
            salt=self.salt,
            iterations=ITERATIONS,
            dklen=32
        )
        self.psswdHash = base64.urlsafe_b64encode(key)
        return self.psswdHash
    def getKeyFromSalt(self, salt:bytes) -> bytes|None:
        passwd = self.psswdCallback()
        if (passwd is None): return None
        password_bytes = passwd.encode("utf-8")
        self.salt = salt
        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password_bytes,
            salt=self.salt,
            iterations=ITERATIONS,
            dklen=32
        )
        self.psswdHash = base64.urlsafe_b64encode(key)
        return self.psswdHash

    def encrypt(self, text: str, reset: bool = False):
        key = self.getKey(reset= reset)
        if key is None:
            raise ValueError("Cannot encrypt: no password provided")
        
        if self.salt is None:
            raise ValueError("Cannot encrypt: salt not generated")
        f = Fernet(key)
        token = f.encrypt(text.encode("utf-8"))
        self.wasEncrypted = True
        salt_b64 = base64.b64encode(self.salt).decode("utf-8")
        return HEADER + salt_b64 + "\n" + token.decode("utf-8")

    
    def decrypt(self, text: str, key: bytes):
        f = Fernet(key)
        decrypted = f.decrypt(text.encode("utf-8"))
        return decrypted.decode("utf-8")
    def extract_salt(self, text: str) -> bytes | None:
        if not text.startswith(HEADER):
            return None
        try:
            body = text[len(HEADER):]
            salt_b64, _ = body.split("\n", 1)
            salt = base64.b64decode(salt_b64)
            return salt
        except Exception:
            return None

    def decryptIfNeeded(self, text: str):
        if not text.startswith(HEADER):
            self.wasEncrypted = False
            self.reset()
            return text

        salt = self.extract_salt(text)
        if salt is None:
            return None

        key = self.getKeyFromSalt(salt)
        if key is None:
            return None

        try:
            _, token = text[len(HEADER):].split("\n", 1)
            decrypted = self.decrypt(token, key)
            self.wasEncrypted = True
            return decrypted
        except InvalidToken:
            return None
