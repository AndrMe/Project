import tkinter as tk

def getFont():
    return "Arial"

DefaultTitle:str = "MyEditor"

##TODO: add keybinds
class UI:
    def __init__(self, root : tk.Tk, openCB, saveCB, saveAsCB, saveAsEncrCB, findCB, undoCB, redoCB):
        self.root: tk.Tk = root
        self.app = 123
        self.openCB = openCB
        self.saveCB = saveCB
        self.saveAsCB = saveAsCB
        self.saveAsEncrCB = saveAsEncrCB
        self.findCB = findCB
        self.undoCB = undoCB
        self.redoCB = redoCB
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
        self.menuBar = tk.Menu(self.root)  
        self.__addMenu("File", self.__FileMenu())
        self.__addMenu("Edit",self.__EditMenu())
        self.__addMenu("View",self.__ViewMenu())
        self.menuBar.add_command(label="Settings", command=lambda: {print("OSettingspen")})
        self.root.config(menu=self.menuBar)
        

    def __FileMenu(self) -> tk.Menu:
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0, font=(getFont(), 10))
        self.fileMenu.add_command(label="Open", command=self.openCB, accelerator="Ctrl+K")
        self.fileMenu.add_command(label="Save(with current mode)", command = self.saveCB, accelerator="Ctrl+S")
        self.fileMenu.add_command(label="SaveAs", command = self.saveAsCB, accelerator = "Ctrl+A")
        self.fileMenu.add_command(label="SaveAsEncrypted", command=self.saveAsEncrCB, accelerator = "Ctrl+E")
        return self.fileMenu
    
    def __EditMenu(self) -> tk.Menu:
        editMenu = tk.Menu(self.menuBar, tearoff=0, font=(getFont(), 10))
        editMenu.add_command(label="Find", command=self.findCB)
        editMenu.add_command(label="Undo", command=self.undoCB, accelerator= "Ctrl+Z")
        editMenu.add_command(label="Undo", command=self.redoCB, accelerator= "Ctrl+Y")
        return editMenu
    def __ViewMenu(self) -> tk.Menu:
        fileMenu = tk.Menu(self.menuBar, tearoff=0,font=(getFont(), 10))
        fileMenu.add_command(label="Font", command=lambda: {print("Font")})
        fileMenu.add_command(label="FontSize", command=lambda: {print("FontSize")})
        fileMenu.add_command(label="indent", command=lambda: {print("indent")})
        return fileMenu
    
    def __addMenu(self, name : str,  menu : tk.Menu):
        self.menuBar.add_cascade(label = name, menu = menu)
        
    def onOpen(self, text:str, filename:str):
        self.fileDisplayName = filename
        self.updateName(filename)

    def updateName(self, fileName:str):
        if (fileName):
            self.root.title(fileName + self.titleMessageAdd)
        else: 
            self.root.title(DefaultTitle)
    def onIsEncrypted(self, isEncr: bool):
        text = "Encrypted" if isEncr else "Not Encrypted"
        self.__status_label.config(text=text)
        self.titleMessageAdd = f" - {DefaultTitle}[{text}]"
        self.updateName(self.fileDisplayName)