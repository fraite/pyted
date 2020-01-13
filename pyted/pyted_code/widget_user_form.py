#
from __future__ import annotations
from typing import TYPE_CHECKING, Union

import tkinter
from tkinter import ttk

import pyted.monet_widget_types as monet_widget_types
if TYPE_CHECKING:
    from pyted.pyted_code.pyted_core import PytedCore

FILLER_TEXT = '        .        '


class UserForm:
    """User Form

    """

    def __init__(self, pyted_core: PytedCore):
        self.pyted_core = pyted_core
        self.widgets = pyted_core.widgets

        self.filler_labels = []
        self.proposed_widget = None
        self.proposed_widget_frame = None
        self.proposed_widget_location = None
        self.proposed_widget_tab = None
        self.mouse_button1_pressed = False
        self.widget_to_deselect_if_not_moved = None

        self.user_frame = None

    def draw_user_frame(self):
        # set up inside of User Frame
        #

        # Find top level widget, assign tk_name to user_frame, and get name
        pyte_widget = self.widgets.find_top_widget()
        if self.user_frame is not None:
            self.user_frame.destroy()
        self.user_frame = ttk.Frame(self.pyted_core.background_user_frame)
        self.user_frame.bind("<Motion>", self.user_motion_callback)
        self.user_frame.bind("<Button-1>", lambda
                             event, arg1=pyte_widget:
                             self.widget_click(event, arg1)
                             )
        self.user_frame.bind("<ButtonRelease-1>", self.widget_release)
        self.user_frame.bind('<Leave>', self.user_frame_leave_callback)
        self.user_frame.grid(row=0, column=0)
        pyte_widget.tk_name = self.user_frame

        # Create and fill Frames with filler labels
        # first create containers before placing non-container widgets
        self.fill_tk_container_frame(pyte_widget)

        return pyte_widget

    def fill_tk_container_frame(self, monet_frame: monet_widget_types.PytedGridContainerWidget) -> None:
        """
        Fill a tk container frame

        Fills a tk container frame corresponding to a monet_widget. The container widget is filled with (blank) label
        widgets or widgets corresponding to pyte widgets. Where there are child container widgets, these are filled out
        recursively.

        :param monet_frame: monet frame container
        :return:
        """

        for i_col in range(int(monet_frame.number_columns)):
            for i_row in range(int(monet_frame.number_rows)):
                self.new_filler_label(monet_frame.tk_name, i_col, i_row)

        for pyte_widget in self.widgets.widget_list:
            if pyte_widget.parent == monet_frame.name:
                if (int(pyte_widget.column) >= int(monet_frame.number_columns) or
                        int(pyte_widget.row) >= int(monet_frame.number_rows)):
                    pyte_widget.remove = True
                elif isinstance(pyte_widget, monet_widget_types.Frame):
                    self.place_pyte_widget(pyte_widget)
                    self.fill_tk_container_frame(pyte_widget)
                else:
                    self.place_pyte_widget(pyte_widget)

    def fill_ttk_notebook(self, monet_notebook):
        frame_list = filter(lambda frame: (frame.parent == monet_notebook.name), self.widgets.widget_list)
        for frame in frame_list:
            print(frame)

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

    def place_pyte_widget(self, pyte_widget: monet_widget_types.PytedPlacedWidget, tk_frame=None,
                          column=None, row=None) -> tkinter.Widget:
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

    def find_grid_location(self, monet_frame: monet_widget_types.PytedGridContainerWidget, x_root: int, y_root: int)\
            -> (monet_widget_types.PytedContainerWidget, (int, int)):
        """
        Find grid location in user_form

        Returns the grid location and the container for a given set of co-ordinates. If the co-ordinates are in a
        child container within the monet_frame, the grid location will be that of the child container. If the
        co-ordinates are on the container itself (in other words the edge of the container), the row and column value
        returned is -1.

        This function is called recursively to find the inner-most container.

        :param monet_frame: the parent frame (normally TopLevel)
        :param x_root: x co-ordinate
        :param y_root: y co-ordinate
        :return: container and grid location for given point (column, row)
        """
        tk_frame = monet_frame.tk_name
        x_location = x_root - tk_frame.winfo_rootx()
        y_location = y_root - tk_frame.winfo_rooty()
        grid_location = tk_frame.grid_location(x_location, y_location)

        # find widget at location given and see if it is a container
        for possible_m_widget in self.widgets.widget_list:
            if isinstance(possible_m_widget, monet_widget_types.PytedPlacedWidget):
                # the possible_m_widget is a placed widget so may be in grid location
                if (grid_location == (int(possible_m_widget.column), int(possible_m_widget.row)) and
                        possible_m_widget.parent == monet_frame.name):
                    # the possible_m_widget is in the same grid location
                    if isinstance(possible_m_widget, monet_widget_types.Frame):
                        # the possible_m_widget is a frame so need to look inside frame
                        monet_frame, grid_location = self.find_grid_location(possible_m_widget, x_root, y_root)
                        break
                    if isinstance(possible_m_widget, monet_widget_types.Notebook):
                        for m_possible_notebook_frame in self.widgets.widget_list:
                            # TODO: need to code to get correct tab, this only finds the first frame
                            if m_possible_notebook_frame.parent == possible_m_widget.name:
                                # found frame in notebook, m_possible_notebook_frame
                                possible_m_widget_in_frame, possible_grid_location =\
                                    self.find_grid_location(m_possible_notebook_frame, x_root, y_root)
                                # check to see if location is in notebook for frame
                                if possible_grid_location[1] >= 0:
                                    # location is inside child frame of notebook
                                    monet_frame = possible_m_widget_in_frame
                                    grid_location = possible_grid_location
                                else:
                                    # location is on the notebook
                                    monet_frame = possible_m_widget
                                    grid_location = (-1, -1)
                                break
                        break

        # check to make sure x_root, y_root is not on the frame or outside

        if grid_location[0] < 0 or grid_location[0] >= int(monet_frame.number_columns):
            grid_location = (-1, -1)
        if grid_location[1] < 0 or grid_location[1] >= int(monet_frame.number_rows):
            grid_location = (-1, -1)
        return monet_frame, grid_location

    def new_tk_widget(self, pyte_widget: monet_widget_types.PytedPlacedWidget, tk_parent=None) -> tkinter.Widget:
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
            self.pyted_core.update_widget_attribute(pyte_widget, k, '', init=True)

        if isinstance(pyte_widget, monet_widget_types.Frame):
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

    def empty_tk_container_widget(self, parent_pyte_widget: monet_widget_types.PytedGridContainerWidget) -> None:
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
            elif isinstance(self.widgets.get_pyte_widget(child_widget), monet_widget_types.Frame):
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
        if self.pyted_core.widget_in_toolbox_chosen is None:
            # print('<<<<', self.pyted_core.selected_widget.name, self.mouse_button1_pressed)
            if self.pyted_core.selected_widget is not None and self.mouse_button1_pressed:
                # selection widget chosen so may need to move widget
                self.pyted_core.widget_move(event)
        else:
            # toolbox widget chosen so may need to insert proposed widget into user_frame
            frame, grid_location = self.find_grid_location(self.widgets.find_top_widget(), event.x_root, event.y_root)

            old_proposed_widget = self.proposed_widget
            old_proposed_widget_frame = self.proposed_widget_frame
            old_proposed_widget_location = self.proposed_widget_location

            # insert a widget if there is a label widget or frame in a container
            if self.proposed_widget_location != grid_location or self.proposed_widget_frame != frame:
                # widget_under_mouse points to the widget under the mouse, it may be a container if on edge
                if grid_location[0] < 0:
                    widget_under_mouse = frame
                else:
                    widget_under_mouse = frame.tk_name.grid_slaves(row=grid_location[1],
                                                                   column=grid_location[0])[0]
                # act depending on type of widget under the mouse
                if isinstance(widget_under_mouse, monet_widget_types.Frame):
                    # do nothing if trying to insert widget onto frame edge (not in)
                    pass
                elif (isinstance(old_proposed_widget_frame, monet_widget_types.Notebook) and
                      isinstance(self.proposed_widget, tkinter.Frame)):
                    # moving frame out of notebook
                    # TODO: implement moving out of notebook
                    #  print(self.proposed_widget_frame.name, old_proposed_widget_frame.name)
                    # self.proposed_widget.destroy()
                    pass
                elif isinstance(widget_under_mouse, monet_widget_types.Notebook):
                    if isinstance(self.proposed_widget, tkinter.Frame):
                        # moving frame into notebook
                        self.proposed_widget_frame = frame
                        self.proposed_widget_location = (-1, -1)
                        self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name)
                        self.fill_blank_tk_frame(self.proposed_widget)
                        frame.tk_name.add(self.proposed_widget)
                        frame.tk_name.select(self.proposed_widget)
                        self.proposed_widget.bind('<Motion>', self.user_motion_callback)
                        self.proposed_widget.bind('<Button-1>', self.inserted_widget_click)
                    else:
                        # moving widget that is not a frame into a notebook so do nothing
                        pass
                else:
                    if widget_under_mouse in self.filler_labels:
                        # moving a widget onto a position with a filler label so insert it
                        self.proposed_widget_frame = frame
                        self.proposed_widget_location = grid_location
                        if self.pyted_core.widget_in_toolbox_chosen is monet_widget_types.Frame:
                            self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name)
                            self.fill_blank_tk_frame(self.proposed_widget)
                        elif self.pyted_core.widget_in_toolbox_chosen is monet_widget_types.Notebook:
                            self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name)
                            # self.proposed_widget['height'] = 75
                            # self.proposed_widget['width'] = 100
                            self.proposed_widget_tab = tkinter.Frame(self.proposed_widget)
                            self.fill_blank_tk_frame(self.proposed_widget_tab)
                            self.proposed_widget.add(self.proposed_widget_tab, text='tab 1')
                        elif hasattr(self.pyted_core.widget_in_toolbox_chosen, 'text'):
                            text = self.widgets.generate_unique_name(self.pyted_core.widget_in_toolbox_chosen)
                            if hasattr(self.pyted_core.widget_in_toolbox_chosen, 'value'):
                                self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                                     text=text,
                                                                                                     value=text)
                            else:
                                self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name,
                                                                                                     text=text)
                        else:
                            self.proposed_widget = self.pyted_core.widget_in_toolbox_chosen.type(frame.tk_name)

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

    def fill_blank_tk_frame(self, proposed_widget):
        number_columns = monet_widget_types.Frame.number_columns
        number_rows = monet_widget_types.Frame.number_rows
        proposed_widget['borderwidth'] = 2
        proposed_widget['relief'] = tkinter.GROOVE
        for i_column in range(number_columns):
            for i_row in range(number_rows):
                new_label = ttk.Label(proposed_widget, text=FILLER_TEXT)
                new_label.grid(row=i_row, column=i_column)
                new_label.bind("<Motion>", self.user_motion_callback)
                new_label.bind("<Button-1>", self.inserted_widget_click)
                self.filler_labels.append(new_label)

    def user_form_click_callback(self, event, _frame):
        m_frame, grid_location = self.find_grid_location(self.widgets.find_top_widget(), event.x_root, event.y_root)
        clicked_tk_widget = m_frame.tk_name.grid_slaves(column=grid_location[0], row=grid_location[1])[0]
        if clicked_tk_widget in self.filler_labels:
            clicked_m_widget = m_frame
        else:
            clicked_m_widget = self.widgets.find_pyte_widget_from_tk(clicked_tk_widget)
        self.widget_click(event, clicked_m_widget)

    # called when a widget or empty label clicked using pointer
    def widget_click(self, _event, pyte_widget):
        self.mouse_button1_pressed = True
        if self.pyted_core.widget_in_toolbox_chosen is None:
            # frame, grid_location = self.find_grid_location(self.find_top_widget(), event.x_root, event.y_root)
            # print('-->', frame.name, grid_location, pyte_widget.name, pyte_widget.parent)
            # self.selected_current_frame = frame
            # self.selected_widget_current_column = grid_location[0]
            # self.selected_widget_current_row = grid_location[1]
            if self.pyted_core.selected_widget is None or self.pyted_core.selected_widget != pyte_widget:
                # no widget selected so selecting a widget or different widget selected
                self.pyted_core.select_widget(pyte_widget)
                self.widget_to_deselect_if_not_moved = None
            else:
                # may need to deselect widget if mouse not moved
                self.widget_to_deselect_if_not_moved = pyte_widget
            return
        elif (self.pyted_core.widget_in_toolbox_chosen is monet_widget_types.Frame and
              isinstance(pyte_widget, monet_widget_types.Notebook)):
            self.pyted_core.insert_widget(self.pyted_core.widget_in_toolbox_chosen(), self.proposed_widget,
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

    def user_frame_leave_callback(self, _event):
        if self.proposed_widget is not None and self.proposed_widget_location is not None:
            self.new_filler_label(self.proposed_widget_frame.tk_name,
                                  self.proposed_widget_location[0], self.proposed_widget_location[1])
            self.proposed_widget.destroy()
            self.proposed_widget_frame = None
            self.proposed_widget_location = None

    def inserted_widget_click(self, _event):
        # print('new widget', _event.x, _event.y, self.proposed_widget)
        self.pyted_core.insert_widget(self.pyted_core.widget_in_toolbox_chosen(), self.proposed_widget,
                                      self.proposed_widget_frame,
                                      self.proposed_widget_location)
