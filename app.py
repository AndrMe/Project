from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from UI import UI
from Editor import Editor
from Encryptor import Encryptor
from FileManager import FileManager


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
        self.root.bind("<Control-i>", self.fileManager.open)     
        self.root.bind("<Control-s>", self.fileManager.save) 
        self.root.bind("<Control-a>", self.fileManager.saveAs)    
        self.root.bind("<Control-e>", self.fileManager.saveAsEncrypted)   
        
    def run(self):
        self.root.mainloop()

    def close(self):
        if (self.editor.getModified()):
            self.askSaveDialog()
        self.fileManager.saveTemp()
        self.root.destroy()

    def autoSave(self):
        if (self.editor.getModified()):
            self.fileManager.autoSave(self.editor.getText())
        self.root.after(int(self.autoSaveTimeSeconds*1000), self.autoSave)

    def askSaveDialog(self):
        answer = messagebox.askyesno("Save File", "Save File?")
        if (answer):
            saved = self.fileManager.save()
            if (not(saved)): self.askSaveDialog()
            self.editor.onFileSave()
            return True
        return False
