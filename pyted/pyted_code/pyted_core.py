import tkinter
from tkinter import ttk
from typing import Union
from tkinter import filedialog, messagebox

import pyted.monet_widget_types as pyted_widget_types
import pyted.save_load_package.save_load as save_load
from pyted.pyted_code.widgets import Widgets
from pyted.pyted_window import PytedWindow
from pyted.pyted_code.widget_handles import Handles
from pyted.pyted_code.widget_attribute_frame import AttributeFrame
from pyted.pyted_code.widget_toolbox_notebook import WidgetToolboxNotebook
from pyted.pyted_code.widget_navigator_tree import NavigatorTree
from pyted.pyted_code.widget_user_form import UserForm

FILLER_TEXT = '        .        '
Pyted_Widget_Type = Union[pyted_widget_types.PytedWidget, pyted_widget_types.PytedGridContainerWidget,
                          pyted_widget_types.PytedPlacedWidget, None]
# update is_pyte_container if Pyte_Container_Type changed
Pyted_Container_Type = Union[pyted_widget_types.TopLevel, pyted_widget_types.Frame]


class PytedCore:
    """A tkinter GUI Editor"""

    def __init__(self):

        self.root_window = tkinter.Tk()

        self.widgets = Widgets()
        # self.widgets.widget_list = self.widgets.widget_list

        self.pyted_window = PytedWindow(self.root_window, self)
        self.background_user_frame = self.pyted_window.background_user_frame

        self.user_form = UserForm(self)
        parent_pyte_widget = self.user_form.draw_user_frame()

        self.selected_widget: Pyted_Widget_Type = None
        self.widget_in_toolbox_chosen = None

        self.handles = Handles(self.root_window)
        self.attr_frame = AttributeFrame(self)

        self.navigator_tree_obj = NavigatorTree(self)
        # TODO: remove navigator_tree by using a function to check for focus, then rename navigator_tree_obj
        self.navigator_tree = self.navigator_tree_obj.navigator_tree

        self.widget_toolbox: WidgetToolboxNotebook = WidgetToolboxNotebook(self)

        self.navigator_tree_obj.build_navigator_tree()
        self.select_widget(parent_pyte_widget)
        self.user_form.draw_user_frame()

        self.handles.place_selected_widget_handles(self.user_form.user_frame)

        self.root_window.mainloop()
        # self.toolbox = None

    def update_widget_attribute(self, pyte_widget: Pyted_Widget_Type, attr: str,
                                new_value: Union[str, bool],
                                init=False) -> Union[None, tuple]:
        """Update a widget attribute with a new value

        The attribute of a widget (both the pyte widget and the associated tk_widget) is changed to the specified new
        value. Under some conditions (for example renaming a widget name to a name that already exists for another
        widget) the attribute will not be changed and a user message generated. Where the location (row or column) is
        changed to an invalid location (for example off the grid) then the widget will be hidden and a user message
        generated.

        When this method is called during initialisation, some of the functionality is not required and this can be
        turned off by setting init to False.

        :param pyte_widget: pyte widget that is to have an attribute changed
        :param attr: attribute to be changed
        :param new_value: new value of the attribute
        :param init: called during initialisation so some functionality not required
        :return:
        :rtype: object
        """

        old_value = getattr(pyte_widget, attr)

        if not init:
            setattr(pyte_widget, attr, new_value)

        try:
            tk_widget = pyte_widget.tk_name
        except AttributeError:
            tk_widget = None

        attr_template = pyte_widget.get_code_template(attr)

        if attr_template == pyted_widget_types.CONFIG_CODE:
            tk_widget[attr] = getattr(pyte_widget, attr)

        elif attr_template == pyted_widget_types.TITLE_CODE:
            return

        elif attr_template == pyted_widget_types.GRID_CODE:
            if init:
                # when user form is drawn grid placement will be handled by user form initialisation code
                return
            try:
                old_position = {'row': tk_widget.grid_info()['row'], 'column': tk_widget.grid_info()['column']}
                new_position = {'row': tk_widget.grid_info()['row'], 'column': tk_widget.grid_info()['column']}
            except KeyError:
                # widget has remove set true so no need to update tk_widget
                return
            new_attr_val = getattr(pyte_widget, attr)
            new_position[attr] = new_attr_val
            if (int(new_position['row']) >= int(self.widgets.find_pyte_parent(pyte_widget).number_rows) or
                    int(new_position['column']) >= int(self.widgets.find_pyte_parent(pyte_widget).number_columns)):
                # pyte_widget.row = old_position['row']
                # pyte_widget.column = old_position['column']
                pyte_widget.remove = True
                pyte_widget.tk_name.grid_remove()
                self.handles.remove_selected_widget_handles()
                self.user_form.new_filler_label(self.widgets.find_tk_parent(pyte_widget),
                                                old_position['column'], old_position['row'])
                messagebox.showwarning('Widget being moved off grid',
                                       'Row or column greater than grid size. Widget has been removed. '
                                       'To get widget back move back onto grid and set remove to false')
            else:

                filler_widget = self.widgets.find_tk_parent(pyte_widget).grid_slaves(row=new_position['row'],
                                                                                     column=new_position['column'])[0]
                if filler_widget not in self.user_form.filler_labels and filler_widget != pyte_widget.tk_name:
                    # trying to move widget onto existing widget
                    pyte_widget.remove = True
                    pyte_widget.tk_name.grid_remove()
                    self.handles.remove_selected_widget_handles()
                    self.user_form.new_filler_label(self.widgets.find_tk_parent(pyte_widget),
                                                    old_position['column'], old_position['row'])
                    messagebox.showwarning('Widget being moved onto existing widget',
                                           'Row and column the same as another widget. Widget has been removed. '
                                           'To get widget back move back onto empty slot and set remove to false')
                    return
                filler_widget.grid(row=old_position['row'], column=old_position['column'])
                tk_widget.grid({attr: new_attr_val})
                self.handles.place_selected_widget_handles(pyte_widget.tk_name)

        elif attr_template == pyted_widget_types.GRID_SIZE_CODE:
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            self.user_form.empty_tk_container_widget(pyte_widget)
            self.user_form.fill_tk_container_frame(pyte_widget)
            self.handles.place_selected_widget_handles(pyte_widget.tk_name)

        elif attr_template == pyted_widget_types.ROW_CONFIGURE or attr_template == pyted_widget_types.COLUMN_CONFIGURE:
            # row and column configuration handled elsewhere in program
            pass

        elif attr_template == pyted_widget_types.BESPOKE_CODE and attr == 'remove':
            if init:
                # when user form is drawn grid_remove will be handled by user form initialisation code
                return

            tk_widget_in_grid = not(len(pyte_widget.tk_name.grid_info()) == 0)
            if getattr(pyte_widget, 'remove'):
                if tk_widget_in_grid:
                    widget_to_hide = pyte_widget
                    self.user_form.new_filler_label(self.widgets.find_tk_parent(widget_to_hide), widget_to_hide.column,
                                                    widget_to_hide.row)
                    widget_to_hide.tk_name.grid_remove()
                    self.handles.remove_selected_widget_handles()
            else:
                # remove attribute is false, if widget not displayed then try to display it
                if not tk_widget_in_grid:
                    # check that the widget is on the grid
                    if (int(pyte_widget.row) >= int(self.widgets.find_pyte_parent(pyte_widget).number_rows) or
                            int(pyte_widget.column) >= int(self.widgets.find_pyte_parent(pyte_widget).number_columns)):
                        messagebox.showwarning('Widget off grid',
                                               'Row or column greater than grid size. '
                                               'To get widget back move back onto grid and set remove to false')
                        setattr(pyte_widget, 'remove', True)
                        return
                    # check that there is not a widget already visible
                    filler_widget = self.widgets.find_tk_parent(pyte_widget).grid_slaves(row=pyte_widget.row,
                                                                                         column=pyte_widget.column)[0]
                    if filler_widget not in self.user_form.filler_labels:
                        pyte_widget.remove = True
                        pyte_widget.tk_name.grid_remove()
                        # self.remove_selected_widget_handles()
                        messagebox.showwarning('Existing widget at grid location',
                                               'Row and column the same as another widget. '
                                               'To get widget back move onto empty slot and set remove to false')
                        return
                    # remove filler label and show user widget
                    filler_widget = self.widgets.find_tk_parent(pyte_widget).grid_slaves(row=pyte_widget.row,
                                                                                         column=pyte_widget.column)[0]
                    filler_widget.grid_forget()
                    filler_widget.destroy()
                    pyte_widget.tk_name.grid(row=pyte_widget.row, column=pyte_widget.column)
                    self.handles.place_selected_widget_handles(pyte_widget.tk_name)

        elif attr_template == pyted_widget_types.BESPOKE_CODE and attr == 'name':
            if init:
                # when user form is drawn the widget name will be handled by user form initialisation code
                return
            # check name is really changed
            if new_value == old_value:
                return
            # check name is not already taken
            for i_pyte_widget in self.widgets.widget_list:
                if i_pyte_widget != pyte_widget:
                    if pyte_widget.name == i_pyte_widget.name:
                        # can't messagebox here as this would move focus out of entry box and cause binding to run again
                        # messagebox.showwarning('Renaming problem',
                        #                        'Name already exists for another widget and Name not changed')
                        setattr(pyte_widget, attr, old_value)
                        return 'Renaming problem', 'Name already exists for another widget and Name not changed'
            for i_pyte_widget in self.widgets.widget_list:
                if i_pyte_widget.parent == old_value:
                    i_pyte_widget.parent = new_value
            # self.update_navigator_tree()
            self.navigator_tree_obj.navigator_tree_change_item_name(pyte_widget, old_value)
            # raise Exception(f'renaming widget not yet implemented')

        elif attr_template == pyted_widget_types.BESPOKE_CODE and (attr == 'comment'):
            if init:
                # when user form is drawn the tk_name will be handled by user form initialisation code
                return
            return

        elif attr_template == pyted_widget_types.BESPOKE_CODE and (attr == 'tab_text'):
            if init:
                # when user form is drawn the tk_name will be handled by user form initialisation code
                return
            tk_parent = self.widgets.find_tk_parent(pyte_widget)
            if isinstance(tk_parent, ttk.Notebook):
                tk_parent.tab(pyte_widget.tk_name, text=new_value)
            # self.widgets.find_tk_parent(pyte_widget).tab(pyte_widget.tk_name, text=new_value)
            return

        elif attr_template == pyted_widget_types.BESPOKE_CODE and attr == 'tk_name':
            if init:
                # when user form is drawn the tk_name will be handled by user form initialisation code
                return
            raise Exception(f'renaming tk_name for widget should not occur')

        elif attr_template == pyted_widget_types.BESPOKE_CODE and attr == 'parent':
            # not used as parent attribute not shown in attribute edit frame
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            raise Exception(f'renaming widget parent not yet implemented')

        elif attr_template == pyted_widget_types.VAR_SET_CODE:
            setattr(pyte_widget, pyted_widget_types.VAR_SET_CODE, new_value)

        elif attr_template.startswith('<'):
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            return

        else:
            raise Exception(f'attr_template "{attr_template}" for "{attr}" not yet configured')
            # print(f'attr_template {attr_template} not yet implemented for {attr}')

    def widget_move(self, event):
        # called when a (not filler) widget in user form is attempted to be moved
        if self.widget_in_toolbox_chosen is None and self.selected_widget is not None:
            # mouse pointer mode chosen from widget toolbox
            self.user_form.widget_to_deselect_if_not_moved = None
            if isinstance(self.selected_widget, pyted_widget_types.TopLevel):
                return
            frame, grid_location = self.user_form.find_grid_location(self.widgets.find_top_widget(), event.x_root,
                                                                     event.y_root)
            if self.selected_widget.type == tkinter.Toplevel:
                selected_widget_current_row = None
                selected_widget_current_column = None
                selected_widget_current_frame = None
            else:
                selected_widget_current_row = self.selected_widget.row
                selected_widget_current_column = self.selected_widget.column
                selected_widget_current_frame = self.widgets.find_pyte_parent(self.selected_widget)
            if (selected_widget_current_column == grid_location[0] and
                selected_widget_current_row == grid_location[1] and
                    selected_widget_current_frame == frame):
                # pointer has not moved from current location so no need to try to move the widget
                return
            if grid_location[0] < 0 or grid_location[1] < 0:
                # grid location is off the edge of the grid so do nothing
                widget_under_mouse = None
            else:
                widget_under_mouse = frame.tk_name.grid_slaves(column=grid_location[0], row=grid_location[1])[0]
            if frame == self.selected_widget:
                # selected widget is the frame and just moving inside frame so do nothing
                widget_under_mouse = None
            elif frame.type != tkinter.Toplevel:
                # check that selected frame is not parent of the frame that we are moving into
                pyte_parent = self.widgets.find_pyte_parent(frame)
                while pyte_parent.type != tkinter.Toplevel:
                    if pyte_parent == self.selected_widget:
                        # trying to move a container into it's child
                        widget_under_mouse = None
                        break
                    pyte_parent = self.widgets.find_pyte_parent(pyte_parent)

            if isinstance(self.selected_widget, pyted_widget_types.PanedWindow):
                # stop PanedWindow from resizing by stopping any further bindings being activated
                return 'break'

            if (isinstance(frame, pyted_widget_types.Notebook) and
                    isinstance(self.selected_widget, pyted_widget_types.Frame)):
                # add tab to Notebook
                self.user_form.new_filler_label(selected_widget_current_frame.tk_name,
                                                selected_widget_current_column,
                                                selected_widget_current_row)
                if getattr(self.selected_widget, 'tab_text') is None:
                    setattr(self.selected_widget, 'tab_text', 'tab text')
                tab_text = getattr(self.selected_widget, 'tab_text')
                self.selected_widget.tk_name.destroy()
                clone = self.user_form.place_pyte_widget(self.selected_widget, tk_frame=frame.tk_name)
                self.user_form.fill_tk_container_frame(self.selected_widget)
                frame.tk_name.add(clone, text=tab_text)
                frame.tk_name.select(clone)
                self.selected_widget.parent = frame.name
                self.attr_frame.update(self.selected_widget)
                self.navigator_tree_obj.build_navigator_tree()
                self.handles.place_selected_widget_handles(clone)

            elif widget_under_mouse in self.user_form.filler_labels:
                selected_widget_parent = self.widgets.find_pyte_parent(self.selected_widget)
                paned_window_parent_forgotten = self.user_form.forget_paned_window_parent(widget_under_mouse)
                if (isinstance(self.selected_widget, pyted_widget_types.Frame) and
                        isinstance(selected_widget_parent, pyted_widget_types.Notebook)):
                    # remove tab from Notebook (if there is more than one)
                    if selected_widget_parent.tk_name.index('end') > 1:
                        selected_widget_parent.tk_name.forget(str(self.selected_widget.tk_name))
                    else:
                        return
                else:
                    # put a new filler label at the old position where the widget was
                    self.user_form. new_filler_label(selected_widget_current_frame.tk_name,
                                                     selected_widget_current_column,
                                                     selected_widget_current_row)
                # remove filler label from where the widget will move to
                self.user_form.filler_labels.remove(widget_under_mouse)
                widget_under_mouse.destroy()
                # move tk_widget, note have to destroy and re-create as you can not move tk_widgets between frames
                self.selected_widget.tk_name.destroy()
                clone = self.user_form.place_pyte_widget(self.selected_widget, tk_frame=frame.tk_name,
                                                         column=grid_location[0], row=grid_location[1])
                if isinstance(self.selected_widget, pyted_widget_types.Frame):
                    self.user_form.fill_tk_container_frame(self.selected_widget)
                if isinstance(self.selected_widget, pyted_widget_types.Notebook):
                    # TODO: implement notebook move
                    self.user_form.fill_ttk_notebook(self.selected_widget)
                # self.selected_widget.tk_name.grid(column=grid_location[0], row=grid_location[1])
                if selected_widget_current_frame != frame:
                    widget_changed_frame = True
                else:
                    widget_changed_frame = False
                self.selected_widget.parent = frame.name
                self.selected_widget.column = grid_location[0]
                self.selected_widget.row = grid_location[1]
                self.attr_frame.update(self.selected_widget)
                if widget_changed_frame:
                    self.navigator_tree_obj.build_navigator_tree()
                # print('end move widget')

                # resize paned window if a widget has been moved into the pane
                parent_widget = self.selected_widget.tk_name
                while parent_widget is not None:
                    parent_widget = parent_widget.master
                    if isinstance(parent_widget, tkinter.PanedWindow):
                        self.user_form.resize_paned_window(parent_widget)

                # resize paned window if a widget has been moved out of the pane
                if selected_widget_current_frame is not None:
                    parent_widget = selected_widget_current_frame.tk_name
                else:
                    parent_widget = None
                while parent_widget is not None:
                    parent_widget = parent_widget.master
                    if isinstance(parent_widget, tkinter.PanedWindow):
                        self.user_form.resize_paned_window(parent_widget)

                self.handles.place_selected_widget_handles(clone)

    def select_widget(self, new_selected_pyte_widget) -> None:
        self.selected_widget = new_selected_pyte_widget

        # place widget handles if required
        remove_or_parent_remove = True
        is_widget = (isinstance(new_selected_pyte_widget, pyted_widget_types.PytedPlacedWidget) or
                     isinstance(new_selected_pyte_widget, pyted_widget_types.TopLevel))
        if is_widget:
            # check to see if widget attribute "remove" is True (or the parent of the widget)
            remove_or_parent_remove = False
            widget_to_check = new_selected_pyte_widget
            while not widget_to_check.type == tkinter.Toplevel:
                try:
                    remove = widget_to_check.remove
                except AttributeError:
                    remove = False
                if remove:
                    remove_or_parent_remove = True
                    break
                widget_to_check = self.widgets.find_pyte_widget_from_m_name(widget_to_check.parent)

        # if new_selected_pyte_widget is in a Notebook then select frame
        p_parent_widget = new_selected_pyte_widget
        # if parent is
        while not isinstance(p_parent_widget, pyted_widget_types.TopLevel) and p_parent_widget is not None:
            p_frame_widget = p_parent_widget
            p_parent_widget = self.widgets.find_pyte_parent(p_frame_widget)
            if isinstance(p_parent_widget, pyted_widget_types.Notebook):
                p_parent_widget.tk_name.select(str(p_frame_widget.tk_name))

        if remove_or_parent_remove:
            self.handles.remove_selected_widget_handles()
        else:
            self.handles.place_selected_widget_handles(self.selected_widget.tk_name)

        # fill out attribute tree, and attribute entry box

        self.attr_frame.update(self.selected_widget)
        # self.update_navigator_tree()
        self.navigator_tree_obj.navigator_tree_select_item()

    def deselect_selected_widget(self) -> None:
        """
        Deselect the selected widget

        Clears the attribute tree, removes the selection frame around the selected widget and sets self.selected_widget
        to None.
        """
        if self.selected_widget is not None:
            self.handles.remove_selected_widget_handles()
            self.selected_widget = None
            self.attr_frame.update(self.selected_widget)

    def escape_key_callback(self, _event):
        self.widget_in_toolbox_chosen = None
        self.widget_toolbox.widget_in_toolbox_chosen_double_click = False
        self.widget_toolbox.pointer_button.invoke()
        if self.user_form.proposed_widget is not None and self.user_form.proposed_widget_location is not None:
            self.user_form.new_filler_label(self.user_form.proposed_widget_frame.tk_name,
                                            self.user_form.proposed_widget_location[0],
                                            self.user_form.proposed_widget_location[1])
            self.user_form.proposed_widget.destroy()
            self.user_form.proposed_widget_frame = None
            self.user_form.proposed_widget_location = None

    def delete_key_callback(self, _event):
        if self.selected_widget is not None:
            # check that focus is not in edit attributes, in which case should not delete widget
            enable_delete = False
            if isinstance(self.root_window.focus_get(), tkinter.Radiobutton):
                enable_delete = True
            if isinstance(self.root_window.focus_get(), ttk.Notebook):
                enable_delete = True
            if isinstance(self.root_window.focus_get(), tkinter.ttk.Button):
                # print(self.root_window.focus_get().cget('text'))
                if self.root_window.focus_get().cget('text') == 'pointer':
                    enable_delete = True
            if self.root_window.focus_get() == self.navigator_tree:
                enable_delete = True
            if enable_delete:
                if not isinstance(self.selected_widget, pyted_widget_types.TopLevel):
                    self.delete_selected_widget()
                    self.selected_widget = None
                    self.attr_frame.update(self.selected_widget)

    def delete_selected_widget(self):
        # print('delete widget at ', self.selected_widget.column, self.selected_widget.row)
        widget_to_delete = self.selected_widget
        self.deselect_selected_widget()
        self.user_form.new_filler_label(self.widgets.find_tk_parent(widget_to_delete), widget_to_delete.column,
                                        widget_to_delete.row)
        widget_to_delete.tk_name.destroy()
        self.widgets.widget_list.remove(widget_to_delete)
        self.navigator_tree_obj.build_navigator_tree()

    def insert_widget(self, new_widget, proposed_widget, proposed_widget_frame, proposed_widget_location):
        # new_widget = self.widget_in_toolbox_chosen()
        new_widget.parent = proposed_widget_frame.name
        new_widget.column = proposed_widget_location[0]
        new_widget.row = proposed_widget_location[1]
        new_widget.tk_name = proposed_widget
        new_widget.name = self.widgets.generate_unique_name(new_widget)
        if hasattr(new_widget, 'text'):
            if hasattr(new_widget, 'value'):
                new_widget.text = new_widget.name
                new_widget.value = new_widget.name
            else:
                new_widget.text = new_widget.name
        new_widget.tk_name.bind('<Motion>', self.user_form.user_motion_callback)
        new_widget.tk_name.bind("<B1-Motion>", self.widget_move)
        new_widget.tk_name.bind("<Button-1>", lambda
                                w_event, arg1=new_widget:
                                self.user_form.widget_click(w_event, arg1)
                                )
        new_widget.tk_name.bind("<ButtonRelease-1>", self.user_form.widget_release)

        if isinstance(new_widget, pyted_widget_types.Frame):
            new_widget.number_columns = pyted_widget_types.Frame.number_columns
            new_widget.number_rows = pyted_widget_types.Frame.number_rows
            # replace binding for filler labels from proposed container filler labels to an inserted container type
            for filler_label in proposed_widget.grid_slaves():
                filler_label.bind("<Motion>", self.user_form.user_motion_callback)
                filler_label.bind("<Button-1>", lambda
                                  event, arg1=new_widget:
                                  self.user_form.widget_click(event, arg1)
                                  )
                filler_label.bind("<ButtonRelease-1>", self.user_form.widget_release)
            if isinstance(self.widgets.find_pyte_parent(new_widget), pyted_widget_types.Notebook):
                setattr(new_widget, 'tab_text', 'tab text')

        self.widgets.widget_list.append(new_widget)
        self.navigator_tree_obj.build_navigator_tree()
        # self.select_widget(new_widget)

        if isinstance(new_widget, pyted_widget_types.Notebook):
            child_frame_widget = pyted_widget_types.Frame()
            child_frame_widget.parent = new_widget
            self.insert_widget(child_frame_widget, self.user_form.proposed_widget_tab, new_widget, [0, 0])

        if isinstance(new_widget, pyted_widget_types.PanedWindow):
            child_frame_widget = pyted_widget_types.Frame()
            child_frame_widget.parent = new_widget
            self.insert_widget(child_frame_widget, self.user_form.proposed_widget_tab, new_widget, [0, 0])
            child_frame_widget = pyted_widget_types.Frame()
            child_frame_widget.parent = new_widget
            self.insert_widget(child_frame_widget, self.user_form.proposed_widget_tab2, new_widget, [0, 0])

        self.user_form.proposed_widget_frame = None
        self.user_form.proposed_widget_location = None
        self.user_form.proposed_widget = None

        if not self.widget_toolbox.widget_in_toolbox_chosen_double_click:
            self.widget_in_toolbox_chosen = None
            self.user_form.user_frame.after(30,
                                            lambda: self.widget_toolbox.widget_in_toolbox_chosen_tk_var.set('pointer'))
        self.select_widget(new_widget)
        # by return "break" we stop further event handling, which stops the inserted widget being active
        # return "break"

    def menu_file_save(self):
        root = self.root_window
        root.filename = filedialog.asksaveasfilename(title="Select file", defaultextension=".py",
                                                     filetypes=(("python files", "*.py"), ("all files", "*.*")))
        if not root.filename == '':
            code = save_load.generate_code(self.widgets)
            with open(root.filename, 'w') as f:
                f.write(code)
        else:
            # no cancel pressed
            pass

    def menu_file_load(self):
        root = self.root_window
        root.filename = filedialog.askopenfilename(initialfile='ddd.py', title="Select file",
                                                   filetypes=(("python files", "*.py"), ("all files", "*.*")))
        if not root.filename == '':
            with open(root.filename) as f:
                self.widgets.widget_list = save_load.parse_code(f)
                parent_pyte_widget = self.user_form.draw_user_frame()
                self.selected_widget = parent_pyte_widget
                self.navigator_tree_obj.build_navigator_tree()
                self.select_widget(parent_pyte_widget)
        else:
            # no cancel pressed
            pass

    def menu_preview(self):
        code = save_load.generate_code(self.widgets)
        name_space = {}
        exec(code, name_space)
        gui_class = name_space['GuiCollection']
        # gui = gui_class()
        gui_class()
