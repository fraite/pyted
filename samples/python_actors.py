import tkinter


class GuiBinder:
    """binder for GuiCollection"""

    def __init__(self):
        pass
        self.first_name = ""
        self.surname = ""
        self.country = "UK"
        self.writer = "1"
        self.director = "0"
        self.actor = "1"

    def entry1_button_1(self, obj, event):
        return

    def win_close(self):
        pass


def init_tk_var(tk_var, gui_binder, tk_var_name):
    if gui_binder is not None:
        if isinstance(gui_binder, dict):
            try:
                value = gui_binder[tk_var_name]
            except KeyError:
                value = None
        else:
            value = getattr(gui_binder, tk_var_name, None)
        if value is not None:
            tk_var.set(value)


class GuiCollection:
    """GuiCollection"""

    def __init__(self, gui_binder=None, parent=None, modal=True):
        self.gui_binder = gui_binder
        self.parent = parent
        if parent is None:
            root = tkinter.Tk()
            top_level = root
        else:
            # find root
            root = parent
            while root.master is not None:
                root = parent.master
            # generate top level window
            top_level = tkinter.Toplevel(parent)
        # new_widget(Project)
        # project_name = GuiCollection
        # new_widget(StringVar)
        self.first_name = tkinter.StringVar()
        self.first_name.set("")
        init_tk_var(self.first_name, gui_binder, "first_name")
        # new_widget(StringVar)
        self.surname = tkinter.StringVar()
        self.surname.set("")
        init_tk_var(self.surname, gui_binder, "surname")
        # new_widget(StringVar)
        self.country = tkinter.StringVar()
        self.country.set("UK")
        init_tk_var(self.country, gui_binder, "country")
        # new_widget(StringVar)
        self.writer = tkinter.StringVar()
        self.writer.set("1")
        init_tk_var(self.writer, gui_binder, "writer")
        # new_widget(StringVar)
        self.director = tkinter.StringVar()
        self.director.set("0")
        init_tk_var(self.director, gui_binder, "director")
        # new_widget(StringVar)
        self.actor = tkinter.StringVar()
        self.actor.set("1")
        init_tk_var(self.actor, gui_binder, "actor")
        # new_widget(Toplevel)
        self.gui_1 = top_level
        self.gui_1.rowconfigure(2, minsize="0", weight="1", pad="0")
        self.gui_1.rowconfigure(1, minsize="0", weight="1", pad="0")
        self.gui_1.rowconfigure(0, minsize="0", weight="0", pad="0")
        self.gui_1.columnconfigure(0, minsize="0", weight="1", pad="0")
        # self.gui_1.grid_size(number_columns="4")
        # self.gui_1.grid_size(number_rows="10")
        self.gui_1.title("Python Actors")
        self.gui_1.config(relief="flat")
        # new_widget(Frame)
        self.frame1 = tkinter.Frame(self.gui_1)
        self.frame1.rowconfigure(0, minsize="0", weight="1", pad="0")
        self.frame1.rowconfigure(1, minsize="0", weight="1", pad="0")
        self.frame1.columnconfigure(1, minsize="0", weight="1", pad="0")
        self.frame1.columnconfigure(0, minsize="0", weight="0", pad="0")
        self.frame1.grid(column="0")
        self.frame1.grid(row="0")
        self.frame1.grid(sticky="EW")
        # self.frame1.grid_size(number_columns="2")
        # self.frame1.grid_size(number_rows="2")
        self.frame1.config(borderwidth="2")
        self.frame1.config(relief="flat")
        # new_widget(Entry)
        self.entry1 = tkinter.Entry(self.frame1)
        self.entry1.grid(column="1")
        self.entry1.grid(row="0")
        self.entry1.grid(sticky="EW")
        self.entry1.config(borderwidth="2")
        self.entry1.config(relief="sunken")
        self.entry1.config(textvariable=self.first_name)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            self.entry1.bind("<Button-1>", lambda
                             event, arg1=self.entry1:
                             gui_binder.entry1_button_1(event, arg1))
        # new_widget(Entry)
        self.sur_name_entry = tkinter.Entry(self.frame1)
        self.sur_name_entry.grid(column="1")
        self.sur_name_entry.grid(row="1")
        self.sur_name_entry.grid(sticky="EW")
        self.sur_name_entry.config(borderwidth="2")
        self.sur_name_entry.config(relief="sunken")
        self.sur_name_entry.config(textvariable=self.surname)
        # new_widget(Label)
        self.label1 = tkinter.Label(self.frame1)
        self.label1.grid(column="0")
        self.label1.grid(row="0")
        self.label1.grid(sticky="W")
        self.label1.config(anchor="w")
        self.label1.config(borderwidth="0")
        self.label1.config(relief="flat")
        self.label1.config(text="First name")
        self.label1.config(underline="0")
        # new_widget(Label)
        self.label2 = tkinter.Label(self.frame1)
        self.label2.grid(column="0")
        self.label2.grid(row="1")
        self.label2.grid(sticky="W")
        self.label2.config(anchor="w")
        self.label2.config(borderwidth="0")
        self.label2.config(relief="flat")
        self.label2.config(text="Surname")
        self.label2.config(underline="0")
        # new_widget(Frame)
        self.frame2 = tkinter.Frame(self.gui_1)
        self.frame2.rowconfigure(0, minsize="0", weight="1", pad="0")
        self.frame2.rowconfigure(1, minsize="0", weight="1", pad="0")
        self.frame2.rowconfigure(2, minsize="0", weight="1", pad="0")
        self.frame2.rowconfigure(3, minsize="0", weight="1", pad="0")
        self.frame2.columnconfigure(0, minsize="0", weight="1", pad="0")
        self.frame2.grid(column="0")
        self.frame2.grid(row="1")
        self.frame2.grid(sticky="NSEW")
        # self.frame2.grid_size(number_columns="1")
        # self.frame2.grid_size(number_rows="4")
        self.frame2.config(borderwidth="2")
        self.frame2.config(relief="groove")
        # new_widget(Label)
        self.label3 = tkinter.Label(self.frame2)
        self.label3.grid(column="0")
        self.label3.grid(row="0")
        self.label3.grid(sticky="W")
        self.label3.config(anchor="w")
        self.label3.config(borderwidth="0")
        self.label3.config(relief="flat")
        self.label3.config(text="County of birth")
        self.label3.config(underline="0")
        # new_widget(Radiobutton)
        self.radiobutton1 = tkinter.Radiobutton(self.frame2)
        self.radiobutton1.grid(column="0")
        self.radiobutton1.grid(row="1")
        self.radiobutton1.grid(sticky="w")
        self.radiobutton1.config(borderwidth="2")
        self.radiobutton1.config(relief="flat")
        self.radiobutton1.config(value="UK")
        self.radiobutton1.config(text="UK")
        self.radiobutton1.config(variable=self.country)
        # new_widget(Radiobutton)
        self.radiobutton2 = tkinter.Radiobutton(self.frame2)
        self.radiobutton2.grid(column="0")
        self.radiobutton2.grid(row="2")
        self.radiobutton2.grid(sticky="w")
        self.radiobutton2.config(borderwidth="2")
        self.radiobutton2.config(relief="flat")
        self.radiobutton2.config(value="USA")
        self.radiobutton2.config(text="USA")
        self.radiobutton2.config(variable=self.country)
        # new_widget(Radiobutton)
        self.radiobutton3 = tkinter.Radiobutton(self.frame2)
        self.radiobutton3.grid(column="0")
        self.radiobutton3.grid(row="3")
        self.radiobutton3.grid(sticky="w")
        self.radiobutton3.config(borderwidth="2")
        self.radiobutton3.config(relief="flat")
        self.radiobutton3.config(value="France")
        self.radiobutton3.config(text="France")
        self.radiobutton3.config(variable=self.country)
        # new_widget(Frame)
        self.frame3 = tkinter.Frame(self.gui_1)
        self.frame3.rowconfigure(0, minsize="0", weight="1", pad="0")
        self.frame3.rowconfigure(1, minsize="0", weight="1", pad="0")
        self.frame3.rowconfigure(2, minsize="0", weight="1", pad="0")
        self.frame3.rowconfigure(3, minsize="0", weight="1", pad="0")
        self.frame3.columnconfigure(0, minsize="0", weight="1", pad="0")
        self.frame3.grid(column="0")
        self.frame3.grid(row="2")
        self.frame3.grid(sticky="NSEW")
        # self.frame3.grid_size(number_columns="1")
        # self.frame3.grid_size(number_rows="4")
        self.frame3.config(borderwidth="2")
        self.frame3.config(relief="groove")
        # new_widget(Label)
        self.label4 = tkinter.Label(self.frame3)
        self.label4.grid(column="0")
        self.label4.grid(row="0")
        self.label4.grid(sticky="W")
        self.label4.config(anchor="w")
        self.label4.config(borderwidth="0")
        self.label4.config(relief="flat")
        self.label4.config(text="Credits")
        self.label4.config(underline="0")
        # new_widget(Checkbutton)
        self.checkbutton1 = tkinter.Checkbutton(self.frame3)
        self.checkbutton1.grid(column="0")
        self.checkbutton1.grid(row="1")
        self.checkbutton1.grid(sticky="W")
        self.checkbutton1.config(borderwidth="2")
        self.checkbutton1.config(relief="flat")
        self.checkbutton1.config(onvalue="1")
        self.checkbutton1.config(offvalue="0")
        self.checkbutton1.config(text="Writer")
        self.checkbutton1.config(variable=self.writer)
        # new_widget(Checkbutton)
        self.checkbutton2 = tkinter.Checkbutton(self.frame3)
        self.checkbutton2.grid(column="0")
        self.checkbutton2.grid(row="2")
        self.checkbutton2.grid(sticky="W")
        self.checkbutton2.config(borderwidth="2")
        self.checkbutton2.config(relief="flat")
        self.checkbutton2.config(onvalue="1")
        self.checkbutton2.config(offvalue="0")
        self.checkbutton2.config(text="Actor")
        self.checkbutton2.config(variable=self.actor)
        # new_widget(Checkbutton)
        self.checkbutton3 = tkinter.Checkbutton(self.frame3)
        self.checkbutton3.grid(column="0")
        self.checkbutton3.grid(row="3")
        self.checkbutton3.grid(sticky="W")
        self.checkbutton3.config(borderwidth="2")
        self.checkbutton3.config(relief="flat")
        self.checkbutton3.config(onvalue="1")
        self.checkbutton3.config(offvalue="0")
        self.checkbutton3.config(text="Director")
        self.checkbutton3.config(variable=self.director)
        top_level.protocol("WM_DELETE_WINDOW", self.win_close)

        if parent is None:
            root.mainloop()
        else:
            if modal:
                top_level.grab_set()
                root.wait_window(top_level)

    def win_close(self):
        gui_binder = getattr(self, 'gui_binder', None)
        if gui_binder is not None:
            if isinstance(gui_binder, dict):
                for key in gui_binder:
                    try:
                        gui_binder[key] = getattr(self, key).get()
                    except AttributeError:
                        pass
            else:
                for key in vars(gui_binder):
                    try:
                        setattr(gui_binder, key, getattr(self, key).get())
                    except AttributeError:
                        pass
                gui_binder.win_close()
        self.gui_1.destroy()


def gui_1(gui_binder=None, parent=None, modal=True):
    appl = GuiCollection(gui_binder, parent, modal)
    if gui_binder is None or isinstance(gui_binder, dict):
        result_dict = {}
        for key in vars(appl):
            if isinstance(getattr(appl, key), tkinter.StringVar):
                result_dict[key] = getattr(appl, key).get()
        return result_dict
    else:
        return appl


if __name__ == "__main__":
    gui = gui_1()
    print(gui)

