from __future__ import annotations
from tkinter import filedialog
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

    def __safeWrite(self, place:str, text:str):
        self.saveToTemp(text)
        os.replace(self.getTempPath(), place)

    def saveToPlace(self, place:str, text:str) -> bool:
        if (place):
            # with open(place, "w") as file:
                # file.write(text)
            self.__safeWrite(place, text)
            self.__removeTemp()
            self.loadedFileName = place
            self.fileLoaded = True
            self.fileUploaded = True
            return True
        return False

    def save(self, text:str) -> bool:
        fileName: str = self.loadedFileName
        if (self.isEncrypted):
            text = self.context.encryptor.encrypt(text)
        if (not(self.fileLoaded)):
            fileName = filedialog.asksaveasfilename(initialfile=self.loadedFileName)
        
        return self.saveToPlace(fileName, text)
    
    def saveAs(self, text:str) -> bool:
        fileName = filedialog.asksaveasfilename(initialfile=self.loadedFileName)
        if (self.saveToPlace(fileName, text)):
            self.isEncrypted = False
            return True
        return False
    
    def getEncName(self, name:str):
        return name + ".enc"
    
    def saveAsEncrypted(self, text:str) -> None:
        fileName = filedialog.asksaveasfilename(initialfile=self.getEncName(self.loadedFileName), 
                                                defaultextension=".enc",
                                                filetypes=[
                                                ("Encrypted files", "*.enc")])
        fileText = self.context.encryptor.encrypt(text)
        self.saveToPlace(fileName, fileText)
        self.isEncrypted = True
        self.__notifyEncryptionMode()
 
    def getTempPath(self):
        baseName = os.path.basename(self.loadedFileName)
        dir = os.path.dirname(self.loadedFileName)
        return dir+ R"/" + tempName +baseName 
    
    def autoSave(self, text:str) -> None:
        if (not(self.fileLoaded)): return
        if (self.isEncrypted):
            fileText = self.context.encryptor.encrypt(text)
        else: 
            fileText = text
        self.saveToTemp(fileText)
        
    def saveToTemp(self, fileText:str):
        resName = self.getTempPath()
        if (resName):
            with open(resName, "w") as file:
                file.write(fileText)
                self.fileLoaded = True
                self.fileUploaded = False
                self.__onSave()
                self.__notifyEncryptionMode()
    def saveTemp(self):
        tempPath = self.getTempPath()
        if (os.path.exists(tempPath)):
            tempData:str
            with open(tempPath, "r") as file:
                tempData = file.read()
                print("save temp")
            self.saveToPlace(self.loadedFileName, tempData)
        

    def open(self) -> str:
        defaultPath: str = self.loadedFileName
        if (not(self.fileLoaded)): defaultPath = os.getcwd()
        fileName: str = filedialog.askopenfilename(initialdir=defaultPath, defaultextension="txt", title="File input")
        if (fileName):
            with open(fileName, "r") as file:
                loadedData = file.read()
                self.loadedFileName = fileName
                self.fileLoaded = True
                self.__onOpen(loadedData)
                self.__notifyEncryptionMode()
                return loadedData
        return ""
    
    def __removeTemp(self):
        if (os.path.exists(self.getTempPath())):
            os.remove(self.getTempPath())

    def __onSave(self):
        self.context.editor.onFileSave()

    def __onOpen(self, text:str):
        self.context.editor.onFileOpen(text, self.loadedFileName)

    def __notifyEncryptionMode(self):
        self.context.ui.onIsEncrypted(self.isEncrypted)