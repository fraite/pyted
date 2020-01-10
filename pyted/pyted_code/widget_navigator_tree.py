#
from __future__ import annotations
from typing import TYPE_CHECKING

import tkinter

import pyted.monet_widget_types as pyted_widget_types
if TYPE_CHECKING:
    from pyted.pyted_code.pyted_core import PytedCore


class NavigatorTree:
    """Widget attribute frame

    Frame that shows the widget attributes (including variables), and events. The frame additionally shows the row
    and column attributes of the parent.
    """

    def __init__(self, pyted_core: PytedCore):
        self.pyted_core = pyted_core
        self.widgets = pyted_core.widgets

        self.navigator_tree = pyted_core.pyted_window.navigator_tree
        self.navigator_tree.tag_bind('project', '<ButtonRelease-1>',
                                     self.navigator_tree_clicked)
        self.navigator_tree.tag_bind('toplevel', '<ButtonRelease-1>',
                                     self.navigator_tree_clicked)
        self.navigator_tree.tag_bind('var', '<ButtonRelease-1>',
                                     self.navigator_tree_clicked)
        self.navigator_tree.tag_bind('widget', '<ButtonRelease-1>',
                                     self.navigator_tree_clicked)

    # called when widget in navigation tree clicked
    def navigator_tree_clicked(self, _event):
        widget_toolbox = self.pyted_core.widget_toolbox
        widget_toolbox.widget_in_toolbox_chosen = None
        widget_toolbox.pointer_button.invoke()

        pyte_widget = None
        for pyte_widget in self.widgets.widget_list:
            if pyte_widget.name == self.navigator_tree.focus():
                break
        self.pyted_core.select_widget(pyte_widget)

    def build_navigator_tree(self) -> None:
        """
        Update navigator tree to show all widgets

        Clears the navigator tree and updates it with all widgets in the project as held in the list self.widgets.

        Note that the first widget in the list must be the TopLevel widget, but all the other widgets may be in any
        order.
        """
        # remove old items from navigator tree
        for i in self.navigator_tree.get_children():
            self.navigator_tree.delete(i)

        # put project widget as main branch
        widget = self.widgets.widget_list[0]
        self.navigator_tree.insert('', 'end', widget.name,
                                   text=widget.name, values='"' + repr(widget.type) + '"',
                                   tags='project')
        self.navigator_tree.item(widget.name, open=True)
        project_name = widget.name

        # put vars into tree
        for widget in self.widgets.widget_list:
            try:
                is_var = widget.is_var
            except AttributeError:
                is_var = False
            if is_var:
                self.navigator_tree.insert(project_name, 'end', widget.name,
                                           text=widget.name, values='"' + repr(widget.type) + '"',
                                           tags='var')

        # put widgets into tree
        widget = self.widgets.find_top_widget()
        self.navigator_tree.insert(self.widgets.widget_list[0].name, 'end', widget.name,
                                   text=widget.name, values='"' + repr(widget.type) + '"',
                                   tags='toplevel')
        self.navigator_tree.item(widget.name, open=True)
        self.build_navigator_tree_parent(widget)
        if self.pyted_core.selected_widget is not None:
            self.navigator_tree.focus(self.pyted_core.selected_widget.name)
            self.navigator_tree.selection_set(self.pyted_core.selected_widget.name)

    def build_navigator_tree_parent(self, parent: pyted_widget_types) -> None:
        """
        Adds items to the navigator tree with the parent specified

        Adds all widgets with the parent specified as items to the navigator tree. Container widgets are also added
        with the branch opened and the function called recursively to fill the tree.

        :param parent: parent of widgets to be added to navigator tree
        """
        for widget in self.widgets.widget_list:
            try:
                widget_type = widget.type
            except AttributeError:
                widget_type = None
            if not widget_type == tkinter.Toplevel:
                if widget.parent == parent.name:
                    self.navigator_tree.insert(widget.parent, 'end', widget.name,
                                               text=widget.name, values='"' + repr(widget.type) + '"',
                                               tags='widget')
                    # TODO: change the below to use container widget superclass
                    if isinstance(widget, pyted_widget_types.Frame) or isinstance(widget, pyted_widget_types.Notebook):
                        self.navigator_tree.item(widget.name, open=True)
                        self.build_navigator_tree_parent(widget)

    def navigator_tree_select_item(self):
        if self.pyted_core.selected_widget is not None:
            self.navigator_tree.focus(self.pyted_core.selected_widget.name)
            self.navigator_tree.selection_set(self.pyted_core.selected_widget.name)
            self.navigator_tree.see(self.pyted_core.selected_widget.name)

    def navigator_tree_change_item_name(self, pyte_widget, old_name):
        item_index = self.navigator_tree.index(old_name)
        item_parent = self.navigator_tree.parent(old_name)
        old_item_is_open = self.navigator_tree.item(old_name, 'open')
        # print(old_item_is_open)
        self.navigator_tree.insert(item_parent, item_index, pyte_widget.name,
                                   text=pyte_widget.name, values='"' + repr(pyte_widget.type) + '"',
                                   tags='widget')
        children = self.navigator_tree.get_children(old_name)
        for child in children:
            self.navigator_tree.move(child, pyte_widget.name, tkinter.END)
        self.navigator_tree.item(pyte_widget.name, open=old_item_is_open)
        self.navigator_tree.delete(old_name)
        if self.pyted_core.selected_widget is not None:
            self.navigator_tree.focus(self.pyted_core.selected_widget.name)
            self.navigator_tree.selection_set(self.pyted_core.selected_widget.name)
