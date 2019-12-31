import tkinter


class Handles:
    """Widget handles

    Handles at each corner of the widget showing selected widget. In the future may be able to resize widget using
    handles.
    """

    def __init__(self, root_window: tkinter.Tk):

        self.root_window = root_window

        self.handle_NW_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_NE_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_SW_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_SE_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)

    def place_selected_widget_handles(self, tk_widget: tkinter.Widget) -> None:
        """Put handles around the selected widget

        Places four canvas objects at each corner of the self.selected_widget object.
        """
        tk_widget.update_idletasks()
        root_x = self.root_window.winfo_rootx()
        root_y = self.root_window.winfo_rooty()
        widget_x1 = tk_widget.winfo_rootx()
        widget_y1 = tk_widget.winfo_rooty()
        widget_x2 = widget_x1 + tk_widget.winfo_width()
        widget_y2 = widget_y1 + tk_widget.winfo_height()
        self.handle_NW_canvas.place(x=(widget_x1 - root_x - 4), y=(widget_y1 - root_y - 4))
        self.handle_NE_canvas.place(x=(widget_x2 - root_x - 4), y=(widget_y1 - root_y - 4))
        self.handle_SW_canvas.place(x=(widget_x1 - root_x - 4), y=(widget_y2 - root_y - 4))
        self.handle_SE_canvas.place(x=(widget_x2 - root_x - 4), y=(widget_y2 - root_y - 4))

    def remove_selected_widget_handles(self) -> None:
        """Remove widget handles

        Removes widget handles from widget (normally selected widget)
        """
        self.handle_NW_canvas.place_forget()
        self.handle_NE_canvas.place_forget()
        self.handle_SW_canvas.place_forget()
        self.handle_SE_canvas.place_forget()