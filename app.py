import tkinter as tk
from UI import UI
from Editor import Editor
from Encryptor import Encryptor
from FileManager import FileManager
class App:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.ui: UI = UI(self.root)
        self.editor: Editor = Editor(self.root)
        self.encryptor :Encryptor = Encryptor()
        self.fileManager: FileManager = FileManager()
    def run(self):
        self.root.mainloop()