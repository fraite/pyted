import inspect
import tkinter
from tkinter import ttk
from typing import List, Union, Optional
from tkinter import filedialog, messagebox

import pyted_package.pyted_widget_types as pyted_widget_types
import pyted_package.save_load_package.save_load as save_load
from pyted_package.pyted_window import PytedWindow

FILLER_TEXT = '        .        '
Pyted_Widget_Type = Union[pyted_widget_types.Project, pyted_widget_types.StringVar,
                          pyted_widget_types.TopLevel, pyted_widget_types.Label, pyted_widget_types.Entry,
                          pyted_widget_types.Frame, pyted_widget_types.Button, pyted_widget_types.Checkbutton]
# update is_pyte_container if Pyte_Container_Type changed
Pyted_Container_Type = Union[pyted_widget_types.TopLevel, pyted_widget_types.Frame]


class Pyted:
    """A tkinter GUI Editor"""
    selected_widget: Optional[Pyted_Widget_Type]
    widgets: List[Pyted_Widget_Type]

    def __init__(self):

        self.root_window = tkinter.Tk()

        self.filler_labels = []
        self.widget_to_deselect_if_not_moved = None
        self.selected_widget = None
        self.widget_in_toolbox_chosen = None
        self.widget_in_toolbox_chosen_tk_var = tkinter.StringVar()
        self.widget_in_toolbox_chosen_double_click = False
        self.proposed_widget = None
        self.proposed_widget_frame = None
        self.proposed_widget_location = None
        self.selection_frame = None
        self.mouse_button1_pressed = False
        self.attr_input_method = tkinter.Entry
        self.attr_labels: List[tkinter.Widget] = []
        self.attr_widgets: List[tkinter.Widget] = []

        # set up test user form
        #
        self.widgets = []
        # Project widget
        # widget = pyted_widgets.Label()
        widget = pyted_widget_types.Project()
        widget.name = 'GuiCollection'
        widget.comment = 'a test GUI'
        self.widgets.append(widget)
        # Top level window
        widget = pyted_widget_types.TopLevel()
        widget.name = 'gui_1'
        widget.comment = 'A demo window'
        widget.window_title = 'My demo window'
        widget.number_columns = '4'
        widget.number_rows = '4'
        widget.padx = '5'
        widget.pady = '5'
        self.widgets.append(widget)

        # set up window
        toolbox = PytedWindow(self.root_window, self)
        self.background_user_frame = toolbox.background_user_frame
        self.user_frame = toolbox.user_frame
        self.toolbox_notebook = toolbox.toolbox_notebook
        # self.ttk_toolbox_frame = toolbox.ttk_toolbox_frame
        self.navigator_tree = toolbox.navigator_tree
        self.attr_frame = toolbox.attribute_frame2
        self.event_frame = toolbox.event_frame2
        self.row_col_frame = toolbox.row_col_frame2

        parent_pyte_widget = self.draw_user_frame()

        # Create handles
        #
        self.handle_NW_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_NE_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_SW_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        self.handle_SE_canvas = tkinter.Canvas(self.root_window, background='red', width=5, height=5)
        # self.NW_canvas.place(x=500, y=30)

        # setup toolbox frames adding tabs. Done by looking to see all tabs used by widgets
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
        ttk_label_button = ttk.Radiobutton(toolbox_frames[tab], text='pointer',
                                           variable=self.widget_in_toolbox_chosen_tk_var, value='pointer')
        ttk_label_button.invoke()
        ttk_label_button.bind("<Button-1>", self.toolbox_pointer_button_click)
        ttk_label_button.grid(column=0, row=0)
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
                        new_button = ttk.Radiobutton(toolbox_frames[tab], text=obj.label,
                                                     variable=self.widget_in_toolbox_chosen_tk_var, value=obj.label)
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
                        new_button.grid(column=toolbox_column[tab], row=toolbox_row[tab])

                        toolbox_column[tab] = toolbox_column[tab] + 2
                        if toolbox_column[tab] >= 8:
                            toolbox_row[tab] = toolbox_row[tab] + 2
                            toolbox_column[tab] = toolbox_column[tab] - 8

                    except AttributeError:
                        pass

        self.build_navigator_tree()
        self.select_widget(parent_pyte_widget)
        self.draw_user_frame()
        self.place_selected_widget_handles(self.user_frame)

        self.root_window.mainloop()
        # self.toolbox = None

    def draw_user_frame(self):
        # set up inside of User Frame
        #

        # Find top level widget, assign tk_name to user_frame, and get name
        pyte_widget = self.find_top_widget()
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

    def find_top_widget(self):
        for pyte_widget in self.widgets:
            try:
                if pyte_widget.type == tkinter.Toplevel:
                    return pyte_widget
            except AttributeError:
                pass
        raise Exception('No TopLevel widget defined in project')

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
                       event, arg1=self.find_pyte_widget_from_tk(container):
                       self.widget_click(event, arg1)
                       )
        new_label.bind("<ButtonRelease-1>", self.widget_release)
        self.filler_labels.append(new_label)

    def find_pyte_parent(self, pyte_widget: pyted_widget_types) -> pyted_widget_types:
        """
        Find the pyte_widget that is the parent of a pyte_widget

        :param pyte_widget: the pyte widget
        :return: the pyte_widget parent
        """
        for w in self.widgets:
            if w.name == pyte_widget.parent:
                parent_widget = w
                break
        else:
            parent_widget = None
        return parent_widget

    def find_tk_parent(self, pyte_widget: pyted_widget_types) -> tkinter.Widget:
        """
        Find the tk_widget that is the parent of a pyte_widget

        :param pyte_widget: the pyte widget
        :return: the tk_widget parent
        """

        for w in self.widgets:
            if w.name == pyte_widget.parent:
                parent_tk_widget = w.tk_name
                break
        else:
            parent_tk_widget = None
        return parent_tk_widget

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
            parent_tk_widget = self.find_tk_parent(pyte_widget)
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
            parent_id = self.find_tk_parent(pyte_widget)
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

    def fill_tk_container_widget(self, parent_pyte_widget: Pyted_Widget_Type) -> None:
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

        for pyte_widget in self.widgets:
            if pyte_widget.parent == parent_pyte_widget.name:
                if (int(pyte_widget.column) >= int(parent_pyte_widget.number_columns) or
                        int(pyte_widget.row) >= int(parent_pyte_widget.number_rows)):
                    pyte_widget.remove = True
                elif isinstance(pyte_widget, pyted_widget_types.Frame):
                    self.place_pyte_widget(pyte_widget)
                    self.fill_tk_container_widget(pyte_widget)
                else:
                    self.place_pyte_widget(pyte_widget)

    def empty_tk_container_widget(self, parent_pyte_widget: Pyted_Widget_Type) -> None:
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
            elif isinstance(self.get_pyte_widget(child_widget), pyted_widget_types.Frame):
                self.empty_tk_container_widget(self.get_pyte_widget(child_widget))
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
        if self.widget_in_toolbox_chosen is None:
            # print('<<<<', self.selected_widget.name, self.mouse_button1_pressed)
            if self.selected_widget is not None and self.mouse_button1_pressed:
                # selection widget chosen so may need to move widget
                self.widget_move(event)
        else:
            # toolbox widget chosen so may need to insert proposed widget into user_frame
            frame, grid_location = self.find_grid_location(self.find_top_widget(), event.x_root, event.y_root)
            # if self.proposed_widget_frame is not None:
            #     print('user motion-toolbox chosen', 'mouse location:', frame.name, grid_location,
            #           'proposed_widget_location', self.proposed_widget_frame.name, self.proposed_widget_location)
            # else:
            #     print('self.proposed_widget_frame is None')
            # add inserted widget if does not exist and valid to do so
            old_proposed_widget = self.proposed_widget
            old_proposed_widget_frame = self.proposed_widget_frame
            old_proposed_widget_location = self.proposed_widget_location
            if self.proposed_widget_location != grid_location or self.proposed_widget_frame != frame:
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
                        if self.widget_in_toolbox_chosen is pyted_widget_types.Frame:
                            self.proposed_widget = self.widget_in_toolbox_chosen.type(frame.tk_name)
                            number_columns = self.widget_in_toolbox_chosen.number_columns
                            number_rows = self.widget_in_toolbox_chosen.number_rows
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
                        elif hasattr(self.widget_in_toolbox_chosen, 'text'):
                            text = self.generate_unique_name(self.widget_in_toolbox_chosen)
                            if hasattr(self.widget_in_toolbox_chosen, 'value'):
                                self.proposed_widget = self.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                          text=text, value=text)
                            else:
                                self.proposed_widget = self.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                          text=text)
                        else:
                            self.proposed_widget = self.widget_in_toolbox_chosen.type(frame.tk_name)

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
            if (int(new_position['row']) >= int(self.find_pyte_widget(pyte_widget.parent).number_rows) or
                    int(new_position['column']) >= int(self.find_pyte_widget(pyte_widget.parent).number_columns)):
                # pyte_widget.row = old_position['row']
                # pyte_widget.column = old_position['column']
                pyte_widget.remove = True
                pyte_widget.tk_name.grid_remove()
                self.remove_selected_widget_handles()
                self.new_filler_label(self.find_tk_parent(pyte_widget),
                                      old_position['column'], old_position['row'])
                messagebox.showwarning('Widget being moved off grid',
                                       'Row or column greater than grid size. Widget has been removed. '
                                       'To get widget back move back onto grid and set remove to false')
            else:

                filler_widget = self.find_tk_parent(pyte_widget).grid_slaves(row=new_position['row'],
                                                                             column=new_position['column'])[0]
                if filler_widget not in self.filler_labels and filler_widget != pyte_widget.tk_name:
                    # trying to move widget onto existing widget
                    pyte_widget.remove = True
                    pyte_widget.tk_name.grid_remove()
                    self.remove_selected_widget_handles()
                    self.new_filler_label(self.find_tk_parent(pyte_widget),
                                          old_position['column'], old_position['row'])
                    messagebox.showwarning('Widget being moved onto existing widget',
                                           'Row and column the same as another widget. Widget has been removed. '
                                           'To get widget back move back onto empty slot and set remove to false')
                    return
                filler_widget.grid(row=old_position['row'], column=old_position['column'])
                tk_widget.grid({attr: new_attr_val})
                self.place_selected_widget_handles(pyte_widget.tk_name)

        elif attr_template == pyted_widget_types.GRID_SIZE_CODE:
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            # self.empty_tk_container_widget(pyte_widget)
            # TODO: seems to be error when resize hides widget, then resize back, then remove=false, then move
            self.empty_tk_container_widget(pyte_widget)
            self.fill_tk_container_widget(pyte_widget)
            self.place_selected_widget_handles(pyte_widget.tk_name)

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
                    self.new_filler_label(self.find_tk_parent(widget_to_hide), widget_to_hide.column,
                                          widget_to_hide.row)
                    widget_to_hide.tk_name.grid_remove()
                    self.remove_selected_widget_handles()
            else:
                # remove attribute is false, if widget not displayed then try to display it
                if not tk_widget_in_grid:
                    # check that the widget is on the grid
                    if (int(pyte_widget.row) >= int(self.find_pyte_widget(pyte_widget.parent).number_rows) or
                            int(pyte_widget.column) >= int(self.find_pyte_widget(pyte_widget.parent).number_columns)):
                        messagebox.showwarning('Widget off grid',
                                               'Row or column greater than grid size. '
                                               'To get widget back move back onto grid and set remove to false')
                        setattr(pyte_widget, 'remove', True)
                        return
                    # check that there is not a widget already visible
                    filler_widget = self.find_tk_parent(pyte_widget).grid_slaves(row=pyte_widget.row,
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
                    filler_widget = self.find_tk_parent(pyte_widget).grid_slaves(row=pyte_widget.row,
                                                                                 column=pyte_widget.column)[0]
                    filler_widget.grid_forget()
                    filler_widget.destroy()
                    pyte_widget.tk_name.grid(row=pyte_widget.row, column=pyte_widget.column)
                    self.place_selected_widget_handles(pyte_widget.tk_name)

        elif attr_template == pyted_widget_types.BESPOKE_CODE and attr == 'name':
            if init:
                # when user form is drawn the widget name will be handled by user form initialisation code
                return
            # check name is really changed
            if new_value == old_value:
                return
            # check name is not already taken
            for i_pyte_widget in self.widgets:
                if i_pyte_widget != pyte_widget:
                    if pyte_widget.name == i_pyte_widget.name:
                        # can't messagebox here as this would move focus out of entry box and cause binding to run again
                        # messagebox.showwarning('Renaming problem',
                        #                        'Name already exists for another widget and Name not changed')
                        setattr(pyte_widget, attr, old_value)
                        return 'Renaming problem', 'Name already exists for another widget and Name not changed'
            for i_pyte_widget in self.widgets:
                if i_pyte_widget.parent == old_value:
                    i_pyte_widget.parent = new_value
            # self.update_navigator_tree()
            self.navigator_tree_change_item_name(pyte_widget, old_value)
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
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            # TODO: implement renaming widget parent code
            raise Exception(f'renaming widget parent not yet implemented')
        elif attr_template == pyted_widget_types.VAR_SET_CODE:
            setattr(pyte_widget, pyted_widget_types.VAR_SET_CODE, new_value)
            # TODO: show widgets that use the variable with the variable value
            # TODO: preview does not widgets with initial variable values, but run coded does...
        elif attr_template.startswith('<'):
            if init:
                # when user form is drawn the widget parent will be handled by user form initialisation code
                return
            return
        else:
            raise Exception(f'attr_template "{attr_template}" not yet configured')
            # print(f'attr_template {attr_template} not yet implemented for {attr}')

    def get_pyte_widget(self, tk_widget):
        """Get pyte widget that has tk_widget in the user form"""
        for pyte_widget in self.widgets:
            if pyte_widget.label != 'Project':
                if tk_widget == pyte_widget.tk_name:
                    return pyte_widget
        raise Exception(f"pyte widget not found for tk widget {tk_widget}")

    # called when a widget clicked using pointer
    def widget_click(self, _event, pyte_widget):
        self.mouse_button1_pressed = True
        if self.widget_in_toolbox_chosen is None:
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

    # called when a (not filler) widget released using pointer
    def widget_release(self, _event):
        # print("widget release:", event.x_root, event.y_root)
        self.mouse_button1_pressed = False
        if self.widget_to_deselect_if_not_moved is None:
            # no widget selected so selecting a widget, or not in mouse pointer mode
            pass
        else:
            # widget already selected so deselect it
            self.deselect_selected_widget()
        return "break"

    def widget_move(self, event):
        # called when a (not filler) widget in user form is attempted to be moved
        if self.widget_in_toolbox_chosen is None and self.selected_widget is not None:
            # mouse pointer mode chosen from widget toolbox
            self.widget_to_deselect_if_not_moved = None
            # x_location = event.x_root - self.user_frame.winfo_rootx()
            # y_location = event.y_root - self.user_frame.winfo_rooty()
            # grid_location = self.user_frame.grid_location(x_location, y_location)
            frame, grid_location = self.find_grid_location(self.find_top_widget(), event.x_root, event.y_root)
            if self.selected_widget.type == tkinter.Toplevel:
                selected_widget_current_row = None
                selected_widget_current_column = None
                selected_widget_current_frame = None
            else:
                selected_widget_current_row = self.selected_widget.row
                selected_widget_current_column = self.selected_widget.column
                selected_widget_current_frame = self.find_pyte_parent(self.selected_widget)
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
                # check that selected frame is not parent of the frame that we are noving into
                pyte_parent = self.find_pyte_parent(frame)
                while pyte_parent.type != tkinter.Toplevel:
                    if pyte_parent == self.selected_widget:
                        # trying to move a container into it's child
                        widget_under_mouse = None
                        break
                    pyte_parent = self.find_pyte_parent(pyte_parent)

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
                self.update_attr_frame()
                self.place_selected_widget_handles(clone)
                if widget_changed_frame:
                    self.build_navigator_tree()
                # print('end move widget')

    def select_widget(self, new_selected_pyte_widget) -> None:
        # print('new select widget: ', new_selected_pyte_widget.name)
        if self.selected_widget is not None:
            # print('current selected widget: ', self.selected_widget.name)
            self.deselect_selected_widget()
        self.selected_widget = new_selected_pyte_widget

        # place widget handles if required
        try:
            is_widget = new_selected_pyte_widget.is_widget
        except AttributeError:
            is_widget = True
        if is_widget:
            # check to see if widget attribute remove is True (or the parent of the widget)
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
                widget_to_check = self.find_pyte_widget(widget_to_check.parent)

            if remove_or_parent_remove:
                self.remove_selected_widget_handles()
            else:
                self.place_selected_widget_handles(self.selected_widget.tk_name)

        # fill out attribute tree, and attribute entry box

        self.update_attr_frame()
        # self.update_navigator_tree()
        self.navigator_tree_select_item()

    def find_pyte_widget(self, name):
        for pyte_widget in self.widgets:
            if pyte_widget.name == name:
                return pyte_widget
        raise Exception(f'pyte widget with name {name} can not be found')

    def find_pyte_widget_from_tk(self, tk_name):
        for pyte_widget in self.widgets:
            try:
                if pyte_widget.tk_name == tk_name:
                    return pyte_widget
            except AttributeError:
                pass
        raise Exception(f'pyte widget with tk_name {tk_name} can not be found')

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

    def remove_selected_widget_handles(self):
        self.handle_NW_canvas.place_forget()
        self.handle_NE_canvas.place_forget()
        self.handle_SW_canvas.place_forget()
        self.handle_SE_canvas.place_forget()

    def update_attr_frame(self):
        for attr_label in self.attr_labels:
            attr_label.destroy()
        self.attr_labels = []
        for attr_widget in self.attr_widgets:
            attr_widget.destroy()
        self.attr_widgets = []
        pyte_widget = self.selected_widget
        attr_row = 0
        event_row = 0
        if self.selected_widget is None:
            return
        for k, v in pyte_widget.get_input_type().items():
            if v != pyted_widget_types.NO_INPUT:
                if pyte_widget.get_code_template(k).startswith('<'):
                    property_frame = self.event_frame
                    event_row = event_row + 1
                    property_row = event_row
                else:
                    property_frame = self.attr_frame
                    attr_row = attr_row + 1
                    property_row = attr_row
                lab = tkinter.Label(property_frame, text=k)
                lab.grid(row=property_row, column=0, sticky='W')
                self.attr_labels.append(lab)
                if v == pyted_widget_types.SINGLE_INPUT:
                    widget_attr = getattr(pyte_widget, k)
                    e = ttk.Entry(property_frame, takefocus=True)
                    e.grid(row=property_row, column=1, sticky='NWES')
                    e.insert(0, str(widget_attr))
                    # self.entry_attr.bind("<Return>", self.pyte_code.attr_entry_changed)
                    # self.entry_attr.bind("<FocusOut>", self.pyte_code.attr_entry_changed)
                    e.bind("<Return>", lambda
                           event, arg1=k, arg2=e:
                           self.attr_entry_callback(event, arg1, arg2)
                           )
                    e.bind("<FocusOut>", lambda
                           event, arg1=k, arg2=e:
                           self.attr_entry_callback(event, arg1, arg2)
                           )
                    self.attr_widgets.append(e)
                elif v == pyted_widget_types.SINGLE_OPTION:
                    widget_attr = getattr(pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    cb['values'] = list(self.selected_widget.get_input_options(k))
                    # self.combobox_attr.bind('<<ComboboxSelected>>', self.pyte_code.attr_combobox_selected_callback)
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb:
                            self.attr_combobox_callback(event, arg1, arg2)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.BOOL_INPUT:
                    widget_attr = getattr(pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    if widget_attr:
                        cb.set('True')
                    else:
                        cb.set('False')
                    cb['values'] = list(self.selected_widget.get_input_options(k))
                    # self.combobox_attr.bind('<<ComboboxSelected>>', self.pyte_code.attr_combobox_selected_callback)
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb:
                            self.attr_combobox_callback(event, arg1, arg2)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.PARENT_OPTION:
                    widget_attr = getattr(pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = []
                    for widget in self.widgets:
                        if isinstance(widget, pyted_widget_types.Frame):
                            var_widgets.append(widget.name)
                    cb['values'] = var_widgets
                    # self.combobox_attr.bind('<<ComboboxSelected>>', self.pyte_code.attr_combobox_selected_callback)
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb:
                            self.attr_combobox_callback(event, arg1, arg2)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.STRING_VAR_OPTION:
                    widget_attr = getattr(pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = []
                    for widget in self.widgets:
                        if isinstance(widget, pyted_widget_types.StringVar):
                            var_widgets.append(widget.name)
                    cb['values'] = var_widgets
                    # self.combobox_attr.bind('<<ComboboxSelected>>', self.pyte_code.attr_combobox_selected_callback)
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb:
                            self.attr_combobox_callback(event, arg1, arg2)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.STRING_EVENT_OPTION:
                    widget_attr = getattr(pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = ['', pyte_widget.name + '_' + k]
                    cb['values'] = var_widgets
                    # self.combobox_attr.bind('<<ComboboxSelected>>', self.pyte_code.attr_combobox_selected_callback)
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb:
                            self.attr_combobox_callback(event, arg1, arg2)
                            )
                    self.attr_widgets.append(cb)
                else:
                    raise Exception('input type not defined')

        # fill row/col tab
        if isinstance(pyte_widget, pyted_widget_types.PytedPlacedWidget):
            # row weight
            lab = tkinter.Label(self.row_col_frame, text='row weight')
            lab.grid(row=1, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.find_pyte_parent(pyte_widget).get_row_configuration(pyte_widget.row)
            widget_attr = row_config['weight']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=1, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='weight', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='weight', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)
            # row minsize
            lab = tkinter.Label(self.row_col_frame, text='row minsize')
            lab.grid(row=2, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.find_pyte_parent(pyte_widget).get_row_configuration(pyte_widget.row)
            widget_attr = row_config['minsize']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=2, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='minsize', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='minsize', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)
            # row pad
            lab = tkinter.Label(self.row_col_frame, text='row pad')
            lab.grid(row=3, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.find_pyte_parent(pyte_widget).get_row_configuration(pyte_widget.row)
            widget_attr = row_config['pad']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=3, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='pad', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='pad', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)
            # col weight
            lab = tkinter.Label(self.row_col_frame, text='col weight')
            lab.grid(row=4, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.find_pyte_parent(pyte_widget).get_column_configuration(pyte_widget.column)
            widget_attr = col_config['weight']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=4, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='weight', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='weight', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)
            # col minsize
            lab = tkinter.Label(self.row_col_frame, text='col minsize')
            lab.grid(row=5, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.find_pyte_parent(pyte_widget).get_column_configuration(pyte_widget.column)
            widget_attr = col_config['minsize']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=5, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='minsize', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='minsize', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)
            # col pad
            lab = tkinter.Label(self.row_col_frame, text='col pad')
            lab.grid(row=6, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.find_pyte_parent(pyte_widget).get_column_configuration(pyte_widget.column)
            widget_attr = col_config['pad']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=6, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='pad', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='pad', arg3=e:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3)
                   )
            self.attr_widgets.append(e)

    # called when a row or column attribute entry box is changed
    def row_col_attr_entry_callback(self, _event, row_col, attr, entrybox):
        if self.selected_widget is not None:
            if row_col == 'row':
                self.find_pyte_parent(self.selected_widget).set_row_configuration(self.selected_widget.row, attr,
                                                                                  entrybox.get())
                self.find_tk_parent(self.selected_widget).rowconfigure(self.selected_widget.row, {attr: entrybox.get()})
            if row_col == 'col':
                self.find_pyte_parent(self.selected_widget).set_column_configuration(self.selected_widget.column, attr,
                                                                                     entrybox.get())
                self.find_tk_parent(self.selected_widget).columnconfigure(self.selected_widget.row,
                                                                          {attr: entrybox.get()})
        # self.update_attr_frame()

    # called when an attribute entry box lost focus or return presses
    def attr_entry_callback(self, _event, attrib, entrybox):
        if self.selected_widget is not None:
            return_value = self.update_widget_attribute(self.selected_widget, attrib, entrybox.get())
            # self.update_attr_frame()
            if return_value is not None:
                messagebox.showwarning('Renaming problem',
                                       'Name already exists for another widget and Name not changed')

    # called attribute combo box enter button or lost focus
    def attr_combobox_callback(self, _event, attrib, combobox):
        if self.selected_widget is not None:
            # attr_template = self.selected_widget.attr_template[attrib]
            attr_template = self.selected_widget.get_input_type(attrib)
            # if attr_template[0] == pyted_widgets.BOOL_INPUT:
            if attr_template == pyted_widget_types.BOOL_INPUT:
                if combobox.get() == 'True':
                    self.update_widget_attribute(self.selected_widget, attrib, True)
                else:
                    self.update_widget_attribute(self.selected_widget, attrib, False)
            else:
                self.update_widget_attribute(self.selected_widget, attrib, combobox.get())
            # self.update_attr_frame()

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
        widget = self.widgets[0]
        self.navigator_tree.insert('', 'end', widget.name,
                                   text=widget.name, values='"' + repr(widget.type) + '"',
                                   tags='project')
        self.navigator_tree.item(widget.name, open=True)
        project_name = widget.name

        # put vars into tree
        for widget in self.widgets:
            try:
                is_var = widget.is_var
            except AttributeError:
                is_var = False
            if is_var:
                self.navigator_tree.insert(project_name, 'end', widget.name,
                                           text=widget.name, values='"' + repr(widget.type) + '"',
                                           tags='var')

        # put widgets into tree
        widget = self.find_top_widget()
        self.navigator_tree.insert(self.widgets[0].name, 'end', widget.name,
                                   text=widget.name, values='"' + repr(widget.type) + '"',
                                   tags='toplevel')
        self.navigator_tree.item(widget.name, open=True)
        self.build_navigator_tree_parent(widget)
        if self.selected_widget is not None:
            self.navigator_tree.focus(self.selected_widget.name)
            self.navigator_tree.selection_set(self.selected_widget.name)

    def build_navigator_tree_parent(self, parent: pyted_widget_types) -> None:
        """
        Adds items to the navigator tree with the parent specified

        Adds all widgets with the parent specified as items to the navigator tree. Container widgets are also added
        with the branch opened and the function called recursively to fill the tree.

        :param parent: parent of widgets to be added to navigator tree
        """
        for widget in self.widgets:
            try:
                widget_type = widget.type
            except AttributeError:
                widget_type = None
            if not widget_type == tkinter.Toplevel:
                if widget.parent == parent.name:
                    self.navigator_tree.insert(widget.parent, 'end', widget.name,
                                               text=widget.name, values='"' + repr(widget.type) + '"',
                                               tags='widget')
                    if isinstance(widget, pyted_widget_types.Frame):
                        self.navigator_tree.item(widget.name, open=True)
                        self.build_navigator_tree_parent(widget)

    def navigator_tree_select_item(self):
        if self.selected_widget is not None:
            self.navigator_tree.focus(self.selected_widget.name)
            self.navigator_tree.selection_set(self.selected_widget.name)
            self.navigator_tree.see(self.selected_widget.name)

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
        if self.selected_widget is not None:
            self.navigator_tree.focus(self.selected_widget.name)
            self.navigator_tree.selection_set(self.selected_widget.name)

    # called when filler label clicked using pointer deselecting the selected widget
    def empty_label_click_callback(self, event):
        """Select parent container if filler label clicked"""
        frame, grid_location = self.find_grid_location(self.find_top_widget(), event.x_root, event.y_root)
        self.select_widget(frame)
        # self.widget_click(event, self.selected_widget)
        # code used to deselect widgets
        # if self.selected_widget is not None:
        #    # TODO: Implement clicking selecting next frame up
        #    self.deselect_selected_widget()

        # self.mouse_button1_pressed = True
        # if self.widget_in_toolbox_chosen is None:
        #     self.selected_current_frame = frame
        #     self.selected_widget_current_column = grid_location[0]
        #     self.selected_widget_current_row = grid_location[1]
        #     if self.selected_widget is None or self.selected_widget != frame:
        #         # no widget selected so selecting a widget or different widget selected
        #         self.select_widget(frame)
        #         self.widget_to_deselect_if_not_moved = None
        #     else:
        #         # may need to deselect widget if mouse not moved
        #         self.widget_to_deselect_if_not_moved = frame
        #     return "break"

    def find_grid_location(self, pyte_frame: Pyted_Widget_Type, x_root: int, y_root: int)\
            -> (Pyted_Widget_Type, (int, int)):
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
        for pyte_widget in self.widgets:
            # if not pyte_widget.type == tkinter.Toplevel:
            try:
                if (grid_location == (int(pyte_widget.column), int(pyte_widget.row)) and
                        pyte_widget.parent == pyte_frame.name):
                    if isinstance(pyte_widget, pyted_widget_types.Frame):
                        pyte_widget, grid_location = self.find_grid_location(pyte_widget, x_root, y_root)
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
            self.remove_selected_widget_handles()
            self.selected_widget = None
            self.update_attr_frame()

    def escape_key_callback(self, _event):
        pass

    def delete_key_callback(self, _event):
        if self.selected_widget is not None:
            # check that focus is not in edit attributes, in which should not delete widget
            enable_delete = False
            if self.root_window.focus_get() == self.root_window:
                enable_delete = True
            if isinstance(self.root_window.focus_get(), tkinter.ttk.Button):
                print(self.root_window.focus_get().cget('text'))
                if self.root_window.focus_get().cget('text') == 'pointer':
                    enable_delete = True
            if self.root_window.focus_get() == self.navigator_tree:
                enable_delete = True
            if enable_delete:
                self.delete_selected_widget()
                self.selected_widget = None
                self.update_attr_frame()

    def delete_selected_widget(self):
        # print('delete widget at ', self.selected_widget.column, self.selected_widget.row)
        widget_to_delete = self.selected_widget
        self.deselect_selected_widget()
        self.new_filler_label(self.find_tk_parent(widget_to_delete), widget_to_delete.column, widget_to_delete.row)
        widget_to_delete.tk_name.destroy()
        self.widgets.remove(widget_to_delete)
        self.build_navigator_tree()

    # called when widget in navigation tree clicked
    def navigator_tree_clicked(self, _event):
        pyte_widget = None
        for pyte_widget in self.widgets:
            if pyte_widget.name == self.navigator_tree.focus():
                break
        self.select_widget(pyte_widget)

    def is_child_container(self, pyte_widget, parent_pyte_widget_name):
        """Is pyte_widget a child of parent_pyte_widget_name (or the same widget)"""
        if pyte_widget.name == self.find_top_widget().name:
            if parent_pyte_widget_name == self.find_top_widget().name:
                return True
            else:
                return False
        elif pyte_widget.name == parent_pyte_widget_name:
            return True
        elif pyte_widget.parent == self.find_top_widget().name:
            return False
        else:
            for i_pyte_widget in self.widgets:
                if pyte_widget.parent == i_pyte_widget.name:
                    return self.is_child_container(i_pyte_widget, parent_pyte_widget_name)
            else:
                raise Exception('could not find widget with name pyte_widget.parent')

    # called when button in toolbox clicked
    def toolbox_button_click_callback(self, _event, tk_widget_obj):
        self.deselect_selected_widget()
        self.widget_in_toolbox_chosen = tk_widget_obj
        # print(tk_widget_obj)

    # called when var button in toolbox clicked
    def toolbox_var_button_click_callback(self, _event, tk_widget_obj):
        new_widget = tk_widget_obj()
        new_widget.name = self.generate_unique_name(new_widget)
        new_widget.parent = self.widgets[0].name

        self.widgets.append(new_widget)
        self.selected_widget = new_widget
        self.build_navigator_tree()
        self.update_attr_frame()
        self.remove_selected_widget_handles()
        # print(len(self.widgets))
        # self.deselect_selected_widget()
        self.widget_in_toolbox_chosen = None
        self.user_frame.after(300, lambda: self.widget_in_toolbox_chosen_tk_var.set('pointer'))

    # called when pointer button clicked in toolbox
    def toolbox_pointer_button_click(self, _event):
        self.widget_in_toolbox_chosen = None
        # print('toolbox pointer button clicked', event.x, event.y)
        # self.deselect_selected_widget()

    def user_frame_leave_callback(self, _event):
        if self.proposed_widget is not None and self.proposed_widget_location is not None:
            self.new_filler_label(self.proposed_widget_frame.tk_name,
                                  self.proposed_widget_location[0], self.proposed_widget_location[1])
            self.proposed_widget.destroy()
            self.proposed_widget_frame = None
            self.proposed_widget_location = None

    def inserted_widget_click(self, _event):
        # print('new widget', _event.x, _event.y, self.proposed_widget)
        new_widget = self.widget_in_toolbox_chosen()
        new_widget.parent = self.find_top_widget().name
        new_widget.parent = self.proposed_widget_frame.name
        new_widget.column = self.proposed_widget_location[0]
        new_widget.row = self.proposed_widget_location[1]
        new_widget.tk_name = self.proposed_widget
        new_widget.name = self.generate_unique_name(new_widget)
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
            new_widget.number_columns = self.widget_in_toolbox_chosen.number_columns
            new_widget.number_rows = self.widget_in_toolbox_chosen.number_rows
            # replace binding for filler labels from proposed container filler labels to an inserted container type
            for filler_label in self.proposed_widget.grid_slaves():
                filler_label.bind("<Motion>", self.user_motion_callback)
                filler_label.bind("<Button-1>", self.empty_label_click_callback)
                filler_label.bind("<ButtonRelease-1>", self.widget_release)

        self.widgets.append(new_widget)
        self.proposed_widget_frame = None
        self.proposed_widget_location = None
        self.proposed_widget = None
        self.build_navigator_tree()
        self.select_widget(new_widget)
        # TODO: implement double_click
        if not self.widget_in_toolbox_chosen_double_click:
            self.widget_in_toolbox_chosen = None
            self.user_frame.after(30, lambda: self.widget_in_toolbox_chosen_tk_var.set('pointer'))
            # by return "break" we stop further event handling, which stops the inserted widget being active
            return "break"

    def generate_unique_name(self, new_widget: pyted_widget_types) -> str:
        """
        Generate a unique name for a given widget

        Returns a unique name for a given widget, generally of in the form of the widget type and a number.

        :param new_widget: widget to be named
        :return: unique name for widget
        """
        potential_number = 1
        no_duplicate_found = False
        while not no_duplicate_found:
            for pw in self.widgets:
                if pw.name == new_widget.label.lower() + str(potential_number):
                    potential_number = potential_number + 1
                    break
            else:
                no_duplicate_found = True
        return new_widget.label.lower() + str(potential_number)

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
                self.widgets = save_load.parse_code(f)
                parent_pyte_widget = self.draw_user_frame()
                self.selected_widget = parent_pyte_widget
                self.build_navigator_tree()
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


if __name__ == '__main__':
    x = Pyted()
    # x.show()
