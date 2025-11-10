import tkinter as tk



def showPasswordDialog(root,  title="Enter Password") -> str | None:
        """Открывает модальное окно для ввода пароля и возвращает строку или None, если закрыто"""
        password = None

        # Создаем окно
        pw_win = tk.Toplevel(root)
        pw_win.title(title)
        pw_win.geometry("300x120")
        pw_win.resizable(False, False)
        pw_win.grab_set()  # делаем окно модальным (блокирует родительское)

        tk.Label(pw_win, text="Password:").pack(pady=(20, 5))

        pw_var = tk.StringVar()
        pw_entry = tk.Entry(pw_win, textvariable=pw_var, show="*", width=25)
        pw_entry.pack(pady=5)
        pw_entry.focus_set()

        def submit():
            nonlocal password
            password = pw_var.get()
            pw_win.destroy()

        def cancel():
            nonlocal password
            password = None
            pw_win.destroy()

        btn_frame = tk.Frame(pw_win)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", width=10, command=submit).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", width=10, command=cancel).pack(side="left", padx=5)

        pw_win.wait_window()  # ждем закрытия окна
        return password
