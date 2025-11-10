from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from UI import UI
from Editor import Editor
from Encryptor import Encryptor
from FileManager import FileManager
from typing import Optional

class Context:
    app: App  
    root: tk.Tk
    ui: UI
    editor: Editor
    encryptor: Encryptor
    fileManager: FileManager


class App:
    def __init__(self):

        self.context = Context()

        self.root: tk.Tk = tk.Tk()
        self.editor: Editor = Editor(self.root)
        self.encryptor :Encryptor = Encryptor()
        self.fileManager: FileManager = FileManager(self.context)

        self.context.app = self
        self.context.root = self.root
        self.context.editor = self.editor
        self.context.encryptor = self.encryptor
        self.context.fileManager = self.fileManager

        self.ui: UI = UI(self.context)
        self.context.ui = self.ui
        
        self.autoSaveTimeSeconds = 5
        self.autoSave()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.ui.initWindow()

        self.__bindKeys()
    def __bindKeys(self):
        self.root.bind("<Control-k>", self.open)     
        self.root.bind("<Control-s>", self.saveFile) 
        self.root.bind("<Control-a>", self.saveAs)    
        self.root.bind("<Control-e>", self.saveAsEncrypted)   

        
    def run(self):
        self.root.mainloop()

    def saveFile(self, event:Optional[tk.Event] = None):
        self.save()

    def close(self):
        if (self.editor.getModified()):
            self.askSaveDialog()
        self.fileManager.saveTemp()
        self.root.destroy()

    def open(self, event:Optional[tk.Event] = None):
        if (self.editor.getModified()): 
            self.askSaveDialog()
        self.fileManager.open()

    def autoSave(self):
        if (self.editor.getModified()):
            self.fileManager.autoSave(self.editor.getText())
        self.root.after(int(self.autoSaveTimeSeconds*1000), self.autoSave)

    def save(self, event:Optional[tk.Event] = None):
        text:str = self.editor.getText()
        self.fileManager.save(text)

    def saveAs(self, event:Optional[tk.Event] = None):
        text:str = self.editor.getText()
        self.fileManager.saveAs(text)

    def saveAsEncrypted(self, event:Optional[tk.Event] = None):
        text:str = self.editor.getText()
        self.fileManager.saveAsEncrypted(text)

    def askSaveDialog(self):
        answer = messagebox.askyesno("Save File", "Save File?")
        if (answer):
            text:str = self.editor.getText()
            saved = self.fileManager.save(text)
            if (not(saved)): self.askSaveDialog()
            self.editor.onFileSave()
