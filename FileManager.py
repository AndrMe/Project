from __future__ import annotations
from tkinter import filedialog, messagebox
from typing import Optional

import os
from typing import TYPE_CHECKING
from  psswd import *
if TYPE_CHECKING:
    from app import Context 

tempName = "~$temp."

class FileManager:
    def __init__(self, context: Context) -> None:
        self.context = context
        self.encryptor = context.encryptor
        self.x = 0
        #fields
        self.loadedFileName:Optional[str|None] = None
        self.isEncrypted = False

        self.psswdHash: bytes | None = None


    def save(self, text:str)->bool:
        fileName = self.loadedFileName
        if (not(fileName)):
            fileName = filedialog.asksaveasfilename(initialfile="newFile.txt")
        if (fileName):
            if (self.isEncrypted):
                passwd = self.getPassword()
                if (not(passwd)): return False
                text = self.__encrypt(text, passwd)
            self.__safeSaveToDisc(text, fileName)
            return True
        return False

    def saveAs(self, text:str):
        if  (self.loadedFileName):
            suggest = self.__removeEncName(self.loadedFileName)
        else: suggest = "newFile.txt"
        
        fileName = filedialog.asksaveasfilename(initialfile=suggest)
        if (fileName):
            self.__safeSaveToDisc(text, fileName)
            self.setEncr(False)
            
    def setEncr(self, encr:bool):
        if (not(encr)):
            self.isEncrypted = False
            self.psswdHash = None
        else:
            self.isEncrypted = True
    def saveAsEncr(self, text:str):
        if  (self.loadedFileName):
            suggest = self.__getEncName(self.loadedFileName)
        else: suggest = "newFile.enc"
        fileName = filedialog.asksaveasfilename(initialfile=suggest)
        if (fileName):
            passwd = self.getPassword(reset=True)
            if (not(passwd)): return
            encryptedText = self.__encrypt(text, passwd)
            self.__safeSaveToDisc(encryptedText, fileName)
            self.setEncr(True)
    def autoSave(self, text:str) -> bool:
        if (not(self.loadedFileName)): return False
        if (self.isEncrypted):
            if (not(self.psswdHash)): return False
            passwd = self.getPassword()
            if (not(passwd)): return False
            fileText = self.__encrypt(text, passwd)
        else: 
            fileText = text
        tempPath = self.__tempPath(self.loadedFileName)
        with open(tempPath, "w", encoding="utf-8") as file:
                file.write(fileText)
                self.x = self.x + 1
                print(f"{self.x}Saved To Temp")
                return True
        return False


    def __encrypt(self, text:str, psswdHash:bytes)->str:
        return self.encryptor.encrypt(text, psswdHash)
    def getPassword(self, reset:bool = False) -> bytes | None:
        if (reset): self.psswdHash = None
        if self.psswdHash:
            return self.psswdHash
        pw = showPasswordDialog(self.context.app.root)
        if not pw:
            return None
        self.psswdHash = self.encryptor.derive_key(pw)  # bytes
        return self.psswdHash
    def open(self)->Optional[str|None]:
        if (not(self.loadedFileName)): defaultPath = os.getcwd()
        else: defaultPath: str = self.loadedFileName
        fileName: str = filedialog.askopenfilename(initialdir=defaultPath, defaultextension="txt", title="File input")
        
        if (fileName and os.path.exists(fileName)):
            text = self.__read(fileName)
            text = self.encryptor.decryptIfNeeded(text, self.getPassword)
            if (text != None):
                self.loadedFileName = fileName
                self.isEncrypted = self.encryptor.wasEncrypted
            else:
                messagebox.showerror("Ошибка", "Пароль не верен", parent = self.context.app.root)
            return text
        return None
    def __read(self, fileName:str)->str:
        with open(fileName, "r", encoding="utf-8") as file:
            loadedData = file.read()
            return loadedData

    def __safeSaveToDisc(self, text: str, path:str):
        tempPath = self.__tempPath(path)
        if (tempPath):
            with open(tempPath, "w", encoding="utf-8") as file:
                file.write(text)
                self.loadedFileName = path
                print("Saved To Temp")
        os.replace(tempPath, path)
        print("Saved To Disc")
    

    def __tempPath(self, path:str)->str:
        baseName = os.path.basename(path)
        dir = os.path.dirname(path)
        return dir+ R"/" + tempName +baseName 
    def __getEncName(self, name:str):
        if (name.endswith(".enc")):
            return name
        return name + ".enc"
    def __removeEncName(self, name:str):
        if (name.endswith(".enc")):
            return name.removesuffix(".enc")
        return name
