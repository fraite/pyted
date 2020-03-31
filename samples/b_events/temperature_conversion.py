import tkinter
from tkinter import ttk


class GuiBinder:
    """binder for GuiCollection"""

    def __init__(self):
        pass
        self.temperature_c = ""
        self.temperature_f = ""

    def entry_c_return_(self, event, obj):
        return

    def entry_c_focus_out(self, event, obj):
        return

    def entry_f_return_(self, event, obj):
        return

    def entry_f_focus_out(self, event, obj):
        return

    def win_close(self):
        return


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
        self._cancel = None
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
        self.root = root
        # new_widget(Project)
        # project_name = GuiCollection
        # new_widget(StringVar)
        self.temperature_c = tkinter.StringVar(root)
        self.temperature_c.set("")
        init_tk_var(self.temperature_c, gui_binder, "temperature_c")
        # new_widget(StringVar)
        self.temperature_f = tkinter.StringVar(root)
        self.temperature_f.set("")
        init_tk_var(self.temperature_f, gui_binder, "temperature_f")
        # new_widget(Toplevel)
        self.gui_1 = top_level
        self.gui_1.rowconfigure(1, minsize="0", weight="1", pad="0")
        self.gui_1.rowconfigure(0, minsize="0", weight="0", pad="0")
        self.gui_1.rowconfigure(2, minsize="0", weight="1", pad="0")
        self.gui_1.columnconfigure(0, minsize="0", weight="1", pad="0")
        self.gui_1.columnconfigure(1, minsize="0", weight="0", pad="0")
        # self.gui_1.grid_size(number_columns="4")
        # self.gui_1.grid_size(number_rows="4")
        self.gui_1.config(height="0")
        self.gui_1.config(width="0")
        self.gui_1.title("My demo window")
        self.gui_1.config(relief="flat")
        # new_widget(Entry)
        self.entry_c = tkinter.Entry(self.gui_1)
        self.entry_c.grid(column="0")
        self.entry_c.grid(row="1")
        self.entry_c.grid(sticky="NSEW")
        self.entry_c.config(width="20")
        self.entry_c.config(borderwidth="2")
        self.entry_c.config(state="normal")
        self.entry_c.config(relief="sunken")
        self.entry_c.config(textvariable=self.temperature_c)
        # if gui_binder is not None and not isinstance(gui_binder, dict):
        self.entry_c.bind("<Return>", lambda
                         event, arg1=self.entry_c:
                         self.entry_c_return_(event, arg1))
        # if gui_binder is not None and not isinstance(gui_binder, dict):
        self.entry_c.bind("<FocusOut>", lambda
                         event, arg1=self.entry_c:
                         self.entry_c_focus_out(event, arg1))
        # new_widget(Label)
        self.label1 = tkinter.Label(self.gui_1)
        self.label1.grid(column="1")
        self.label1.grid(row="1")
        self.label1.grid(sticky="")
        self.label1.config(height="0")
        self.label1.config(width="0")
        self.label1.config(anchor="e")
        self.label1.config(borderwidth="0")
        self.label1.config(relief="flat")
        self.label1.config(text=" C")
        self.label1.config(underline="0")
        # new_widget(Label)
        self.label2 = tkinter.Label(self.gui_1)
        self.label2.grid(column="0")
        self.label2.grid(row="0")
        self.label2.grid(sticky="")
        self.label2.config(height="0")
        self.label2.config(width="0")
        self.label2.config(anchor="e")
        self.label2.config(borderwidth="0")
        self.label2.config(relief="flat")
        self.label2.config(text="Temperature conversion:")
        self.label2.config(underline="0")
        # new_widget(Entry)
        self.entry_f = tkinter.Entry(self.gui_1)
        self.entry_f.grid(column="0")
        self.entry_f.grid(row="2")
        self.entry_f.grid(sticky="NSEW")
        self.entry_f.config(width="20")
        self.entry_f.config(borderwidth="2")
        self.entry_f.config(state="normal")
        self.entry_f.config(relief="sunken")
        self.entry_f.config(textvariable=self.temperature_f)
        # if gui_binder is not None and not isinstance(gui_binder, dict):
        self.entry_f.bind("<Return>", lambda
                         event, arg1=self.entry_f:
                         self.entry_f_return_(event, arg1))
        # if gui_binder is not None and not isinstance(gui_binder, dict):
        self.entry_f.bind("<FocusOut>", lambda
                         event, arg1=self.entry_f:
                         self.entry_f_focus_out(event, arg1))
        # new_widget(Label)
        self.label3 = tkinter.Label(self.gui_1)
        self.label3.grid(column="1")
        self.label3.grid(row="2")
        self.label3.grid(sticky="")
        self.label3.config(height="0")
        self.label3.config(width="0")
        self.label3.config(anchor="e")
        self.label3.config(borderwidth="0")
        self.label3.config(relief="flat")
        self.label3.config(text=" F")
        self.label3.config(underline="0")
        top_level.protocol("WM_DELETE_WINDOW", lambda: self.win_close_ok(False))

        if parent is None:
            if modal:
                root.mainloop()
        else:
            if modal:
                top_level.grab_set()
                root.wait_window(top_level)

    def copy_bound_object_to_tkinter_var(self):
        gui_binder = getattr(self, 'gui_binder', None)
        if gui_binder is None:
            pass
        elif isinstance(gui_binder, dict):
            for key in gui_binder:
                try:
                    getattr(self, key).set(gui_binder[key])
                except AttributeError:
                    pass
        else:
            for key in vars(gui_binder):
                try:
                    getattr(self, key).set(getattr(gui_binder, key))
                except AttributeError:
                    pass

    def copy_tkinter_var_to_bound_object(self):
        gui_binder = getattr(self, 'gui_binder', None)
        if gui_binder is None:
            pass
        elif isinstance(gui_binder, dict):
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

    def win_close_ok(self, text):
        self._cancel = text
        gui_binder = getattr(self, 'gui_binder', None)
        self.copy_tkinter_var_to_bound_object()
        if isinstance(gui_binder, GuiBinder):
            self.win_close()
        self.gui_1.destroy()

    def win_close_cancel(self):
        self._cancel = True
        gui_binder = getattr(self, 'gui_binder', None)
        if gui_binder is None:
            pass
        elif isinstance(gui_binder, dict):
            pass
        else:
            self.win_close()
        self.gui_1.destroy()

    def entry_c_return_(self, event, obj):
        gui_binder = getattr(self, "gui_binder", None)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            self.copy_tkinter_var_to_bound_object()
            try:
                gui_binder.entry_c_return_(event, obj)
            except AttributeError:
                pass
            self.copy_bound_object_to_tkinter_var()
        return

    def entry_c_focus_out(self, event, obj):
        gui_binder = getattr(self, "gui_binder", None)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            self.copy_tkinter_var_to_bound_object()
            try:
                gui_binder.entry_c_focus_out(event, obj)
            except AttributeError:
                pass
            self.copy_bound_object_to_tkinter_var()
        return

    def entry_f_return_(self, event, obj):
        gui_binder = getattr(self, "gui_binder", None)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            self.copy_tkinter_var_to_bound_object()
            try:
                gui_binder.entry_f_return_(event, obj)
            except AttributeError:
                pass
            self.copy_bound_object_to_tkinter_var()
        return

    def entry_f_focus_out(self, event, obj):
        gui_binder = getattr(self, "gui_binder", None)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            self.copy_tkinter_var_to_bound_object()
            try:
                gui_binder.entry_f_focus_out(event, obj)
            except AttributeError:
                pass
            self.copy_bound_object_to_tkinter_var()
        return

    def win_close(self):
        gui_binder = getattr(self, "gui_binder", None)
        if gui_binder is not None and not isinstance(gui_binder, dict):
            try:
                gui_binder.win_close()
            except AttributeError:
                pass
        return


def gui_1(gui_binder=None, parent=None, modal=True):
    appl = GuiCollection(gui_binder, parent, modal)
    if gui_binder is None or isinstance(gui_binder, dict):
        if appl._cancel == True:
            result_dict = {}
        else:
            result_dict = {'_button': appl._cancel}
            for key in vars(appl):
                if isinstance(getattr(appl, key), tkinter.StringVar):
                    result_dict[key] = getattr(appl, key).get()
        return result_dict
    else:
        return appl


if __name__ == "__main__":
    gui = gui_1()
    print(gui)
