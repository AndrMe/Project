from __future__ import annotations
import tkinter as tk
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app import Context 

def getFont():
    return "Arial"
DefaultTitle:str = "MyEditor"

##TODO: add keybinds
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
        self.__menuBar.add_command(label="Settings", command=lambda: {print("OSettingspen")})
        self.root.config(menu=self.__menuBar)
        
    def __FileMenu(self) -> tk.Menu:
        self.fileMenu = tk.Menu(self.__menuBar, tearoff=0, font=(getFont(), 10))
        fileManager = self.context.app.fileManager
        self.fileMenu.add_command(label="Open", command = fileManager.open, accelerator="Ctrl+I")
        self.fileMenu.add_command(label="Save(with current mode)", command = fileManager.save, accelerator="Ctrl+S")
        self.fileMenu.add_command(label="SaveAs", command = fileManager.saveAs, accelerator = "Ctrl+A")
        self.fileMenu.add_command(label="SaveAsEncrypted", command = fileManager.saveAsEncrypted, accelerator = "Ctrl+E")
        return self.fileMenu
    
    def __EditMenu(self) -> tk.Menu:
        editMenu = tk.Menu(self.__menuBar, tearoff=0, font=(getFont(), 10))
        editMenu.add_command(label="Find", command=lambda: {})
        editMenu.add_command(label="Undo", command=self.context.editor.undo, accelerator= "Ctrl+Z")
        editMenu.add_command(label="Redo", command=self.context.editor.redo, accelerator= "Ctrl+Y")
        return editMenu
    def __ViewMenu(self) -> tk.Menu:
        fileMenu = tk.Menu(self.__menuBar, tearoff=0,font=(getFont(), 10))
        fileMenu.add_command(label="Font", command=lambda: {print("Font")})
        fileMenu.add_command(label="FontSize", command=lambda: {print("FontSize")})
        fileMenu.add_command(label="indent", command=lambda: {print("indent")})
        return fileMenu
    
    def __addMenu(self, name : str,  menu : tk.Menu):
        self.__menuBar.add_cascade(label = name, menu = menu)
        
    def onOpen(self, text:str, filename:str):
        self.fileDisplayName = filename
        self.__updateName(filename)

    def __updateName(self, fileName:str):
        if (fileName):
            self.root.title(fileName + self.titleMessageAdd)
        else: 
            self.root.title(DefaultTitle)
    def onIsEncrypted(self, isEncr: bool):
        text = "Encrypted" if isEncr else "Not Encrypted"
        self.__status_label.config(text=text)
        self.titleMessageAdd = f" - {DefaultTitle}[{text}]"
        self.__updateName(self.fileDisplayName)