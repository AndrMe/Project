from __future__ import annotations
import tkinter as tk
from typing import TYPE_CHECKING
from typing import Optional
if TYPE_CHECKING:
    from app import Context 

def getFont():
    return "Arial"
DefaultTitle:str = "MyEditor"

class UI:
    def __init__(self, context: Context):
        self.root: tk.Tk = context.root
        self.context = context
       
        self.titleMessageAdd = DefaultTitle
        self.fileDisplayName = ""


    def initWindow(self):
        self.root.geometry("1100x800") 
        self.__initMenu()
        self.__initStatus()
        self.encrypt_enabled = tk.BooleanVar(value=False)
        self.autosave_enabled = tk.BooleanVar(value=self.context.app.isAutoSave)
        self.autoSaveIntervalText = tk.DoubleVar(value=self.context.app.autoSaveTimeSeconds)  
        
    def __initStatus(self):
        self.__status_frame = tk.Frame(self.root)
        self.__status_frame.pack(side="bottom", fill="x")
        self.__status_label = tk.Label(self.__status_frame, text="Not Encrypted")
        self.__status_label.pack(side="right", padx=40, pady=20)

    def __initMenu(self):
        self.__menuBar = tk.Menu(self.root)  
        self.__addMenu("File", self.__FileMenu())
        self.__addMenu("Edit",self.__EditMenu())
        self.__addMenu("View",self.__ViewMenu())
        self.__menuBar.add_command(label="Settings", command=self.showSettingsWindow)
        self.root.config(menu=self.__menuBar)
        
    def __FileMenu(self) -> tk.Menu:
        self.fileMenu = tk.Menu(self.__menuBar, tearoff=0, font=(getFont(), 10))
        app = self.context.app
        self.fileMenu.add_command(label="Open", command = app.open, accelerator="Ctrl+I")
        self.fileMenu.add_command(label="Save(with current mode)", command = app.save, accelerator="Ctrl+S")
        self.fileMenu.add_command(label="SaveAs", command = app.saveAs, accelerator = "Ctrl+A")
        self.fileMenu.add_command(label="SaveAsEncrypted", command = app.saveAsEncrypted, accelerator = "Ctrl+E")
        return self.fileMenu
    
    def __EditMenu(self) -> tk.Menu:
        editMenu = tk.Menu(self.__menuBar, tearoff=0, font=(getFont(), 10))
        editMenu.add_command(label="Find", command=self.context.editor.openFindDialog, accelerator="Ctrl+F")
        editMenu.add_command(label="Undo", command=self.context.editor.undo, accelerator= "Ctrl+Z")
        editMenu.add_command(label="Redo", command=self.context.editor.redo, accelerator= "Ctrl+Y")
        return editMenu
    def __ViewMenu(self) -> tk.Menu:
        fileMenu = tk.Menu(self.__menuBar, tearoff=0,font=(getFont(), 10))
        fileMenu.add_command(label="Toggle Theme", command=self.context.editor.toggleTheme)
        fileMenu.add_command(label="Increase Font", command=lambda: self.context.editor.changeFontSize(2))
        fileMenu.add_command(label="Decrease Font", command=lambda: self.context.editor.changeFontSize(-2))
        return fileMenu
    
    def __addMenu(self, name : str,  menu : tk.Menu):
        self.__menuBar.add_cascade(label = name, menu = menu)
        
    def onOpen(self, filename:Optional[str|None]):
        self.fileDisplayName = filename
        self.__updateName(filename)

    def __updateName(self, fileName:Optional[str|None]):
        if (fileName):
            self.root.title(fileName + self.titleMessageAdd)
        else: 
            self.root.title(DefaultTitle)
    def setBackground(self, background: str):
        self.__status_frame.configure(bg=background)
        self.__status_label.configure(bg=background)
        
    def onIsEncrypted(self, isEncr: bool):
        text = "Encrypted" if isEncr else "Not Encrypted"
        self.isEncr = isEncr
        self.__status_label.config(text=text)
        self.titleMessageAdd = f" - {DefaultTitle}[{text}]"
        self.__updateName(self.fileDisplayName)
        self.encrypt_enabled.set(isEncr)

    def showSettingsWindow(self):
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Settings")
        self.settings_win.geometry("400x300")
        self.settings_win.resizable(False, False)


        tk.Label(self.settings_win, text="Encryption:").pack(anchor="w", padx=10, pady=(10,0))
        self.encrypt_cb = tk.Checkbutton(self.settings_win, text="Enable Encryption", variable=self.encrypt_enabled)
        self.encrypt_cb.pack(anchor="w", padx=20)


        tk.Label(self.settings_win, text="Autosave:").pack(anchor="w", padx=10, pady=(10,0))
        self.autosave_cb = tk.Checkbutton(self.settings_win, text="Enable Autosave", variable=self.autosave_enabled)
        self.autosave_cb.pack(anchor="w", padx=20)


        tk.Label(self.settings_win, text="Autosave interval (sec):").pack(anchor="w", padx=10, pady=(10,0))
        
        self.autosave_entry = tk.Entry(self.settings_win, textvariable=self.autoSaveIntervalText, width=10)
        self.autosave_entry.pack(anchor="w", padx=20)
        tk.Button(self.settings_win, text="Save", command=self.context.app.save_settings).pack(pady=40)
