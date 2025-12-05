from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from ui import UI
from editor import Editor
from encryptor import Encryptor
from file_manager import FileManager
from typing import Optional
import config
import time
from  psswd import *

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
        encrypt, autoSave, asInterval = config.loadSettings()
        self.isAutoSave = autoSave
        self.isAutoSaved = False
        self.autoSaveTimeSeconds = asInterval
        
        self.encryptor :Encryptor = Encryptor(self.getPsswd)
        self.context.encryptor = self.encryptor
        self.fileManager: FileManager = FileManager(self.context)

        self.context.app = self
        self.context.root = self.root  
        self.context.fileManager = self.fileManager

        self.ui: UI = UI(self.context)
        self.editor: Editor = Editor(self.root, self.ui)
        self.context.editor = self.editor
        self.context.ui = self.ui
        self.ui.initWindow()
        self.editor.initTheme()
        
        self.fileManager.setEncr(encrypt)
        self.ui.onIsEncrypted(self.fileManager.isEncrypted)

        self.lastSaveTime = time.perf_counter()
        
        self.autoSave()
        self.__bindKeys()
        
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def getPsswd(self):
        return showPasswordDialog(self.root)
    def __bindKeys(self):
        self.root.bind("<Control-i>", self.open)     
        self.root.bind("<Control-s>", self.save) 
        self.root.bind("<Control-Shift-S>", self.saveAs)    
        self.root.bind("<Control-e>", self.saveAsEncrypted)   
    def __notifySaved(self):
        self.editor.modified = False
        self.isAutoSaved = False
        self.ui.onOpen(self.fileManager.loadedFileName)
        self.ui.onIsEncrypted(self.fileManager.isEncrypted)
    def save(self, event:Optional[tk.Event] = None):
        text = self.editor.getText()
        saved = self.fileManager.save(text)
        if (saved): self.__notifySaved()
    def saveAs(self, event:Optional[tk.Event] = None):
        text = self.editor.getText()
        saved = self.fileManager.saveAs(text)
        if (saved): self.__notifySaved()
    def saveAsEncrypted(self, event:Optional[tk.Event] = None):
        text = self.editor.getText()
        saved = self.fileManager.saveAsEncr(text)
        if (saved): self.__notifySaved()
    def open(self, event:Optional[tk.Event] = None):
        if (self.editor.modified or (self.isAutoSaved == True)):
            self.askSaveDialog()
        text = self.fileManager.open()
        if (text != None):
            self.editor.setText(text)
            self.__notifySaved()
    def save_settings(self):

        self.context.app.isAutoSave = self.ui.autosave_enabled.get()
        self.context.app.autoSaveTimeSeconds = self.ui.autoSaveIntervalText.get()
        self.context.fileManager.setEncr(self.ui.encrypt_enabled.get())
        self.ui.onIsEncrypted(self.fileManager.isEncrypted)
        config.saveSettings(self.context.fileManager.isEncrypted,
                        self.isAutoSave,
                        self.autoSaveTimeSeconds)
        self.ui.settings_win.destroy()

    def run(self):
        self.root.mainloop()

    def close(self):
        if (self.editor.modified or self.isAutoSaved):
            self.askSaveDialog()            
        config.saveSettings(self.context.fileManager.isEncrypted,
                       self.isAutoSave,
                        self.autoSaveTimeSeconds)
        self.root.destroy()

    def autoSave(self):
        now = time.perf_counter()
        elapsed = now - self.lastSaveTime
        if (elapsed >= self.autoSaveTimeSeconds
            and self.editor.modified and (self.isAutoSave)
            and self.fileManager.loadedFileName):
            success = self.fileManager.autoSave(self.editor.getText())
            if (success):
                self.editor.modified = False
                self.__notifySaved()
                self.isAutoSaved = True
                self.lastSaveTime = now
        self.root.after(16, self.autoSave)

    def askSaveDialog(self):
        answer = messagebox.askyesno("Save File", "Save File?")
        if (answer):
            text = self.editor.getText()
            saved = self.fileManager.save(text)
            if (not(saved)): self.askSaveDialog()
            self.editor.modified = False
            return True
        self.fileManager.removeTemp()
        return False
