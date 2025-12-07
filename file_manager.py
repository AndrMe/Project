from __future__ import annotations
from tkinter import filedialog, messagebox
from typing import Optional
import threading

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
        self.loadedFileName:Optional[str] = None
        self.isEncrypted = False


        self.psswdHash: bytes | None = None

    def removeTemp(self):
        if (not(self.loadedFileName)): return
        name:str = self.__tempPath(self.loadedFileName)
        if (not(os.path.exists(name))): return
        os.remove(name)

        
    def save(self, text:str)->bool:
        fileName = self.loadedFileName
        newText = text
        if (not(fileName)):
            fileName = filedialog.asksaveasfilename(initialfile="newFile.txt")
        if (fileName):
            self.loadedFileName = fileName
            if (self.isEncrypted):
                    newText = self.__encrypt(text)
                    if (newText == None) : return False
            else:
                self.encryptor.reset()
            self.__safeSaveToDisc(newText, fileName)
            return True
        return False

    def saveAs(self, text:str):
        if  (self.loadedFileName):
            suggest = self.__removeEncName(self.loadedFileName)
        else: suggest = "newFile.txt"
        
        fileName = filedialog.asksaveasfilename(initialfile=suggest)
        if (fileName):
            self.removeTemp()
            self.loadedFileName = fileName
            self.__safeSaveToDisc(text, fileName)
            self.setEncr(False)
            return True
        return False
            
    def setEncr(self, encr:bool):
        if (not(encr)):
            self.isEncrypted = False
            self.encryptor.reset()
        else:
            self.isEncrypted = True
    def saveAsEncr(self, text:str):
        if  (self.loadedFileName):
            suggest = self.__getEncName(self.loadedFileName)
        else: suggest = "newFile.enc"
        fileName = filedialog.asksaveasfilename(initialfile=suggest)
        if (fileName):
            self.removeTemp()
            self.loadedFileName = fileName
            self.encryptor.reset()
            encryptedText = self.__encrypt(text)
            if (encryptedText == None) : return False
            self.__safeSaveToDisc(encryptedText, fileName)
            self.setEncr(True)
            return True
        return False
    def autoSave(self, text:str) -> bool:
        if (not(self.loadedFileName)): return False
        if (self.isEncrypted):
            fileText = self.__encrypt(text)
            if (fileText == None) : return False
        else: 
            self.encryptor.reset()
            fileText = text
        tempPath = self.__tempPath(self.loadedFileName)
        with open(tempPath, "w", encoding="utf-8") as file:
                file.write(fileText)
                return True
        return False


    def __encrypt(self, text:str)->str|None:
        try:
            newText = self.encryptor.encrypt(text)
        except(e:Exception):
            newText = None
            messagebox.showerror("Ошибка", f"{e}", parent = self.context.app.root)
        return newText
    def open(self)->Optional[str]:
        if (not(self.loadedFileName)): defaultPath = os.getcwd()
        else: defaultPath: str = os.path.dirname(self.loadedFileName) or os.getcwd()
        fileName: str = filedialog.askopenfilename(initialdir=defaultPath, defaultextension="txt", title="File input")
        
        if (fileName and os.path.exists(fileName)):
            text = self.__checkTempOnOpen(fileName)
            if (text is None):
                text = self.__read(fileName)
            text = self.encryptor.decryptIfNeeded(text)
            if (text != None):
                self.loadedFileName = fileName
                self.isEncrypted = self.encryptor.wasEncrypted
            else:
                messagebox.showerror("Ошибка", "Пароль не верен, либо файл был изменен", parent = self.context.app.root)
            return text
        return None
    def __checkTempOnOpen(self, filename: str) -> Optional[str]:
        """Проверяем, есть ли автосохранение для данного файла."""
        temp_path = self.__tempPath(filename)
        if os.path.exists(temp_path):
            answer = messagebox.askyesno(
                "Restore autosave",
                f"Autosaved version of '{filename}' found. Restore?"
            )
            if answer:
                return self.__read(temp_path)
            else:
                os.remove(temp_path)
        return None 
    def __read(self, fileName:str)->str:
        with open(fileName, "r", encoding="utf-8") as file:
            loadedData = file.read()
            return loadedData

    def __safeSaveToDisc(self, text: str, path:str):
        print("Started save")
        threading.Thread(target=self.__safeSaveToDiscThr, args=(text, path), daemon=True).start()
        
    
    def __safeSaveToDiscThr(self, text: str, path: str):
        try:
            tempPath = self.__tempPath(path)
            with open(tempPath, "w", encoding="utf-8") as file:
                file.write(text)
            os.replace(tempPath, path)
        except Exception as e:
            self.context.root.after(0, lambda: self.__onSaveError(e, path))

    def __onSaveError(self, error: Exception, path: str):
        messagebox.showerror("Save Error", f"Failed to save to {path}:\n{error}")

    def __tempPath(self, path:str)->str:
        baseName = os.path.basename(path)
        dirName = os.path.dirname(path)
        return os.path.join(dirName, tempName + baseName)
    def __getEncName(self, name:str):
        if (name.endswith(".enc")):
            return name
        return name + ".enc"
    def __removeEncName(self, name:str):
        if (name.endswith(".enc")):
            return name.removesuffix(".enc")
        return name
