import tkinter
from tkinter import ttk
from tkinter import messagebox
from typing import List, Union

import pyted.pyted_widget_types as pyted_widget_types

import pyted.pyted_code.pyted_core as pyted_core
import pyted.pyted_code.widgets as widgets
import pyted.pyted_code.widget_handles as widget_handles



class AttributeFrame:
    """Widget attribute frame

    Frame that shows the widget attributes (including variables), and events. The frame additionally shows the row
    and column attributes of the parent.
    """

    def __init__(self, pyted_core: pyted_core):
        self.pyted_core: pyted_core = pyted_core
        self.handles: widget_handles = pyted_core.handles
        self.pyted_window = pyted_core.pyted_window
        self.widgets: widgets.Widgets = pyted_core.widgets
        # TODO: convert self.pyted_code.widgets to widgets, remove pyted_core

        self.attr_labels: List[tkinter.Widget] = []
        self.attr_widgets: List[tkinter.Widget] = []
        self.var_labels: List[tkinter.Widget] = []
        self.var_widgets: List[tkinter.Widget] = []

        self.attr_frame = self.pyted_window.attribute_frame2
        self.event_frame = self.pyted_window.event_frame2
        self.row_col_frame = self.pyted_window.row_col_frame2
        self.var_use_frame = self.pyted_window.var_use_frame2
        self.attr_notebook = self.pyted_window.attribute_event_note2

    def update(self, selected_widget: Union[pyted_widget_types.PytedWidget, None]):
        for attr_label in self.attr_labels:
            attr_label.destroy()
        self.attr_labels = []
        for attr_widget in self.attr_widgets:
            attr_widget.destroy()
        self.attr_widgets = []
        selected_pyte_widget = selected_widget
        attr_row = 0
        event_row = 0
        if selected_widget is None:
            return
        for k, v in selected_pyte_widget.get_input_type().items():
            if v != pyted_widget_types.NO_INPUT:
                if selected_pyte_widget.get_code_template(k).startswith('<'):
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
                    widget_attr = getattr(selected_pyte_widget, k)
                    e = ttk.Entry(property_frame, takefocus=True)
                    e.grid(row=property_row, column=1, sticky='NWES')
                    e.insert(0, str(widget_attr))
                    # self.pyted_core.entry_attr.bind("<Return>", self.pyted_core.pyte_code.attr_entry_changed)
                    # self.pyted_core.entry_attr.bind("<FocusOut>", self.pyted_core.pyte_code.attr_entry_changed)
                    e.bind("<Return>", lambda
                           event, arg1=k, arg2=e, arg3=selected_widget:
                           self.attr_entry_callback(event, arg1, arg2, arg3)
                           )
                    e.bind("<FocusOut>", lambda
                           event, arg1=k, arg2=e, arg3=selected_widget:
                           self.attr_entry_callback(event, arg1, arg2, arg3)
                           )
                    self.attr_widgets.append(e)
                elif v == pyted_widget_types.SINGLE_OPTION:
                    widget_attr = getattr(selected_pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    cb['values'] = list(selected_widget.get_input_options(k))
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb, arg3=selected_widget:
                            self.attr_combobox_callback(event, arg1, arg2, arg3)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.BOOL_INPUT:
                    widget_attr = getattr(selected_pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    if widget_attr:
                        cb.set('True')
                    else:
                        cb.set('False')
                    cb['values'] = list(selected_widget.get_input_options(k))
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb, arg3=selected_widget:
                            self.attr_combobox_callback(event, arg1, arg2, arg3)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.PARENT_OPTION:
                    widget_attr = getattr(selected_pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = []
                    for widget in self.widgets.widget_list:
                        if isinstance(widget, pyted_widget_types.Frame):
                            var_widgets.append(widget.name)
                    cb['values'] = var_widgets
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb, arg3=selected_widget:
                            self.attr_combobox_callback(event, arg1, arg2, arg3)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.STRING_VAR_OPTION:
                    widget_attr = getattr(selected_pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = []
                    for widget in self.widgets.widget_list:
                        if isinstance(widget, pyted_widget_types.StringVar):
                            var_widgets.append(widget.name)
                    cb['values'] = var_widgets
                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb, arg3=selected_widget:
                            self.attr_combobox_callback(event, arg1, arg2, arg3)
                            )
                    self.attr_widgets.append(cb)
                elif v == pyted_widget_types.STRING_EVENT_OPTION:
                    widget_attr = getattr(selected_pyte_widget, k)
                    cb = ttk.Combobox(property_frame)
                    cb.configure(state='readonly')
                    cb.grid(row=property_row, column=1, columnspan=1, sticky=tkinter.EW)
                    cb.set(widget_attr)
                    var_widgets = ['', selected_pyte_widget.name + '_' + k]
                    cb['values'] = var_widgets

                    cb.bind('<<ComboboxSelected>>', lambda
                            event, arg1=k, arg2=cb, arg3=selected_widget:
                            self.attr_combobox_callback(event, arg1, arg2, arg3)
                            )
                    self.attr_widgets.append(cb)
                else:
                    raise Exception('input type not defined')
    
        # fill row/col tab
        pyte_parent = self.widgets.find_pyte_parent(selected_pyte_widget)
        if (isinstance(selected_pyte_widget, pyted_widget_types.PytedPlacedWidget) and
                not isinstance(pyte_parent, pyted_widget_types.Notebook)):
            self.attr_notebook.add(self.pyted_window.row_col_tab_frame)
            # row weight
            lab = tkinter.Label(self.row_col_frame, text='row weight')
            lab.grid(row=1, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.widgets.find_pyte_parent(selected_pyte_widget).\
                get_row_configuration(selected_pyte_widget.row)
            widget_attr = row_config['weight']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=1, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='weight', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='weight', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
            # row minsize
            lab = tkinter.Label(self.row_col_frame, text='row minsize')
            lab.grid(row=2, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.widgets.find_pyte_parent(selected_pyte_widget).\
                get_row_configuration(selected_pyte_widget.row)
            widget_attr = row_config['minsize']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=2, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='minsize', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='minsize', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
            # row pad
            lab = tkinter.Label(self.row_col_frame, text='row pad')
            lab.grid(row=3, column=0, sticky='W')
            self.attr_labels.append(lab)
            row_config = self.widgets.find_pyte_parent(selected_pyte_widget).\
                get_row_configuration(selected_pyte_widget.row)
            widget_attr = row_config['pad']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=3, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='row', arg2='pad', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='row', arg2='pad', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
            # col weight
            lab = tkinter.Label(self.row_col_frame, text='col weight')
            lab.grid(row=4, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.widgets.find_pyte_parent(selected_pyte_widget). \
                get_column_configuration(selected_pyte_widget.column)
            widget_attr = col_config['weight']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=4, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='weight', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='weight', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
            # col minsize
            lab = tkinter.Label(self.row_col_frame, text='col minsize')
            lab.grid(row=5, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.widgets.find_pyte_parent(selected_pyte_widget). \
                get_column_configuration(selected_pyte_widget.column)
            widget_attr = col_config['minsize']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=5, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='minsize', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='minsize', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
            # col pad
            lab = tkinter.Label(self.row_col_frame, text='col pad')
            lab.grid(row=6, column=0, sticky='W')
            self.attr_labels.append(lab)
            col_config = self.widgets.find_pyte_parent(selected_pyte_widget). \
                get_column_configuration(selected_pyte_widget.column)
            widget_attr = col_config['pad']
            e = ttk.Entry(self.row_col_frame, takefocus=True)
            e.grid(row=6, column=1, sticky='NWES')
            e.insert(0, str(widget_attr))
            e.bind("<Return>", lambda
                   event, arg1='col', arg2='pad', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            e.bind("<FocusOut>", lambda
                   event, arg1='col', arg2='pad', arg3=e, arg4=selected_widget:
                   self.row_col_attr_entry_callback(event, arg1, arg2, arg3, arg4)
                   )
            self.attr_widgets.append(e)
        else:
            self.attr_notebook.hide(self.pyted_window.row_col_tab_frame)
    
        # fill variable usage tab
        if isinstance(selected_pyte_widget, pyted_widget_types.StringVar):
            self.attr_notebook.add(self.pyted_window.var_use_tab_frame)
            for var_label in self.var_labels:
                var_label.destroy()
            self.var_labels = []
            for var_widget in self.var_widgets:
                var_widget.destroy()
            self.var_widgets = []
            var_row = 0
            if selected_widget is None:
                return
            for pyted_widget_search in self.widgets.widget_list:
                try:
                    var_name = pyted_widget_search.textvariable
                except AttributeError:
                    var_name = None
                if var_name is None:
                    try:
                        var_name = pyted_widget_search.variable
                    except AttributeError:
                        var_name = None
    
                if var_name == selected_pyte_widget.name:
                    var_use_frame = self.var_use_frame
                    var_row = var_row + 1
                    lab = tkinter.Label(var_use_frame, text=pyted_widget_search.name)
                    lab.grid(row=var_row, column=0, sticky='W')
                    self.var_labels.append(lab)
                    lab = tkinter.Label(var_use_frame, text=pyted_widget_search.label)
                    lab.grid(row=var_row, column=1, sticky='W')
                    self.var_labels.append(lab)
        else:
            self.attr_notebook.hide(self.pyted_window.var_use_tab_frame)

    # called when a row or column attribute entry box is changed
    def row_col_attr_entry_callback(self, _event, row_col, attr, entrybox, selected_widget):
        pyte_parent = self.widgets.find_pyte_parent(selected_widget)
        tk_parent = self.widgets.find_tk_parent(selected_widget)
        if selected_widget is not None:
            if row_col == 'row':
                pyte_parent.set_row_configuration(selected_widget.row, attr, entrybox.get())
                tk_parent.rowconfigure(selected_widget.row, {attr: entrybox.get()})
            if row_col == 'col':
                pyte_parent.set_column_configuration(selected_widget.column, attr, entrybox.get())
                tk_parent.columnconfigure(selected_widget.row, {attr: entrybox.get()})
        # self.update_attr_frame()
        self.handles.place_selected_widget_handles(selected_widget.tk_name)

    # called when an attribute entry box lost focus or return presses
    def attr_entry_callback(self, _event, attrib, entrybox, selected_widget):
        if selected_widget is not None:
            return_value = self.pyted_core.update_widget_attribute(selected_widget,
                                                                   attrib, entrybox.get())
            # self.update_attr_frame()
            self.handles.place_selected_widget_handles(selected_widget.tk_name)
            if return_value is not None:
                messagebox.showwarning('Renaming problem',
                                       'Name already exists for another widget and Name not changed')

    # called attribute combo box enter button or lost focus
    def attr_combobox_callback(self, _event, attrib, combobox, selected_widget):
        if selected_widget is not None:
            # attr_template = self.selected_widget.attr_template[attrib]
            attr_template = selected_widget.get_input_type(attrib)
            # if attr_template[0] == pyted_widgets.BOOL_INPUT:
            if attr_template == pyted_widget_types.BOOL_INPUT:
                if combobox.get() == 'True':
                    self.pyted_core.update_widget_attribute(selected_widget, attrib, True)
                else:
                    self.pyted_core.update_widget_attribute(selected_widget, attrib, False)
            else:
                self.pyted_core.update_widget_attribute(selected_widget, attrib, combobox.get())
            # self.update_attr_frame()
            self.handles.place_selected_widget_handles(selected_widget.tk_name)
