import tkinter as tk
from typing import Optional
from tkinter import font

from  psswd import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from UI import UI

from dataclasses import dataclass

@dataclass
class Theme:
    name: str
    background: str
    foreground: str
    cursor: str
    select_bg: str
    curr_select_bg: str
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
    curr_select_bg = "#388EA8" ,
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
    curr_select_bg="#7ba5ff",
    line_highlight="#f0f0f0",
    line_number_bg="#f3f3f3",
    line_number_fg="#555555",
    number_color="#0066cc",

)

class Editor:
    def __init__(self, root : tk.Tk,ui: "UI",  theme: Theme = LIGHT_THEME):

        self.__root = root
        self.ui = ui

        self.modified = False
        self.__fullText:str = ""
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
            yscrollcommand=self.__scrollbar.set  
        )
        self.__text.pack(expand=True, fill="both")
        self.__scrollbar.config(command=self.__text.yview) 

        self.__text.bind("<<Modified>>", self.__onModified)
        self.__text.bind("<Control-y>", self.redo)
        self.__text.bind("<Tab>", self.__onTab)
        self.__text.bind("<Shift-Tab>", self.__onShiftTab)
        self.__text.bind("<KeyRelease>", self.__onKeyRelease)
        self.__text.bind("<Button-1>", self.__onCursorMove)
        self.__text.bind("<Motion>", self.__onCursorMove)
        self.__text.bind("<Control-MouseWheel>", self.__onCtrlMouseWheel)
        self.__text.bind("<Control-f>", lambda e: self.openFindDialog())

        self.__text.tag_config("find_match", background=self.__theme.select_bg)
        self.__text.tag_config("find_current", background=self.__theme.curr_select_bg)


        self.__findQuery: str = ""
        self.__findPositions: list[tuple[int,str]] = []
        self.__findCurrentIdx: int = -1

        self.setText("")

    def initTheme(self):
        self.applyTheme(self.__theme)
    def __onCtrlMouseWheel(self, event: tk.Event):
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
        return "break"

    def __onCursorMove(self, event: Optional[tk.Event|None]=None):
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
            selectforeground=t.foreground
        )
        self.__text.tag_configure("active_line", background=t.line_highlight)
        self.__text.tag_configure("number", foreground=t.number_color)
        self.highlightCurrentLine()

    def toggleTheme(self):
        self.applyTheme(LIGHT_THEME if self.__theme.name == "Dark" else DARK_THEME)

    def __onKeyRelease(self, event: Optional[tk.Event|None]=None):
        self.highlightCurrentLine()


    def highlightCurrentLine(self, event: Optional[tk.Event]=None):
        self.__text.tag_remove("active_line", "1.0", "end")
        self.__text.tag_add("active_line", "insert linestart", "insert lineend+1c")
        self.__text.tag_lower("active_line")



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

            if line_text.startswith("    "):
                self.__text.delete(line_start, f"{line_start}+4c")
            elif line_text.startswith("\t"):
                self.__text.delete(line_start, f"{line_start}+1c")

        self.__text.tag_add("sel", f"{start_line}.0", f"{end_line}.end")
        return "break"
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
        print("Text starts to set")
        self.__text.edit_modified(False)
        self.__text.delete("1.0", tk.END)
        self.__text.insert(tk.END, text)
        self.__root.after_idle(func = self.__notModified)
        print("Text finished to set")
    def setFullText(self, text:str):
        self.__fullText = text


    def __notModified(self):
        self.modified = False


    def getText(self) -> str:
        print("Text returning to set")
        return self.__text.get(1.0, tk.END)
    def __onModified(self, event: tk.Event):
        if self.__text.edit_modified():
            self.modified = True
            self.__text.edit_modified(False)

            self.__findPositions = []
            self.__findCurrentIdx = -1
            self.__findQuery = ""
            self.__text.tag_remove("find_match", "1.0", "end")
            self.__text.tag_remove("find_current", "1.0", "end")
    def openFindDialog(self):
        """Открывает окно поиска"""
        win = tk.Toplevel(self.__root)
        win.title("Find")
        win.geometry("300x100")
        win.resizable(False, False)
        win.transient(self.__root)

        tk.Label(win, text="Find:").pack(anchor="w", padx=10, pady=(10,0))

        find_var = tk.StringVar()
        entry = tk.Entry(win, textvariable=find_var, width=30)
        entry.pack(padx=10)
        entry.focus_set()

        def do_find(event: Optional[tk.Event]=None):
            query = find_var.get()
            if query != self.__findQuery:
                self.__findQuery = query
                self.__findCurrentIdx = -1
                self.__findPositions = []
                self.__findAll(query)

            self.__findNext()

        entry.bind("<Return>", do_find)

        tk.Button(win, text="Find", command=do_find).pack(pady=10)
    def __findAll(self, pattern: str):
        self.__text.tag_remove("find_match", "1.0", "end")
        self.__text.tag_remove("find_current", "1.0", "end")
        self.__findPositions.clear()
        self.__findCurrentIdx = -1

        if not pattern:
            return

        start_index = "1.0"
        while True:
            pos = self.__text.search(pattern, start_index, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(pattern)}c"
            self.__text.tag_add("find_match", pos, end)
            self.__findPositions.append((pos, end))
            start_index = end

    def __findNext(self):
        if not self.__findPositions:
            return

        self.__text.tag_remove("find_current", "1.0", "end")

        self.__findCurrentIdx = (self.__findCurrentIdx + 1) % len(self.__findPositions)

        start, end = self.__findPositions[self.__findCurrentIdx]
        self.__text.tag_add("find_current", start, end)
        self.__text.mark_set("insert", start)
        self.__text.see(start)
