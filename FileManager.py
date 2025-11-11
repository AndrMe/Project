from __future__ import annotations
import tkinter as tk
from tkinter import filedialog
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
        #fields
        self.loadedFileName:Optional[str|None] = None
        self.isEncrypted = False

        self.psswdHash: str | None = None


    def save(self, text:str)->bool:
        fileName = self.loadedFileName
        if (not(fileName)):
            fileName = filedialog.asksaveasfilename(initialfile=self.loadedFileName)
        if (fileName):
            if (self.isEncrypted):
                passwd = self.getPassword()
                if (not(passwd)): return False
                text = self.__encrypt(text, passwd)
            self.__safeSaveToDisc(text, fileName)
            return True

    def saveAs(self, text:str):
        suggest = self.__removeEncName(self.loadedFileName)
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
        suggest = self.__getEncName(self.loadedFileName)
        fileName = filedialog.asksaveasfilename(initialfile=suggest)
        if (fileName):
            passwd = showPasswordDialog(self.context.app.root)
            if (not(passwd)): return
            encryptedText = self.__encrypt(text, passwd)
            self.__safeSaveToDisc(encryptedText, fileName)
            self.setEncr(True)
    def autoSave(self, text:str) -> None:
        if (not(self.loadedFileName)): return None
        if (self.isEncrypted):
            if (not(self.psswdHash)): return None
            passwd = self.getPassword()
            if (not(passwd)): return None
            fileText = self.__encrypt(text, passwd)
        else: 
            fileText = text
        tempPath = self.__tempPath(self.loadedFileName)
        with open(tempPath, "w") as file:
                file.write(fileText)
                print("Saved To Temp")


    def __encrypt(self, text:str, psswdHash:str)->str:
        return self.encryptor.encrypt(text, psswdHash)
    def getPassword(self) -> str | None:
        if self.psswdHash:
            return self.psswdHash
        pw = showPasswordDialog(self.context.app.root)
        if pw:
            self.psswdHash = pw
        return pw
    def open(self)->Optional[str|None]:
        if (not(self.loadedFileName)): defaultPath = os.getcwd()
        else: defaultPath: str = self.loadedFileName
        fileName: str = filedialog.askopenfilename(initialdir=defaultPath, defaultextension="txt", title="File input")
        
        if (fileName and os.path.exists(fileName)):
            text = self.__read(fileName)
            return text
        return None
    def __read(self, fileName:str)->str:
        with open(fileName, "r") as file:
            loadedData = file.read()
            self.loadedFileName = fileName
            return loadedData

    def __safeSaveToDisc(self, text: str, path:str):
        tempPath = self.__tempPath(path)
        if (tempPath):
            with open(tempPath, "w") as file:
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
        return name + ".enc"
    def __removeEncName(self, name:str):
        if (name.endswith(".enc")):
            return name.removesuffix(".enc")
        return name
