import tkinter as tk
from tkinter import messagebox
from UI import UI
from Editor import Editor
from Encryptor import Encryptor
from FileManager import FileManager
from FileManager import CallBack, CallbackType


class App:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.ui: UI = UI(self.root, self.open, self.save, self.saveAs, self.saveAsEncrypted)
        self.editor: Editor = Editor(self.root)
        self.encryptor :Encryptor = Encryptor()
        self.fileManager: FileManager = FileManager(self.encryptor)

        self.autoSaveTimeSeconds = 5
        self.autoSave()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.ui.initWindow()
        self.fileManager.registerCall(CallBack(CallbackType.Save, self.editor.onFileSave))
        self.fileManager.registerCall(CallBack(CallbackType.Open,self.editor.onFileOpen))
        self.fileManager.registerCall(CallBack(CallbackType.ISEncrypted, self.ui.onIsEncrypted))
    def run(self):
        self.root.mainloop()

    def close(self):
        if (self.editor.getModified()):
            self.askSaveDialog()
        self.fileManager.saveTemp()
        self.root.destroy()
    def open(self):
        if (self.editor.getModified()): 
            self.askSaveDialog()
        self.fileManager.open()

    def autoSave(self):
        if (self.editor.getModified()):
            self.fileManager.autoSave(self.editor.getText())
        self.root.after(int(self.autoSaveTimeSeconds*1000), self.autoSave)
    def save(self):
        text:str = self.editor.getText()
        self.fileManager.save(text)

    def saveAs(self):
        text:str = self.editor.getText()
        self.fileManager.saveAs(text)

    def saveAsEncrypted(self):
        text:str = self.editor.getText()
        self.fileManager.saveAsEncrypted(text)

    def askSaveDialog(self):
        answer = messagebox.askyesno("Save File", "Save File?")
        if (answer):
            text:str = self.editor.getText()
            saved = self.fileManager.save(text)
            if (not(saved)): self.askSaveDialog()
            self.editor.onFileSave()
