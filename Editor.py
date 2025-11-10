import tkinter as tk


class Editor:
    def __init__(self, root : tk.Tk):
        #root
        self.__root = root
        #field
        self.__modified = False
        #initialization
        self.__text = tk.Text(self.__root, wrap="word", undo=True)
        self.setText("")
        self.__text.pack(expand=True, fill = "both", pady = (20,0), padx = 20)
        self.__text.bind("<<Modified>>", self.__onModified)
        self.__text.bind("<Control-y>", self.redo)
        
    def undo(self,event=None):
        try:
            self.__text.edit_undo()
        except tk.TclError:
            pass

    def redo(self,event=None):
        try:
            self.__text.edit_redo()
        except tk.TclError:
            pass    
        
    def setText(self, text: str):
        self.__text.edit_modified(False)
        self.__text.delete("1.0", tk.END)
        self.__text.insert(tk.END, text)
        self.__root.after_idle(func = self.__notModified)
    def onFileOpen(self, text:str, filename:str):
        self.setText(text)

    def __notModified(self):
        self.__modified = False

    def __onModified(self, event: tk.Event):
        if self.__text.edit_modified():
            self.__modified = True
            self.__text.edit_modified(False)
    def getModified(self):
        return self.__modified
    def getText(self) -> str: 
        return self.__text.get(1.0, tk.END)
    
    def onFileSave(self):
        self.__modified = False