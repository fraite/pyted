#
from __future__ import annotations
from typing import TYPE_CHECKING

import inspect
import tkinter
from tkinter import ttk

import pyted.pyted_widget_types as pyted_widget_types
if TYPE_CHECKING:
    from pyted.pyted_code.pyted_core import PytedCore


class WidgetToolboxNotebook:
    """Widget attribute frame

    Frame that shows the widget attributes (including variables), and events. The frame additionally shows the row
    and column attributes of the parent.
    """

    def __init__(self, pyted_core: PytedCore):
        self.pyted_core = pyted_core
        self.pyted_window = pyted_core.pyted_window
        self.widgets = pyted_core.widgets
        self.attr_frame = pyted_core.attr_frame
        self.handles = pyted_core.handles
        self.navigator_tree = pyted_core.navigator_tree_class

        self.widget_in_toolbox_chosen = None
        self.widget_in_toolbox_chosen_tk_var = tkinter.StringVar()
        self.widget_in_toolbox_chosen_double_click = False

        # setup toolbox frames adding tabs. Done by looking to see all tabs used by widgets
        self.toolbox_notebook = self.pyted_window.toolbox_notebook
        toolbox_frames = {}
        toolbox_row = {}
        toolbox_column = {}
        # force project to be the first tab by setting up StringVar Radiobutton
        obj = pyted_widget_types.StringVar
        tab = obj.tab
        toolbox_frames[tab] = ttk.Frame(self.toolbox_notebook)
        toolbox_row[tab] = 0
        toolbox_column[tab] = 2
        self.toolbox_notebook.add(toolbox_frames[tab], text=tab)
        self.pointer_button = tkinter.Radiobutton(toolbox_frames[tab], text='pointer', indicatoron=0,
                                                  variable=self.widget_in_toolbox_chosen_tk_var,
                                                  value='pointer')
        self.pointer_button.invoke()
        self.pointer_button.bind("<Button-1>", self.toolbox_pointer_button_click)
        self.pointer_button.grid(column=0, row=0)
        # get all the other tabs
        for name, obj in inspect.getmembers(pyted_widget_types):
            if inspect.isclass(obj) and obj:
                try:
                    tab = obj.tab
                except AttributeError:
                    tab = None
                if tab is not None and tab not in toolbox_frames:
                    toolbox_frames[tab] = ttk.Frame(self.toolbox_notebook)
                    toolbox_row[tab] = 0
                    toolbox_column[tab] = 0
                    self.toolbox_notebook.add(toolbox_frames[tab], text=tab)
                    # ttk_label_button = ttk.Button(toolbox_frames[tab], text='pointer')
                    # ttk_label_button.bind("<Button-1>", self.toolbox_pointer_button_click)
                    # ttk_label_button.grid(column=0, row=0)

        # set up inside of Toolbox Frame with a Radiobutton for each widget type
        for name, obj in inspect.getmembers(pyted_widget_types):
            if inspect.isclass(obj) and obj:
                try:
                    tab = obj.tab
                except AttributeError:
                    tab = None
                if tab is not None:
                    try:
                        new_button = tkinter.Radiobutton(toolbox_frames[tab], text=obj.label,
                                                         variable=self.widget_in_toolbox_chosen_tk_var,
                                                         value=obj.label,
                                                         indicatoron=0)
                        try:
                            is_var = obj.is_var
                        except AttributeError:
                            is_var = False
                        if is_var:
                            new_button.bind("<Button-1>", lambda
                                            event, arg1=obj:
                                            self.toolbox_var_button_click_callback(event, arg1)
                                            )
                        else:
                            new_button.bind("<Button-1>", lambda
                                            event, arg1=obj:
                                            self.toolbox_button_click_callback(event, arg1)
                                            )
                            new_button.bind("<Double-Button-1>", lambda
                                            event, arg1=obj:
                                            self.toolbox_button_double_click_callback(event, arg1)
                                            )
                        new_button.grid(column=toolbox_column[tab], row=toolbox_row[tab])

                        toolbox_column[tab] = toolbox_column[tab] + 2
                        if toolbox_column[tab] >= 8:
                            toolbox_row[tab] = toolbox_row[tab] + 2
                            toolbox_column[tab] = toolbox_column[tab] - 8

                    except AttributeError:
                        pass

    # called when button in toolbox clicked
    def toolbox_button_click_callback(self, _event, tk_widget_obj):
        self.pyted_core.deselect_selected_widget()
        self.widget_in_toolbox_chosen = tk_widget_obj
        self.widget_in_toolbox_chosen_double_click = False
        # print(tk_widget_obj)

    # called when button in toolbox double clicked
    def toolbox_button_double_click_callback(self, _event, tk_widget_obj):
        self.pyted_core.deselect_selected_widget()
        self.widget_in_toolbox_chosen = tk_widget_obj
        self.widget_in_toolbox_chosen_double_click = True

    # called when var button in toolbox clicked
    def toolbox_var_button_click_callback(self, _event, tk_widget_obj):
        new_widget = tk_widget_obj()
        new_widget.name = self.widgets.generate_unique_name(new_widget)
        new_widget.parent = self.widgets.widget_list[0].name

        self.widgets.widget_list.append(new_widget)
        self.pyted_core.selected_widget = new_widget
        self.navigator_tree.build_navigator_tree()
        self.attr_frame.update(self.pyted_core.selected_widget)
        self.handles.remove_selected_widget_handles()
        # print(len(self.widgets))
        # self.deselect_selected_widget()
        self.widget_in_toolbox_chosen = None
        self.pyted_core.user_frame.after(300, lambda: self.widget_in_toolbox_chosen_tk_var.set('pointer'))

    # called when pointer button clicked in toolbox
    def toolbox_pointer_button_click(self, _event):
        self.widget_in_toolbox_chosen = None
        # print('toolbox pointer button clicked', event.x, event.y)
        # self.deselect_selected_widget()
