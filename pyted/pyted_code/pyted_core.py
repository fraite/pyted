import tkinter
from tkinter import ttk
from typing import Union
from tkinter import filedialog, messagebox

import pyted.pyted_widget_types as pyted_widget_types
import pyted.save_load_package.save_load as save_load
from pyted.pyted_code.widgets import Widgets
from pyted.pyted_window import PytedWindow
from pyted.pyted_code.widget_handles import Handles
from pyted.pyted_code.widget_attribute_frame import AttributeFrame
from pyted.pyted_code.widget_toolbox_notebook import WidgetToolboxNotebook
from pyted.pyted_code.widget_navigator_tree import NavigatorTree

FILLER_TEXT = '        .        '
Pyted_Widget_Type = Union[pyted_widget_types.Project, pyted_widget_types.StringVar,
                          pyted_widget_types.TopLevel, pyted_widget_types.Label, pyted_widget_types.Entry,
                          pyted_widget_types.Frame, pyted_widget_types.Button, pyted_widget_types.Checkbutton]
# update is_pyte_container if Pyte_Container_Type changed
Pyted_Container_Type = Union[pyted_widget_types.TopLevel, pyted_widget_types.Frame]


class PytedCore:
    """A tkinter GUI Editor"""

    def __init__(self):

        self.root_window = tkinter.Tk()

        self.filler_labels = []
        self.widget_to_deselect_if_not_moved = None
        self.selected_widget = None
        self.proposed_widget = None
        self.proposed_widget_frame = None
        self.proposed_widget_location = None
        self.proposed_widget_tab = None
        self.selection_frame = None
        self.mouse_button1_pressed = False
        self.attr_input_method = tkinter.Entry

        # set up test user form
        #
        # TODO: change references self.widget
        self.widgets = Widgets()
        # self.widgets.widget_list = self.widgets.widget_list

        # set up window
        self.pyted_window = PytedWindow(self.root_window, self)
        self.background_user_frame = self.pyted_window.background_user_frame
        self.user_frame = self.pyted_window.user_frame
        # self.ttk_toolbox_frame = pyted_window.ttk_toolbox_frame

        self.handles = Handles(self.root_window)
        self.attr_frame = AttributeFrame(self)


        parent_pyte_widget = self.draw_user_frame()

        self.navigator_tree_class = NavigatorTree(self)
        self.navigator_tree = self.navigator_tree_class.navigator_tree

        self.widget_toolbox: WidgetToolboxNotebook = WidgetToolboxNotebook(self)

        self.navigator_tree_class.build_navigator_tree()
        self.select_widget(parent_pyte_widget)
        self.draw_user_frame()
        self.handles.place_selected_widget_handles(self.user_frame)

        self.root_window.mainloop()
        # self.toolbox = None

    def draw_user_frame(self):
        # set up inside of User Frame
        #

        # Find top level widget, assign tk_name to user_frame, and get name
        pyte_widget = self.widgets.find_top_widget()
        if self.user_frame is not None:
            self.user_frame.destroy()
        self.user_frame = ttk.Frame(self.background_user_frame)
        self.user_frame.bind("<Motion>", self.user_motion_callback)
        self.user_frame.bind("<Button-1>", self.empty_label_click_callback)
        self.user_frame.bind("<ButtonRelease-1>", self.widget_release)
        self.user_frame.bind('<Leave>', self.user_frame_leave_callback)
        self.user_frame.grid(row=0, column=0)
        pyte_widget.tk_name = self.user_frame

        # Create and fill Frames with filler labels
        # first create containers before placing non-container widgets
        self.fill_tk_container_widget(pyte_widget)

        return pyte_widget

    def new_filler_label(self, container: tkinter.Widget, column: int, row: int) -> None:
        """
        Create and place a new filler label

        Creates a new filler label in the given frame (or TopLevel) at the given column or row and adds it to the list
        of filler labels.

        :param container: pointer to tk container
        :param column: column for new filler label
        :param row: row for new filler label
        :return:
        """
        new_label = ttk.Label(container, text=FILLER_TEXT)
        new_label.grid(row=row, column=column)
        new_label.bind("<Motion>", self.user_motion_callback)
        # new_label.bind("<Button-1>", self.empty_label_click_callback)
        new_label.bind("<Button-1>", lambda
                       event, arg1=self.widgets.find_pyte_widget_from_tk(container):
                       self.widget_click(event, arg1)
                       )
        new_label.bind("<ButtonRelease-1>", self.widget_release)
        self.filler_labels.append(new_label)

    def place_pyte_widget(self, pyte_widget: Pyted_Widget_Type, tk_frame=None, column=None, row=None) -> tkinter.Widget:
        """
        Create a tk_widget and places in a container

        Creates a tk_widget from a pyte_widget and places it into a container. The widget may be a container but if it
        is a container the widgets inside the container will not be placed. There must be a filler_widget already at
        the location and this is removed.

        The pyte_widget is by default placed in the frame defined by the pyte_widget and in the column, row defined in
        the pyte_widget. It is possible to instead define where the widget is placed, for example when the user is
        moving the widget.

        :param pyte_widget: pyte widget to be placed onto the user form
        :param tk_frame: frame to place widget on, if none specified then use parent widget defined in pyte_widget
        :param row: row in parent widget, if none specified then row defined in pyte_widget
        :param column: column in parent widget, if none specified then column defined in pyte_widget
        :return:
        """

        # work out parent_tk_frame
        if tk_frame is None:
            parent_tk_widget = self.widgets.find_tk_parent(pyte_widget)
        else:
            parent_tk_widget = tk_frame
        if parent_tk_widget is None:
            raise Exception('widget in project missing parent')
        # work out row and column
        if column is None:
            tk_column = pyte_widget.column
        else:
            tk_column = column
        if row is None:
            tk_row = pyte_widget.row
        else:
            tk_row = row

        # remove filler label
        if not parent_tk_widget.grid_slaves(row=tk_row, column=tk_column) == []:
            filler_widget = parent_tk_widget.grid_slaves(row=tk_row, column=tk_column)[0]
            filler_widget.grid_forget()
            self.filler_labels.remove(filler_widget)
            filler_widget.destroy()
        tk_new_widget = self.new_tk_widget(pyte_widget, parent_tk_widget)
        tk_new_widget.grid(row=tk_row, column=tk_column, sticky=pyte_widget.sticky)
        try:
            remove = pyte_widget.remove
        except AttributeError:
            remove = False
        if remove:
            tk_new_widget.grid_remove()
            self.new_filler_label(parent_tk_widget, row=tk_row, column=tk_column)

        return tk_new_widget

    def new_tk_widget(self, pyte_widget: Pyted_Widget_Type, tk_parent=None) -> tkinter.Widget:
        """
        Create a tk_widget from a pyte widget. Normally the tk_widget will have the parent as specified in the
        pyte_widget but this can be over-ridden for example if the tk_widget is going to be put into a selection_frame.

        :param pyte_widget:
        :param tk_parent: tk_container to put widget in, if none then take parent from pyte_widget
        :return:
        """
        if tk_parent is None:
            parent_id = self.widgets.find_tk_parent(pyte_widget)
        else:
            parent_id = tk_parent
        if parent_id is None:
            raise Exception('widget in project missing parent')
        new_w_class = pyte_widget.type
        tk_new_widget = new_w_class(parent_id)
        pyte_widget.tk_name = tk_new_widget
        for k, v in vars(pyte_widget).items():
            self.update_widget_attribute(pyte_widget, k, '', init=True)

        if isinstance(pyte_widget, pyted_widget_types.Frame):
            tk_new_widget.bind("<Motion>", self.user_motion_callback)
            # tk_new_widget.bind("<Button-1>", self.empty_label_click_callback)
            tk_new_widget.bind("<Button-1>", lambda
                               event, arg1=pyte_widget:
                               self.widget_click(event, arg1)
                               )
            tk_new_widget.bind("<ButtonRelease-1>", self.widget_release)
        else:
            tk_new_widget.bind('<Motion>', self.user_motion_callback)
            # tk_new_widget.bind("<B1-Motion>", self.widget_move)
            tk_new_widget.bind("<Button-1>", lambda
                               event, arg1=pyte_widget:
                               self.widget_click(event, arg1)
                               )
            tk_new_widget.bind("<ButtonRelease-1>", self.widget_release)
        return tk_new_widget

    def fill_tk_container_widget(self, parent_pyte_widget: pyted_widget_types.PytedGridContainerWidget) -> None:
        """
        Fill a tk container widget

        Fills a tk container widget corresponding to a pyte_widget. The container widget is filled with (blank) label
        widgets or widgets corresponding to pyte widgets. Where there are child container widgets, these are filled out
        recursively.

        :param parent_pyte_widget: pyte container
        :return:
        """

        for i_col in range(int(parent_pyte_widget.number_columns)):
            for i_row in range(int(parent_pyte_widget.number_rows)):
                self.new_filler_label(parent_pyte_widget.tk_name, i_col, i_row)

        for pyte_widget in self.widgets.widget_list:
            if pyte_widget.parent == parent_pyte_widget.name:
                if (int(pyte_widget.column) >= int(parent_pyte_widget.number_columns) or
                        int(pyte_widget.row) >= int(parent_pyte_widget.number_rows)):
                    pyte_widget.remove = True
                elif isinstance(pyte_widget, pyted_widget_types.Frame):
                    self.place_pyte_widget(pyte_widget)
                    self.fill_tk_container_widget(pyte_widget)
                else:
                    self.place_pyte_widget(pyte_widget)

    def empty_tk_container_widget(self, parent_pyte_widget: pyted_widget_types.PytedGridContainerWidget) -> None:
        """
        Empty a tk container widget

        Empty a tk container widget corresponding to the pyte_widget of child widgets. All the label widgets in the
        container are removed (including from filler_labels list). tk widgets corresponding to pyte widgets are removed
        but the pyte widget remains in the widgets list. Where there are child container widgets, these are emptied
        recursively.

        :param parent_pyte_widget: pyte container
        :return:
        """

        for child_widget in parent_pyte_widget.tk_name.grid_slaves():
            if child_widget in self.filler_labels:
                self.filler_labels.remove(child_widget)
            elif isinstance(self.widgets.get_pyte_widget(child_widget), pyted_widget_types.Frame):
                self.empty_tk_container_widget(self.widgets.get_pyte_widget(child_widget))
            child_widget.destroy()

    def user_motion_callback(self, event):
        """
        Call back method when mouse is moved in user frame, either in blank space, filler label or widget

        If no specific widget is chosen in the widget toolbox (in other words the pointer is chosen in the toolbox) and
        the mouse button 1 is pressed and a widget is selected then move the selected widget.

        If a widget is chosen in the widget toolbox a check is made to see if the location of the mouse is
        different to the existing proposed widget to insert (including if no proposed widget exists). If the mouse is
        in a different location then insert new proposed widget.

        :param event: the tkinter event object
        :return: None
        """
        if self.widget_toolbox.widget_in_toolbox_chosen is None:
            # print('<<<<', self.selected_widget.name, self.mouse_button1_pressed)
            if self.selected_widget is not None and self.mouse_button1_pressed:
                # selection widget chosen so may need to move widget
                self.widget_move(event)
        else:
            # toolbox widget chosen so may need to insert proposed widget into user_frame
            frame, grid_location = self.find_grid_location(self.widgets.find_top_widget(), event.x_root, event.y_root)
            # if self.proposed_widget_frame is not None:
            #     print('user motion-toolbox chosen', 'mouse location:', frame.name, grid_location,
            #           'proposed_widget_location', self.proposed_widget_frame.name, self.proposed_widget_location)
            # else:
            #     print('self.proposed_widget_frame is None')
            # add inserted widget if does not exist and valid to do so

            old_proposed_widget = self.proposed_widget
            old_proposed_widget_frame = self.proposed_widget_frame
            old_proposed_widget_location = self.proposed_widget_location

            # insert new frame into a notebook?
            if isinstance(frame, pyted_widget_types.Notebook) and isinstance(self.proposed_widget, tkinter.Frame):
                if self.proposed_widget_frame != frame:
                    self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name)
                    self.proposed_widget_frame = frame
                    self.proposed_widget_location = [0, 0]
                    number_columns = self.widget_toolbox.widget_in_toolbox_chosen.number_columns
                    number_rows = self.widget_toolbox.widget_in_toolbox_chosen.number_rows
                    self.proposed_widget['borderwidth'] = 2
                    self.proposed_widget['relief'] = tkinter.GROOVE
                    # tk_widget[attr] = getattr(pyte_widget, attr)
                    for i_column in range(number_columns):
                        for i_row in range(number_rows):
                            # self.new_filler_label(self.proposed_widget, i_column, i_row)
                            new_label = ttk.Label(self.proposed_widget, text=FILLER_TEXT)
                            new_label.grid(row=i_row, column=i_column)
                            new_label.bind("<Motion>", self.user_motion_callback)
                            new_label.bind("<Button-1>", self.inserted_widget_click)
                            # new_label.bind("<ButtonRelease-1>", self.widget_release)
                            self.filler_labels.append(new_label)
                    # self.proposed_widget.grid(column=grid_location[0], row=grid_location[1])
                    frame.tk_name.add(self.proposed_widget)
                    frame.tk_name.select(self.proposed_widget)
                    self.proposed_widget.bind('<Motion>', self.user_motion_callback)
                    self.proposed_widget.bind('<Button-1>', self.inserted_widget_click)

            # insert a widget if there is a label widget
            elif self.proposed_widget_location != grid_location or self.proposed_widget_frame != frame:
                if grid_location[0] >= 0 and grid_location[1] >= 0:
                    try:
                        widget_under_mouse = frame.tk_name.grid_slaves(row=grid_location[1],
                                                                       column=grid_location[0])[0]
                    except IndexError:
                        widget_under_mouse = None
                else:
                    widget_under_mouse = None
                # widget is under mouse unless mouse is not in the user_frame area
                if widget_under_mouse is not None:
                    if widget_under_mouse in self.filler_labels:
                        self.proposed_widget_frame = frame
                        self.proposed_widget_location = grid_location
                        if self.widget_toolbox.widget_in_toolbox_chosen is pyted_widget_types.Frame:
                            self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name)
                            number_columns = self.widget_toolbox.widget_in_toolbox_chosen.number_columns
                            number_rows = self.widget_toolbox.widget_in_toolbox_chosen.number_rows
                            self.proposed_widget['borderwidth'] = 2
                            self.proposed_widget['relief'] = tkinter.GROOVE
                            # tk_widget[attr] = getattr(pyte_widget, attr)
                            for i_column in range(number_columns):
                                for i_row in range(number_rows):
                                    # self.new_filler_label(self.proposed_widget, i_column, i_row)
                                    new_label = ttk.Label(self.proposed_widget, text=FILLER_TEXT)
                                    new_label.grid(row=i_row, column=i_column)
                                    new_label.bind("<Motion>", self.user_motion_callback)
                                    new_label.bind("<Button-1>", self.inserted_widget_click)
                                    # new_label.bind("<ButtonRelease-1>", self.widget_release)
                                    self.filler_labels.append(new_label)
                        elif self.widget_toolbox.widget_in_toolbox_chosen is pyted_widget_types.Notebook:
                            self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name)
                            # self.proposed_widget['height'] = 75
                            # self.proposed_widget['width'] = 100
                            self.proposed_widget_tab = tkinter.Frame(self.proposed_widget)
                            number_columns = pyted_widget_types.Frame.number_columns
                            number_rows = pyted_widget_types.Frame.number_rows
                            self.proposed_widget_tab['borderwidth'] = 2
                            self.proposed_widget_tab['relief'] = tkinter.GROOVE
                            # tk_widget[attr] = getattr(pyte_widget, attr)
                            for i_column in range(number_columns):
                                for i_row in range(number_rows):
                                    # self.new_filler_label(self.proposed_widget, i_column, i_row)
                                    new_label = ttk.Label(self.proposed_widget_tab, text=FILLER_TEXT)
                                    new_label.grid(row=i_row, column=i_column)
                                    new_label.bind("<Motion>", self.user_motion_callback)
                                    new_label.bind("<Button-1>", self.inserted_widget_click)
                                    # new_label.bind("<ButtonRelease-1>", self.widget_release)
                                    self.filler_labels.append(new_label)
                            self.proposed_widget.add(self.proposed_widget_tab, text='tab 1')
                        elif hasattr(self.widget_toolbox.widget_in_toolbox_chosen, 'text'):
                            text = self.widgets.generate_unique_name(self.widget_toolbox.widget_in_toolbox_chosen)
                            if hasattr(self.widget_toolbox.widget_in_toolbox_chosen, 'value'):
                                self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                                         text=text,
                                                                                                         value=text)
                            else:
                                self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                                         text=text)
                        else:
                            self.proposed_widget = self.widget_toolbox.widget_in_toolbox_chosen.type(frame.tk_name)

                        self.proposed_widget.grid(column=grid_location[0], row=grid_location[1])
                        self.proposed_widget.bind('<Motion>', self.user_motion_callback)
                        self.proposed_widget.bind('<Button-1>', self.inserted_widget_click)

                        widget_under_mouse.destroy()
                        # print('new inserted widget x, y', event.x_root, event.y_root, grid_location)
            # replace old proposed widget with filler label (including if mouse moved out of user_frame)
            # print('here:', old_proposed_widget_location)
            if (old_proposed_widget_location != grid_location or old_proposed_widget_frame != frame) and\
                    old_proposed_widget_location is not None:
                if old_proposed_widget is not None and old_proposed_widget != self.proposed_widget:
                    old_proposed_widget.destroy()
                    self.new_filler_label(old_proposed_widget_frame.tk_name,
                                          old_proposed_widget_location[0], old_proposed_widget_location[1])

    def update_widget_attribute(self, pyte_widget: Pyted_Widget_Type, attr: str, new_value: Union[str, bool],
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
            if (int(new_position['row']) >= int(self.widgets.find_pyte_widget(pyte_widget.parent).number_rows) or
                    int(new_position['column']) >= int(self.widgets.find_pyte_widget(pyte_widget.parent).number_columns)):
                # pyte_widget.row = old_position['row']
                # pyte_widget.column = old_position['column']
                pyte_widget.remove = True
                pyte_widget.tk_name.grid_remove()
                self.handles.remove_selected_widget_handles()
                self.new_filler_label(self.widgets.find_tk_parent(pyte_widget),
                                      old_position['column'], old_position['row'])
                messagebox.showwarning('Widget being moved off grid',
                                       'Row or column greater than grid size. Widget has been removed. '
                                       'To get widget back move back onto grid and set remove to false')
            else:

                filler_widget = self.widgets.find_tk_parent(pyte_widget).grid_slaves(row=new_position['row'],
                                                                                     column=new_position['column'])[0]
                if filler_widget not in self.filler_labels and filler_widget != pyte_widget.tk_name:
                    # trying to move widget onto existing widget
                    pyte_widget.remove = True
                    pyte_widget.tk_name.grid_remove()
                    self.handles.remove_selected_widget_handles()
                    self.new_filler_label(self.widgets.find_tk_parent(pyte_widget),
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
            # self.empty_tk_container_widget(pyte_widget)
            self.empty_tk_container_widget(pyte_widget)
            self.fill_tk_container_widget(pyte_widget)
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
                    self.new_filler_label(self.widgets.find_tk_parent(widget_to_hide), widget_to_hide.column,
                                          widget_to_hide.row)
                    widget_to_hide.tk_name.grid_remove()
                    self.handles.remove_selected_widget_handles()
            else:
                # remove attribute is false, if widget not displayed then try to display it
                if not tk_widget_in_grid:
                    # check that the widget is on the grid
                    if (int(pyte_widget.row) >= int(self.widgets.find_pyte_widget(pyte_widget.parent).number_rows) or
                            int(pyte_widget.column) >= int(self.widgets.find_pyte_widget(pyte_widget.parent).number_columns)):
                        messagebox.showwarning('Widget off grid',
                                               'Row or column greater than grid size. '
                                               'To get widget back move back onto grid and set remove to false')
                        setattr(pyte_widget, 'remove', True)
                        return
                    # check that there is not a widget already visible
                    filler_widget = self.widgets.find_tk_parent(pyte_widget).grid_slaves(row=pyte_widget.row,
                                                                                         column=pyte_widget.column)[0]
                    if filler_widget not in self.filler_labels:
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
            self.navigator_tree_class.navigator_tree_change_item_name(pyte_widget, old_value)
            # raise Exception(f'renaming widget not yet implemented')

        elif attr_template == pyted_widget_types.BESPOKE_CODE and (attr == 'comment'):
            if init:
                # when user form is drawn the tk_name will be handled by user form initialisation code
                return
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
            raise Exception(f'attr_template "{attr_template}" not yet configured')
            # print(f'attr_template {attr_template} not yet implemented for {attr}')

    # called when a widget clicked using pointer
    def widget_click(self, _event, pyte_widget):
        self.mouse_button1_pressed = True
        if self.widget_toolbox.widget_in_toolbox_chosen is None:
            # frame, grid_location = self.find_grid_location(self.find_top_widget(), event.x_root, event.y_root)
            # print('-->', frame.name, grid_location, pyte_widget.name, pyte_widget.parent)
            # self.selected_current_frame = frame
            # self.selected_widget_current_column = grid_location[0]
            # self.selected_widget_current_row = grid_location[1]
            if self.selected_widget is None or self.selected_widget != pyte_widget:
                # no widget selected so selecting a widget or different widget selected
                self.select_widget(pyte_widget)
                self.widget_to_deselect_if_not_moved = None
            else:
                # may need to deselect widget if mouse not moved
                self.widget_to_deselect_if_not_moved = pyte_widget
            return "break"
        elif (self.widget_toolbox.widget_in_toolbox_chosen is pyted_widget_types.Frame and
              isinstance(pyte_widget, pyted_widget_types.Notebook)):
            self.insert_widget(self.widget_toolbox.widget_in_toolbox_chosen(), self.proposed_widget,
                               self.proposed_widget_frame,
                               [0, 0])

    # called when a (not filler) widget released using pointer
    def widget_release(self, _event):
        # print("widget release:", event.x_root, event.y_root)
        self.mouse_button1_pressed = False
        if self.widget_to_deselect_if_not_moved is None:
            # no widget selected so selecting a widget, or not in mouse pointer mode
            pass
        else:
            pass
            # widget already selected but deselect widget function commented out
            # self.deselect_selected_widget()
        return "break"

    def widget_move(self, event):
        # called when a (not filler) widget in user form is attempted to be moved
        if self.widget_toolbox.widget_in_toolbox_chosen is None and self.selected_widget is not None:
            # mouse pointer mode chosen from widget toolbox
            self.widget_to_deselect_if_not_moved = None
            # x_location = event.x_root - self.user_frame.winfo_rootx()
            # y_location = event.y_root - self.user_frame.winfo_rooty()
            # grid_location = self.user_frame.grid_location(x_location, y_location)
            frame, grid_location = self.find_grid_location(self.widgets.find_top_widget(), event.x_root, event.y_root)
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
                try:
                    widget_under_mouse = frame.tk_name.grid_slaves(column=grid_location[0], row=grid_location[1])[0]
                except IndexError:
                    # grid location returned is off the edge of the grid so do nothing
                    widget_under_mouse = None
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

            if widget_under_mouse in self.filler_labels:
                # print('widget move ', frame.name, grid_location)
                # print('old location', self.selected_current_frame.name, self.selected_widget_current_column,
                #       self.selected_widget_current_row)

                # put a new filler label at the old position where the widget was
                # print('>>>>>>>>>>>>', self.selected_widget.name, self.selected_widget_current_column)
                self.new_filler_label(selected_widget_current_frame.tk_name, selected_widget_current_column,
                                      selected_widget_current_row)

                # remove filler label from where the widget will move to
                self.filler_labels.remove(widget_under_mouse)
                widget_under_mouse.destroy()

                # move tk_widget, note have to destroy and re-create as you can not move tk_widgets between frames
                self.selected_widget.tk_name.destroy()
                clone = self.place_pyte_widget(self.selected_widget, tk_frame=frame.tk_name,
                                               column=grid_location[0], row=grid_location[1])
                if isinstance(self.selected_widget, pyted_widget_types.Frame):
                    self.fill_tk_container_widget(self.selected_widget)

                # self.selected_widget.tk_name.grid(column=grid_location[0], row=grid_location[1])
                if selected_widget_current_frame != frame:
                    widget_changed_frame = True
                else:
                    widget_changed_frame = False
                self.selected_widget.parent = frame.name
                self.selected_widget.column = grid_location[0]
                self.selected_widget.row = grid_location[1]
                self.attr_frame.update(self.selected_widget)
                self.handles.place_selected_widget_handles(clone)
                if widget_changed_frame:
                    self.navigator_tree_class.build_navigator_tree()
                # print('end move widget')

    def select_widget(self, new_selected_pyte_widget) -> None:
        # print('new select widget: ', new_selected_pyte_widget.name)
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
                widget_to_check = self.widgets.find_pyte_widget(widget_to_check.parent)

        if remove_or_parent_remove:
            self.handles.remove_selected_widget_handles()
        else:
            self.handles.place_selected_widget_handles(self.selected_widget.tk_name)

        # fill out attribute tree, and attribute entry box

        self.attr_frame.update(self.selected_widget)
        # self.update_navigator_tree()
        self.navigator_tree_class.navigator_tree_select_item()

    # called when filler label clicked using pointer
    def empty_label_click_callback(self, event):
        """Select parent container if filler label clicked"""
        frame, grid_location = self.find_grid_location(self.widgets.find_top_widget(), event.x_root, event.y_root)
        self.select_widget(frame)

    def find_grid_location(self, pyte_frame: pyted_widget_types.PytedGridContainerWidget, x_root: int, y_root: int)\
            -> (pyted_widget_types.PytedGridContainerWidget, (int, int)):
        """
        Find grid location in user_form

        Returns the grid location in the user_form (the GUI being designed by the user) for a given set of
        co-ordinates. If the co-ordinates are in a container within the main GUI, the grid location will be that of the
        container. The container is also returned.

        This function is called recursively to find the inner-most container.

        :param pyte_frame: the parent frame (normally TopLevel)
        :param x_root: x co-ordinate
        :param y_root: y co-ordinate
        :return: container and grid location for given point
        """
        tk_frame = pyte_frame.tk_name
        x_location = x_root - tk_frame.winfo_rootx()
        y_location = y_root - tk_frame.winfo_rooty()
        grid_location = tk_frame.grid_location(x_location, y_location)
        # find location is actually a container
        for pyte_widget in self.widgets.widget_list:
            # if not pyte_widget.type == tkinter.Toplevel:
            try:
                if (grid_location == (int(pyte_widget.column), int(pyte_widget.row)) and
                        pyte_widget.parent == pyte_frame.name):
                    if isinstance(pyte_widget, pyted_widget_types.Frame):
                        pyte_widget, grid_location = self.find_grid_location(pyte_widget, x_root, y_root)
                        break
                    if isinstance(pyte_widget, pyted_widget_types.Notebook):
                        # TODO: need to code to get correct tab
                        for pyte_widget_child in self.widgets.widget_list:
                            if pyte_widget_child.parent == pyte_widget.name:
                                possible_pyte_widget, possible_grid_location =\
                                    self.find_grid_location(pyte_widget_child, x_root, y_root)
                                # check to see if location is in notebook for frame
                                if possible_grid_location[1] >= 0:
                                    pyte_widget = possible_pyte_widget
                                    grid_location = possible_grid_location
                                else:
                                    grid_location = [0, 0]
                                break
                        break
            except AttributeError:
                pass
        else:
            pyte_widget = pyte_frame
        return pyte_widget, grid_location

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
        self.widget_toolbox.widget_in_toolbox_chosen = None
        self.widget_toolbox.widget_in_toolbox_chosen_double_click = False
        self.widget_toolbox.pointer_button.invoke()
        if self.proposed_widget is not None and self.proposed_widget_location is not None:
            self.new_filler_label(self.proposed_widget_frame.tk_name,
                                  self.proposed_widget_location[0], self.proposed_widget_location[1])
            self.proposed_widget.destroy()
            self.proposed_widget_frame = None
            self.proposed_widget_location = None

    def delete_key_callback(self, _event):
        if self.selected_widget is not None:
            # check that focus is not in edit attributes, in which case should not delete widget
            enable_delete = False
            if isinstance(self.root_window.focus_get(), tkinter.Radiobutton):
                enable_delete = True
            if isinstance(self.root_window.focus_get(), ttk.Notebook):
                enable_delete = True
            if isinstance(self.root_window.focus_get(), tkinter.ttk.Button):
                print(self.root_window.focus_get().cget('text'))
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
        self.new_filler_label(self.widgets.find_tk_parent(widget_to_delete), widget_to_delete.column,
                              widget_to_delete.row)
        widget_to_delete.tk_name.destroy()
        self.widgets.widget_list.remove(widget_to_delete)
        self.navigator_tree_class.build_navigator_tree()

    def user_frame_leave_callback(self, _event):
        if self.proposed_widget is not None and self.proposed_widget_location is not None:
            self.new_filler_label(self.proposed_widget_frame.tk_name,
                                  self.proposed_widget_location[0], self.proposed_widget_location[1])
            self.proposed_widget.destroy()
            self.proposed_widget_frame = None
            self.proposed_widget_location = None

    def inserted_widget_click(self, _event):
        # print('new widget', _event.x, _event.y, self.proposed_widget)
        self.insert_widget(self.widget_toolbox.widget_in_toolbox_chosen(), self.proposed_widget,
                           self.proposed_widget_frame,
                           self.proposed_widget_location)

    def insert_widget(self, new_widget, proposed_widget, proposed_widget_frame, proposed_widget_location):
        # new_widget = self.widget_toolbox.widget_in_toolbox_chosen()
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
        new_widget.tk_name.bind('<Motion>', self.user_motion_callback)
        new_widget.tk_name.bind("<B1-Motion>", self.widget_move)
        new_widget.tk_name.bind("<Button-1>", lambda
                                w_event, arg1=new_widget:
                                self.widget_click(w_event, arg1)
                                )
        new_widget.tk_name.bind("<ButtonRelease-1>", self.widget_release)

        if isinstance(new_widget, pyted_widget_types.Frame):
            new_widget.number_columns = pyted_widget_types.Frame.number_columns
            new_widget.number_rows = pyted_widget_types.Frame.number_rows
            # replace binding for filler labels from proposed container filler labels to an inserted container type
            for filler_label in proposed_widget.grid_slaves():
                filler_label.bind("<Motion>", self.user_motion_callback)
                filler_label.bind("<Button-1>", self.empty_label_click_callback)
                filler_label.bind("<ButtonRelease-1>", self.widget_release)

        self.widgets.widget_list.append(new_widget)
        self.navigator_tree_class.build_navigator_tree()
        # self.select_widget(new_widget)

        if isinstance(new_widget, pyted_widget_types.Notebook):
            child_frame_widget = pyted_widget_types.Frame()
            child_frame_widget.parent = new_widget
            self.insert_widget(child_frame_widget, self.proposed_widget_tab, new_widget, [0, 0])

        self.proposed_widget_frame = None
        self.proposed_widget_location = None
        self.proposed_widget = None

        if not self.widget_toolbox.widget_in_toolbox_chosen_double_click:
            self.widget_toolbox.widget_in_toolbox_chosen = None
            self.user_frame.after(30, lambda: self.widget_toolbox.widget_in_toolbox_chosen_tk_var.set('pointer'))
        # by return "break" we stop further event handling, which stops the inserted widget being active
        # self.select_widget(new_widget)
        # return "break"

    def menu_file_save(self):
        root = self.root_window
        root.filename = filedialog.asksaveasfilename(title="Select file", defaultextension=".py",
                                                     filetypes=(("python files", "*.py"), ("all files", "*.*")))
        if not root.filename == '':
            code = save_load.generate_code(self.widgets.widget_list)
            with open(root.filename, 'w') as f:
                f.write(code)
        else:
            # no cancel pressed
            pass

    def menu_file_load(self):
        root = self.root_window
        print(self.root_window)
        root.filename = filedialog.askopenfilename(initialfile='ddd.py', title="Select file",
                                                   filetypes=(("python files", "*.py"), ("all files", "*.*")))
        if not root.filename == '':
            with open(root.filename) as f:
                self.widgets.widget_list = save_load.parse_code(f)
                parent_pyte_widget = self.draw_user_frame()
                self.selected_widget = parent_pyte_widget
                self.navigator_tree_class.build_navigator_tree()
                self.select_widget(parent_pyte_widget)
        else:
            # no cancel pressed
            pass

    def menu_preview(self):
        code = save_load.generate_code(self.widgets.widget_list)
        name_space = {}
        exec(code, name_space)
        gui_class = name_space['GuiCollection']
        # gui = gui_class()
        gui_class()
