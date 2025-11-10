import tkinter as tk
from typing import Optional
from tkinter import font
import re

from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    background: str
    foreground: str
    cursor: str
    select_bg: str
    line_highlight: str
    line_number_bg: str
    line_number_fg: str
    number_color: str



DARK_THEME = Theme(
    name="Dark",
    background="#1e1e1e",
    foreground="#dcdcdc",
    cursor="#ffffff",
    select_bg="#264f78",
    line_highlight="#2a2a2a",
    line_number_bg="#252526",
    line_number_fg="#858585",
    number_color="#569CD6",

)

LIGHT_THEME = Theme(
    name="Light",
    background="#ffffff",
    foreground="#000000",
    cursor="#000000",
    select_bg="#cce8ff",
    line_highlight="#f0f0f0",
    line_number_bg="#f3f3f3",
    line_number_fg="#555555",
    number_color="#0066cc",

)

class Editor:
    def __init__(self, root : tk.Tk,ui,  theme: Theme = LIGHT_THEME):
        #root
        self.__root = root
        self.ui = ui
        #field
        self.__modified = False
        #initialization
        self.__theme = theme
        self.__font = font.Font(family="Consolas", size=12)

        self.__frame = tk.Frame(self.__root)
        self.__frame.pack(expand=True, fill="both", pady=(20,0), padx=20)
        self.__scrollbar = tk.Scrollbar(self.__frame)
        self.__scrollbar.pack(side="right", fill="y")

        self.__text = tk.Text(
            self.__frame,
            wrap="word",
            undo=True,
            font=self.__font,
            yscrollcommand=self.__scrollbar.set  # связываем с scrollbar
        )
        self.__text.pack(expand=True, fill="both")
        self.__scrollbar.config(command=self.__text.yview)  # двусторонняя связь
        
        self.__text.bind("<<Modified>>", self.__onModified)
        self.__text.bind("<Control-y>", self.redo)
        self.__text.bind("<Tab>", self.__onTab)
        self.__text.bind("<Shift-Tab>", self.__onShiftTab)  
        self.__text.bind("<KeyRelease>", self.__onKeyRelease)   
        self.__text.bind("<Button-1>", self.__onCursorMove)
        self.__text.bind("<Motion>", self.__onCursorMove)
        self.__text.bind("<Control-MouseWheel>", self.__onCtrlMouseWheel)

        self.setText("")

    def initTheme(self):
        self.applyTheme(self.__theme)
    def __onCtrlMouseWheel(self, event: tk.Event):
        """Изменяет размер шрифта при Ctrl + прокрутка"""
        delta = 0
        if hasattr(event, "delta"):
            delta = 1 if event.delta > 0 else -1
        else:
            # Linux: Button-4 = scroll up, Button-5 = scroll down
            if event.num == 4:
                delta = 1
            elif event.num == 5:
                delta = -1

        self.changeFontSize(delta)
        return "break"  # предотвращает прокрутку текста

    def __onCursorMove(self, event=None):
        self.highlightCurrentLine()    
    def applyTheme(self, theme: Theme):
        self.__theme = theme
        t = theme
        self.__root.configure(bg=t.background)
        self.__frame.configure(bg=t.background)

        self.ui.setBackground(t.background)
        
        self.__text.config(
            bg=t.background,
            fg=t.foreground,
            insertbackground=t.cursor,
            selectbackground=t.select_bg,
            selectforeground=t.foreground  # 🔹 текст выделения теперь виден
        )
        self.__text.tag_configure("active_line", background=t.line_highlight)
        self.__text.tag_configure("number", foreground=t.number_color)
        self.highlightCurrentLine()
        self.highlightSyntax()

        # self.__line_numbers.config(
        #     bg=t.line_number_bg,
        #     fg=t.line_number_fg
        # )
    def toggleTheme(self):
        self.applyTheme(LIGHT_THEME if self.__theme.name == "Dark" else DARK_THEME)

    def __onKeyRelease(self, event=None):
        """Обновляем подсветку после любого изменения"""
        self.highlightCurrentLine()
        self.highlightSyntax()

    def highlightCurrentLine(self, event=None):
        self.__text.tag_remove("active_line", "1.0", "end")
        self.__text.tag_add("active_line", "insert linestart", "insert lineend+1c")
        self.__text.tag_lower("active_line")

    def highlightSyntax(self):
        """Простейшая подсветка чисел"""
        self.__text.tag_remove("number", "1.0", "end")
        text = self.__text.get("1.0", "end-1c")
        for match in re.finditer(r"\b\d+(\.\d+)?\b", text):
            start = f"1.0 + {match.start()}c"
            end = f"1.0 + {match.end()}c"
            self.__text.tag_add("number", start, end)

              
    def setFont(self, family: str = "Consolas", size: int = 12):
        self.__font = font.Font(family=family, size=size)
        self.__text.configure(font=self.__font)
    def changeFontSize(self, delta: int):
        current_size = self.__font.cget("size")
        new_size = current_size + delta

        MIN_FONT_SIZE = 6
        MAX_FONT_SIZE = 72
        new_size = max(MIN_FONT_SIZE, min(MAX_FONT_SIZE, new_size))

        self.__font.configure(size=new_size)
    def __onTab(self, event: tk.Event):
        """Обрабатывает Tab — добавляет отступ для выделенных строк"""
        try:
            start = self.__text.index("sel.first")
            end = self.__text.index("sel.last")
        except tk.TclError:
            self.__text.insert(tk.INSERT, "    ") 
            return "break"

        start_line = int(start.split(".")[0])
        end_line = int(end.split(".")[0])

        for line in range(start_line, end_line + 1):
            self.__text.insert(f"{line}.0", "    ")

        # пересчитываем выделение, чтобы оно оставалось выделенным
        self.__text.tag_add("sel", f"{start_line}.0", f"{end_line}.end")
        return "break"

    def __onShiftTab(self, event: tk.Event):
        """Обрабатывает Shift+Tab — удаляет отступ у выделенных строк"""
        try:
            start = self.__text.index("sel.first")
            end = self.__text.index("sel.last")
        except tk.TclError:
            return "break"

        start_line = int(start.split(".")[0])
        end_line = int(end.split(".")[0])

        for line in range(start_line, end_line + 1):
            line_start = f"{line}.0"
            line_text = self.__text.get(line_start, f"{line}.end")

            # убираем первые 4 пробела или таб
            if line_text.startswith("    "):
                self.__text.delete(line_start, f"{line_start}+4c")
            elif line_text.startswith("\t"):
                self.__text.delete(line_start, f"{line_start}+1c")

        # пересчитываем выделение
        self.__text.tag_add("sel", f"{start_line}.0", f"{end_line}.end")
        return "break"
    ###
    def undo(self, event:Optional[tk.Event] = None):
        try:
            self.__text.edit_undo()
        except tk.TclError:
            pass

    def redo(self, event:Optional[tk.Event] = None):
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
        
    