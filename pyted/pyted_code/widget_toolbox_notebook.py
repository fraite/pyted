import tkinter
import pyted.pyted_code.pyted_core as pyted_core


class WidgetToolboxNotebook:
    """Widget attribute frame

    Frame that shows the widget attributes (including variables), and events. The frame additionally shows the row
    and column attributes of the parent.
    """

    def __init__(self, pyted_core: pyted_core):
        self.pyted_core: pyted_core = pyted_core
        self.widget_in_toolbox_chosen = None
        self.widget_in_toolbox_chosen_tk_var = tkinter.StringVar()
        self.widget_in_toolbox_chosen_double_click = False