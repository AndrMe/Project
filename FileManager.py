from tkinter import filedialog
from Encryptor import Encryptor
from enum import Enum
import os

class CallbackType(Enum):
    Save = 1
    Open = 2
    ISEncrypted = 3

class CallBack:
    def __init__(self, type:CallbackType, call) -> None:
        self.type = type
        self.call = call

tempName = "~temp."

class FileManager:
    def __init__(self, encryptor: Encryptor) -> None:
        self.encryptor = encryptor
        self.__onCallback: list[CallBack] = []
        #fields
        self.loadedFileName:str = ""
        self.fileLoaded: bool = False
        self.fileUploaded:bool = False
        self.isEncrypted = False

    def registerCall(self, callBack: CallBack):
        self.__onCallback.append(callBack)

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
            text = self.encryptor.encrypt(text)
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
        fileText = self.encryptor.encrypt(text)
        self.saveToPlace(fileName, fileText)
        self.isEncrypted = True
 
    def getTempPath(self):
        baseName = os.path.basename(self.loadedFileName)
        dir = os.path.dirname(self.loadedFileName)
        return dir+ R"/" + tempName +baseName 
    def autoSave(self, text:str) -> None:
        if (not(self.fileLoaded)): return
        if (self.isEncrypted):
            fileText = self.encryptor.encrypt(text)
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
                self.__notifySave()
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
        fileName: str = filedialog.askopenfilename(defaultextension="txt", initialdir = "/", title="File input")
        if (fileName):
            with open(fileName, "r") as file:
                loadedData = file.read()
                self.loadedFileName = fileName
                self.fileLoaded = True
                self.__notifyOpen(loadedData)
                self.__notifyEncryptionMode()
                return loadedData
        return ""
    def __removeTemp(self):
        if (os.path.exists(self.getTempPath())):
            os.remove(self.getTempPath())
    def __notifySave(self):
        print(f"Saved")
        for call in self.__onCallback:
            if (call.type == CallbackType.Save):
                call.call()
    def __notifyOpen(self, text:str):
        print(f"Opened")
        for call in self.__onCallback:
            if (call.type == CallbackType.Open):
                call.call(text, self.loadedFileName)
    def __notifyEncryptionMode(self):
        for call in self.__onCallback:
            if (call.type == CallbackType.ISEncrypted):
                call.call(self.isEncrypted)