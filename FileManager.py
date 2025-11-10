from __future__ import annotations
import tkinter as tk
from tkinter import filedialog
from typing import Optional
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import Context 

tempName = "~$temp."

class FileManager:
    def __init__(self, context: Context) -> None:
        self.context = context
        #fields
        self.loadedFileName:str = ""
        self.fileLoaded: bool = False
        self.fileUploaded:bool = False
        self.isEncrypted = False


    def save(self, event:Optional[tk.Event] = None):
        text:str = self.context.editor.getText()
        fileName: str = self.loadedFileName
        if (self.isEncrypted):
            text = self.context.encryptor.encrypt(text)
        if (not(self.fileLoaded)):
            fileName = filedialog.asksaveasfilename(initialfile=self.loadedFileName)
        if (fileName):
            self.__saveToFilePath(fileName, text) 
            return True
        else: 
            return False
    
    def saveAs(self, event:Optional[tk.Event] = None):
        text:str = self.context.editor.getText()
        fileName = filedialog.asksaveasfilename(initialfile=self.loadedFileName)
        if (fileName):
            self.__saveToFilePath(fileName, text)
            self.isEncrypted = False
            return True
        return False
    
    def __getEncName(self, name:str):
        return name + ".enc"
    
    def saveAsEncrypted(self, event:Optional[tk.Event] = None) -> None:
        text:str = self.context.editor.getText()
        fileName = filedialog.asksaveasfilename(initialfile=self.__getEncName(self.loadedFileName), 
                                                defaultextension=".enc",
                                                filetypes=[
                                                ("Encrypted files", "*.enc")])
        fileText = self.context.encryptor.encrypt(text)
        self.__saveToFilePath(fileName, fileText)
        self.isEncrypted = True
        self.__notifyEncryptionMode()
     
    def autoSave(self, text:str) -> None:
        if (not(self.fileLoaded)): return
        if (self.isEncrypted):
            fileText = self.context.encryptor.encrypt(text)
        else: 
            fileText = text
        self.__saveToTemp(fileText)
    def saveTemp(self):
        tempPath = self.__getTempPath()
        if (os.path.exists(tempPath)):
            tempData:str
            with open(tempPath, "r") as file:
                tempData = file.read()
                print("saved temp file")
            self.__saveToFilePath(self.loadedFileName, tempData)
        

    def open(self, event:Optional[tk.Event] = None) -> str:
        if (self.context.editor.getModified() or not(self.fileUploaded)): 
            self.context.app.askSaveDialog()
        self.__removeTemp()
        defaultPath: str = self.loadedFileName
        if (not(self.fileLoaded)): defaultPath = os.getcwd()
        fileName: str = filedialog.askopenfilename(initialdir=defaultPath, defaultextension="txt", title="File input")
        if (fileName):
            with open(fileName, "r") as file:
                loadedData = file.read()
                self.loadedFileName = fileName
                self.fileLoaded = True
                self.fileUploaded = True
                self.__onOpen(loadedData)
                self.__notifyEncryptionMode()
                return loadedData
        return ""
    
    def __getTempPath(self):
        baseName = os.path.basename(self.loadedFileName)
        dir = os.path.dirname(self.loadedFileName)
        return dir+ R"/" + tempName +baseName 

        
    def __saveToTemp(self, fileText:str):
        resName = self.__getTempPath()
        if (resName):
            with open(resName, "w") as file:
                file.write(fileText)
                self.fileLoaded = True
                self.fileUploaded = False
                self.__onTempSave()
                self.__notifyEncryptionMode()
                print("Saved To Temp")
    
    def __safeWrite(self, path:str, data:str):
        self.__saveToTemp(data)
        os.replace(self.__getTempPath(), path)
        print("Saved To Disc")

    def __saveToFilePath(self, path:str, data:str):
        self.__safeWrite(path, data)
        self.__removeTemp()
        self.loadedFileName = path
        self.fileUploaded = True
       
    
    def __removeTemp(self):
        if (os.path.exists(self.__getTempPath())):
            os.remove(self.__getTempPath())

    def __onTempSave(self):
        self.context.editor.onFileSave()

    def __onOpen(self, text:str):
        self.context.editor.onFileOpen(text, self.loadedFileName)
        self.context.ui.onOpen(text, self.loadedFileName)

    def __notifyEncryptionMode(self):
        self.context.ui.onIsEncrypted(self.isEncrypted)