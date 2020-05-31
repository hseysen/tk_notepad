import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox


class CNotePad(tk.Frame):
    """
    Very basic program that attempts to simulate the behavior of Notepad.
    """
    def __init__(self, master):
        """
        Initialize the program.
        :param master: tk.Tk
        """
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_close_program)         # method to call on program exit
        self.style = ttk.Style()                # later used for ttk-styling
        self.textfont = ("Consolas", 14)        # font for the text everywhere

        self.configure_master()
        self.initialize_menu()
        self.create_notebook()
        self.background_process()
        self.bind_keys()

    def background_process(self):
        """
        Update the "Save", "Save as", and "Close" buttons on the "File" menu bar,
        depending on whether or not at least one file is open.
        :return: None
        """
        try:
            self.notebook.index("current")
        except Exception:
            if self.file_menu.entrycget(2, "state") == tk.NORMAL:
                self.file_menu.entryconfig(2, state=tk.DISABLED)
                self.file_menu.entryconfig(3, state=tk.DISABLED)
                self.file_menu.entryconfig(4, state=tk.DISABLED)
        else:
            if self.file_menu.entrycget(2, "state") == tk.DISABLED:
                self.file_menu.entryconfig(2, state=tk.NORMAL)
                self.file_menu.entryconfig(3, state=tk.NORMAL)
                self.file_menu.entryconfig(4, state=tk.NORMAL)

        self.master.after(200, self.background_process)

    def configure_master(self):
        """
        Configures the root object's name, icon and size.
        :return: None
        """
        self.master.title("CNotePad")
        self.master.iconbitmap("note.ico")
        self.master.geometry("1013x628")
        self.master.minsize(width=1013, height=628)

    def initialize_menu(self):
        """
        Responsible for creating the menu bar and setting up buttons.
        :return: None
        """
        self.menu_bar = tk.Menu(self.master)
        self.master.option_add("*tearOff", False)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.file_menu_new)
        self.file_menu.add_command(label="Open", command=self.file_menu_open)
        self.file_menu.add_command(label="Save", command=self.file_menu_save)
        self.file_menu.add_command(label="Save as", command=self.file_menu_save_as)
        self.file_menu.add_command(label="Close", command=self.file_menu_close)
        self.file_menu.add_command(label="Close all", command=self.close_all_tabs)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close_program)

    def file_menu_close(self, asksave=True, programclose=False):
        """
        Closes the current tab of the self.notebook when called.
        :param programclose: bool
        :param asksave: bool
        :return: None
        """
        try:
            # If there are no tabs in self.notebook, this line should raise an Exception
            # in that case, there is nothing to be closed, so the method terminates
            fn, write_area, initial_text = self.tabs[self.notebook.index("current")]
            if initial_text == write_area.get(1.0, tk.INSERT):
                asksave = False
        except Exception:
            return
        if asksave:
            if programclose:
                answ = messagebox.askyesno(title="Closing All Tabs", message="Do you want to save the file?")
            else:
                answ = messagebox.askyesnocancel(title="Closing file", message="Do you want to save the file?")
            if answ is None:
                return
            elif answ:            # may happen that the user presses "Cancel", rather than "Save"
                self.file_menu_save(openagain=False)
                return
        self.tabs.pop(self.notebook.index("current"))               # remove the tab's information from tabs list
        self.notebook.forget(self.notebook.index("current"))        # completely forget the tab

    def file_menu_save_as(self, openagain=True):
        """
        Saves the text on the current tab of self.notebook as a new file.
        :return: None
        """
        try:
            # If there is any issue during saving or naming the file, these lines should raise an Exception
            fn = filedialog.asksaveasfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py *.pyw")],
                                              defaultextension="*.*")
            if fn:
                self.file_menu_save(fn, openagain=openagain)
        except Exception:
            pass

    def file_menu_save(self, saveasfn=None, openagain=True):
        """
        Saves the text on the currently active text file. If the text file does not exist
        on the system, this method calls self.file_menu_save_as method.
        :param openagain: bool
        :param saveasfn: str
        :return: None
        """
        fn, write_area, initial_text = self.tabs[self.notebook.index("current")]

        if saveasfn is None:
            if initial_text == write_area.get(1.0, tk.INSERT):
                # This means the file was not changed since it was last loaded, so there's no point in saving it.
                return

        try:
            # the variable saveasfn is None by default,
            # it only gets overwritten from the self.file_menu_save_as method
            if saveasfn is None:
                saveasfn = fn

            with open(saveasfn, "w") as wf:
                wf.write(write_area.get(1.0, tk.INSERT))
        except FileNotFoundError:
            pass
        except OSError:
            # This Exception is only raised when the file name is invalid, thus the user needs to
            # choose a different name for the file. This Exception is also raised when a new file is
            # created and doesn't have a name yet, so needs to be saved for the first time
            self.file_menu_save_as(openagain=openagain)
        else:
            # If no exceptions occur, and the file get saved successfully, the program closes
            # the current tab, and reloads it from the file. This way, the variable initial_text
            # is also updated.
            self.file_menu_close(asksave=False)
            if openagain:
                self.file_menu_open(saveasfn)
                self.notebook.select(len(self.tabs) - 1)

    def file_menu_open(self, fn=None):
        """
        Calls a File Dialog to open a new text file.
        :param fn: str
        :return: None
        """
        try:
            if fn is None:
                fn = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py *.pyw")])

            # Loading in the information written on the file selected by the user. If the entered file
            # does not exist, FileNotFoundError will be raised.
            with open(fn, "r") as rf:
                write_area = self.file_menu_new(fn)
                write_area.insert(tk.INSERT, rf.read())
                initial_text = write_area.get(1.0, tk.INSERT)
                self.notebook.select(len(self.tabs) - 1)
                self.tabs[self.notebook.index("current")][2] = initial_text    # update for saving
        except FileNotFoundError:
            pass

    def file_menu_new(self, tabname="*new"):
        """
        Creates a new tab in self.notebook. Returns the tk.Text object that is created on the tab,
        just for simplicity.
        :param tabname: str
        :return: tk.Text
        """
        fr = tk.LabelFrame(self.notebook, bg="black")
        fr.pack(expand=True, fill="both")

        self.notebook.add(fr, text=tabname)

        write_area = tk.Text(fr, font=self.textfont, wrap=tk.NONE, bg="black", fg="white")
        write_area.place(relwidth=1, relheight=1)

        sc_x = ttk.Scrollbar(fr, command=write_area.xview, orient=tk.HORIZONTAL)
        sc_y = ttk.Scrollbar(fr, command=write_area.yview)
        sc_x.place(relx=0, rely=0.98, relwidth=0.99, relheight=0.02)
        sc_y.place(relx=0.99, rely=0, relwidth=0.01, relheight=0.98)

        beauty_button = ttk.Button(fr, state=tk.DISABLED)           # the gray spot on the bottom right corner
        beauty_button.place(relx=0.99, rely=0.98, relwidth=0.01, relheight=0.02)

        write_area.config(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        write_area.config(insertbackground="cyan")

        initial_text = ""
        self.tabs.append([tabname, write_area, initial_text])       # adds this tab's information to self.tabs list

        return write_area

    def create_notebook(self):
        """
        Creates self.notebook and styles it.
        :return: None
        """
        self.tabs = []

        self.notebook = ttk.Notebook(self.master, takefocus=False)
        self.notebook.pack(expand=True, fill="both")

        self.style.configure("TNotebook", background="gray")

        # print(self.style.layout("Tab"))           # The layout below was taken from here

        self.style.layout("Tab", [('Notebook.tab', {'sticky': 'nswe', 'children': [
            ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                # ('Notebook.focus', {'side': 'top', 'sticky': 'nswe', 'children': [
                ('Notebook.label', {'side': 'top', 'sticky': ''})
            ]})
        ]})])

    def ctrl_save(self):
        """
        Called when CTRL-S key combination is pressed.
        :return: None
        """
        if self.file_menu.entrycget(2, "state") == tk.NORMAL:
            self.file_menu_save()

    def ctrl_close(self):
        """
        Called when CTRL-W key combination is pressed.
        :return: None
        """
        if self.file_menu.entrycget(4, "state") == tk.NORMAL:
            self.file_menu_close()

    def delete_word(self):
        """
        Called when CTRL-BACKSPACE key combination is pressed. Deletes a whole word.
        :return: None
        """
        if self.file_menu.entrycget(2, "state") == tk.NORMAL:
            write_area = self.tabs[self.notebook.index("current")][1]
            try:
                pos = write_area.search(" ", tk.INSERT, stopindex=float(write_area.index("current").split(".")[0]),
                                        backwards=True)
                row, col = map(int, pos.split("."))
                col += 1
                pos = f"{row}.{col}"
                write_area.delete(pos, tk.INSERT)
            except Exception:
                # the exception is raised for the first word of every line
                pos = write_area.index("current").split(".")[0] + ".0"
                write_area.delete(pos, tk.INSERT)

    def bind_keys(self):
        """
        Binds the following key combinations to appropriate methods:
        CTRL-S, CTRL-W, CTRL-SHIFT-W, CTRL-N, CTRL-O, CTRL-BACKSPACE
        :return: None
        """
        self.master.bind("<Control-s>", lambda event: self.ctrl_save())
        self.master.bind("<Control-S>", lambda event: self.ctrl_save())
        self.master.bind("<Control-w>", lambda event: self.ctrl_close())
        self.master.bind("<Control-W>", lambda event: self.ctrl_close())
        self.master.bind("<Control-Shift-W>", lambda event: self.close_all_tabs())
        self.master.bind("<Control-Shift-w>", lambda event: self.close_all_tabs())
        self.master.bind("<Control-n>", lambda event: self.file_menu_new())
        self.master.bind("<Control-N>", lambda event: self.file_menu_new())
        self.master.bind("<Control-o>", lambda event: self.file_menu_open())
        self.master.bind("<Control-O>", lambda event: self.file_menu_open())
        self.master.bind("<Control-BackSpace>", lambda event: self.delete_word())

    def close_all_tabs(self, tabcount=None):
        """
        Closes all open tabs.
        :return: None
        """
        if tabcount is None:
            tabcount = len(self.tabs)
        if tabcount > 0:
            tabcount -= 1
            self.notebook.select(0)
            self.file_menu_close(programclose=True)
            self.close_all_tabs(tabcount=tabcount)

    def close_all_tabs_and_quit(self):
        """
        Calls self.close_all_tabs and exits the program
        :return: None
        """
        self.close_all_tabs()
        self.master.destroy()

    def on_close_program(self):
        """
        Program exit method.
        :return: None
        """
        if messagebox.askyesno(title="Close program", message="Do you want to close the program?"):
            self.close_all_tabs_and_quit()


def main():
    root = tk.Tk()
    app = CNotePad(root)
    app.mainloop()


if __name__ == "__main__":
    main()
