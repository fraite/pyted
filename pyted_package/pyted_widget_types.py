"""
Class definitions for each pyted widget type.

Information for each pyted widget type is held in an object, with the class of the object being defined in this module.
The classes used are dataclasses. See the docstring for the base class, PytedWidget, on how the fields in the
dataclasses are used to hold information on each tkinter widget attribute. As stated, the base class is:

* PytedWidget: the base class, that is used as a base for all other widgets

There are 2 subclasses that can then be used as a base class for other widgets:

* PytedContainerWidget: the base class for widgets that can be used as containers for other widgets
* PytedPlacedWidget: the base class for widgets that can be placed on a grid

The classes that are used for each widget are based on the above base classes. Note that multiple inheritance allows
for more than one base class to be used. The classes are:

* Project: used to describe the gui collection
* StringVar: corresponds to tkinter StringVar
* .
* the widgets in between correspond to tkinter widgets
* .
* Frame: corresponds to tkinter Frame
"""

import tkinter
from dataclasses import dataclass, field, fields

# the tkinter command to remove a widget from the grid
GRID_REMOVE = 'grid_remove'

# input type for attribute, for example 'relief' is SINGLE_OPTION, that is a single value from a list options
NO_INPUT = 'no input'                           # the attribute will be hidden from the user as there is no input
SINGLE_INPUT = 'single input'                   # single input in the form of text
BOOL_INPUT = 'bool input'                       # input is True or False
SINGLE_OPTION = 'single option'                 # single input from a list of options
MULTI_OPTION = 'multi option'                   # multiple inputs from a list of options
PARENT_OPTION = 'parent option'                 # single input from a list of available container widgets
COLOR_OPTION = 'color option'                   # single input from a list of available colors
LIST_OPTION = 'list option'                     # not sure where used
STRING_VAR_OPTION = 'string var option'         # single input from a list of available string vars
STRING_EVENT_OPTION = 'string event option'     # single input for a string event option

# tkinter code or pseudo code used to set set the attribute, for example 'relief' uses the 'config' method
BESPOKE_CODE = 'bespoke'
CONFIG_CODE = 'config'
GRID_CODE = 'grid'
GRID_SIZE_CODE = 'grid_size'
TITLE_CODE = 'title'
VAR_SET_CODE = 'set'
BIND_CODE = 'bind'
ROW_CONFIGURE = 'rowconfigure'
COLUMN_CONFIGURE = 'columnconfigure'


def make_empty_dict():
    """A factory method to return an empty dictionary.

    :return: and empty dictionary
    """

    return {}


@dataclass()
class PytedWidget:
    """
    Base dataclass for all Pyted widgets.

    Information for each Pyted widget type is held in an object, with a field holding information for each widget
    attribute. The dataclass fields generally have metadata attached to fields and are described below:

    * type: input type, for example SINGLE_OPTION is a single input from a list of options
    * template: the tkinter code or pseudo code used set the attribute
    * options: the list of options for SINGLE_OPTION or MULTI_OPTION input types

    Class methods are defined to allow easy access to the metadata. These class methods are:

    * get_input_type(attr): get the type metadata for the attribute given
    * get_code_template(attr): get the template metadata for the attribute given
    * get_input_options(attr): get the options metadata for the attribute given
    * get_attr_from_template(template): get the attribute that use the (event) template given

    Class fields split into class fields that remain the same for all widgets of the same class, and instance fields
    that hold specific information for each widget. The class fields are:

    * type: the tkinter class of the widget. This field is over-ridden by all widgets but is included to prevent lint
            type checking errors

    The instance fields are:

    * name: the pyted name of the widget
    * parent: the pyted name of the parent widget that contains the widget
    * tk_name: the name assigned by tkinter to the widget for the GUI editing phase
    """

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default='PytedWidget', init=False)  # over-ridden, needed to prevent lint type checking error

    # instance attributes
    name: str = field(default=None, metadata={'type': SINGLE_INPUT, 'template': BESPOKE_CODE, 'options': None})
    parent: str = field(default=None, metadata={'type': NO_INPUT, 'template': BESPOKE_CODE, 'options': None})
    tk_name: tkinter.Widget = field(default=None, metadata={'type': NO_INPUT, 'template': BESPOKE_CODE,
                                                            'options': None})

    def get_input_type(self, attr: str = None):
        """
        Get the input type of the widget attribute.

        Gets the input type for the widget attribute that is encoded in the field metadata. The types of input are
        defined at the start of this module and common ones are SINGLE_INPUT, SINGLE_OPTION, MULTI_INPUT AND NO_INPUT.
        For example the title attribute of a TopLevel object is SINGLE_INPUT and uses a text box to get a single item.
        If NO_INPUT is defined, then the attribute is hidden from the user.

        If no widget attribute is defined, then a list of all input types used by all the attributes of the widget is
        returned.

        :param attr: the widget attribute
        :return: input type of widget attribute, or list of all input types for all attributes of the widget
        """

        input_type_dict = {}
        for i_field in fields(self):
            try:
                input_type_dict[i_field.name] = i_field.metadata['type']
            except KeyError:
                pass
        if attr is None:
            return input_type_dict
        else:
            return input_type_dict[attr]

    def get_code_template(self, attr: str = None):
        """
        Get the code template for the attribute of the widget.

        Gets the code template type for the widget attribute that is encoded in the field metadata. The code template
        type is used by the save function to define how the attribute is encoded by tkinter. The available code
        templates are defined at the start of this module. Example code templates are CONFIG_CODE, GRID_CODE and
        BESPOKE_CODE. For example CONFIG_CODE is used to generate tkinter code for config methods. BESPOKE_CODE uses
        bespoke python code to configure the attribute.

        If no widget attribute is defined, then a list of all code templates used by all the attributes of the widget is
        returned.

        :param attr: the widget attribute
        :return: code template used by the widget attribute, or list of all code templates used by the widget
        """
        code_template_dict = {}
        for i_field in fields(self):
            try:
                code_template_dict[i_field.name] = i_field.metadata['template']
            except KeyError:
                pass
        if attr is None:
            return code_template_dict
        else:
            return code_template_dict[attr]

    def get_input_options(self, attr: str):
        # TODO: may need some error checking if attr has no options
        input_options_dict = {}
        for i_field in fields(self):
            try:
                input_options_dict[i_field.name] = i_field.metadata['options']
            except KeyError:
                pass
        if attr is None:
            return input_options_dict
        else:
            return input_options_dict[attr]

    def get_attr_from_template(self, template: str):
        """Returns the attribute with the specified template"""
        # TODO: may need some error checking if attr has no options
        attr_dict = {}
        for i_field in fields(self):
            try:
                attr_dict[i_field.metadata['template']] = i_field.name
            except KeyError:
                pass
        if template is None:
            return attr_dict
        else:
            return attr_dict[template]


#
# PytedContainerWidget
#
@dataclass()
class PytedContainerWidget(PytedWidget):
    """Parent class for pyted container widgets

    """

    # instance attributes
    number_columns: int = field(default=2, metadata={'type': SINGLE_INPUT, 'template': GRID_SIZE_CODE, 'options': None})
    number_rows: int = field(default=2, metadata={'type': SINGLE_INPUT, 'template': GRID_SIZE_CODE, 'options': None})

    # instance attributes
    _row_configure: dict = field(default_factory=make_empty_dict,
                                 metadata={'type': NO_INPUT, 'template': ROW_CONFIGURE, 'options': None})
    _col_configure: dict = field(default_factory=make_empty_dict,
                                 metadata={'type': NO_INPUT, 'template': ROW_CONFIGURE, 'options': None})

    def get_row_configuration(self, row=None) -> dict:
        """
        Get the row configuration for the container

        Gets a dictionary containing the row configuration data of the given row for the container object. The row
        configuration data is used by the row_configuration method in tkinter. The following dictionary attributes are
        available:

        * minsize: the minimum size of the row
        * weight: the relative weight used for resizing the row
        * pad: the row padding

        :param row: the row in the grid
        :return: row configuration data
        """

        if row is None:
            return self._row_configure
        else:
            try:
                row_config = self._row_configure[row]
            except KeyError:
                row_config = {'minsize': '0', 'weight': '1', 'pad': '0'}
                self._row_configure[row] = row_config
            return row_config

    def set_row_configuration(self, row, attr, value) -> None:
        """Set a row configuration attribute for the container

        Sets a row configuration item for the given row in the the container object to the value given. Valid attribute
        types are:

        * minsize: the minimum size of the row
        * weight: the relative weight used for resizing the row
        * pad: the row padding
        """
        try:
            row_config = self._row_configure[row]
        except KeyError:
            row_config = {'minsize': '0', 'weight': '1', 'pad': '0'}
        row_config[attr] = value
        self._row_configure[row] = row_config

    def get_column_configuration(self, col=None) -> dict:
        """
        Get the column configuration for the container

        Gets a dictionary containing the column configuration data of the given column for the container object. The row
        configuration data is used by the col_configuration method in tkinter. The following dictionary attributes are
        available:

        * minsize: the minimum size of the row
        * weight: the relative weight used for resizing the row
        * pad: the row padding

        :param col: the col in the grid
        :return: col configuration data
        """

        if col is None:
            return self._col_configure
        else:
            try:
                col_config = self._col_configure[col]
            except KeyError:
                col_config = {'minsize': '0', 'weight': '1', 'pad': '0'}
                self._col_configure[col] = col_config
            return col_config

    def set_column_configuration(self, col, attr, value) -> None:
        """Set a column configuration attribute for the container

        Sets a column configuration item for the given column in the the container object to the value given. Valid
        attribute types are:

        * minsize: the minimum size of the row
        * weight: the relative weight used for resizing the row
        * pad: the row padding
        """
        try:
            col_config = self._col_configure[col]
        except KeyError:
            col_config = {'minsize': '0', 'weight': '1', 'pad': '0'}
        col_config[attr] = value
        self._col_configure[col] = col_config


@dataclass()
class PytedPlacedWidget(PytedWidget):
    """Parent class for placed pyted widgets

    """

    # instance attributes
    column: int = field(default=None, metadata={'type': SINGLE_INPUT, 'template': GRID_CODE, 'options': None})
    row: int = field(default=None, metadata={'type': SINGLE_INPUT, 'template': GRID_CODE, 'options': None})
    sticky: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': GRID_CODE, 'options': None})
    remove: bool = field(default=False, metadata={'type': BOOL_INPUT, 'template': BESPOKE_CODE,
                                                  'options': (True, False)})


#
# Project
#
@dataclass()
class Project(PytedWidget):
    """Data for TopLevel widget

    This Dataclass holds information for the project instance. Attributes hold the information for the project and
    metadata is used to describe the type of attribute. The metadata is

    type: the input type of attribute, for example SINGLE_OPTION attributes have a single value from a range of options
    template: the python code type used to display the attribute
    options: the valid options the attribute can hold
    """

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default='project', init=False)
    tab: str = field(default='Project', init=False)
    label: str = field(default='Project', init=False)
    is_on_toolbox: bool = field(default=False, init=False)
    is_widget: bool = field(default=False, init=False)

    # instance attributes
    comment: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': BESPOKE_CODE, 'options': None})

    def generate_code(self):
        # TODO: sort out if and how Project & TopLevel is used
        # code = f'self.{self.name} = tkinter.TopLevel(parent)\n'
        code = f'# project_name = {self.name} \n'
        return code


#
# Tkinter StringVar
#
@dataclass()
class StringVar(PytedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.StringVar, init=False)
    tab: str = field(default='Project', init=False)
    label: str = field(default='StringVar', init=False)
    is_on_toolbox: bool = field(default=True, init=False)
    is_var: bool = field(default=True, init=False)
    is_widget: bool = field(default=False, init=False)

    # instance attributes
    set: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': VAR_SET_CODE, 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.StringVar()\n'
        return code


#
# Tkinter TopLevel
#
@dataclass()
class TopLevel(PytedContainerWidget):
    """Data for TopLevel widget

    This Dataclass holds information for a TopLevel widget instance. Attributes hold the information for the widget and
    metadata is used to describe the type of attribute. The metadata is

    type: the input type of attribute, for example SINGLE_OPTION attributes have a single value from a range of options
    template: the python code type used to display the attribute
    options: the valid options the attribute can hold
    """

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Toplevel, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Toplevel', init=False)
    is_on_toolbox: bool = field(default=False, init=False)

    # instance attributes
    comment: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': BESPOKE_CODE, 'options': None})
    window_title: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': TITLE_CODE, 'options': None})
    # padx: str = field(default='0', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    # pady: str = field(default='0', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.FLAT, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                        'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                    tkinter.GROOVE)})

    def generate_code(self):
        # TODO: Sort out if and how TopLevel is used
        # code = f'self.{self.name} = tkinter.TopLevel(parent)\n'
        code = f'self.{self.name} = top_level\n'
        return code


#
# TTK Label
#
@dataclass()
class Label(PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Label, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Label', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    anchor: str = field(default=tkinter.E, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                     'options': (tkinter.N, tkinter.NE, tkinter.E, tkinter.SE,
                                                                 tkinter.S, tkinter.SW, tkinter.W, tkinter.NW,
                                                                 tkinter.CENTER)})
    borderwidth: str = field(default='0', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.FLAT, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                        'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                    tkinter.GROOVE)})
    text: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    underline: str = field(default='0', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Label(self.{self.parent})\n'
        return code


#
# TTK Entry
#
@dataclass()
class Entry(PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Entry, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Entry', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    borderwidth: str = field(default='2', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.SUNKEN, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                          'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                      tkinter.GROOVE)})
    textvariable: str = field(default='', metadata={'type': STRING_VAR_OPTION, 'template': CONFIG_CODE,
                                                    'options': None})
    button_1: str = field(default='', metadata={'type': STRING_EVENT_OPTION, 'template': '<Button-1>', 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Entry(self.{self.parent})\n'
        return code


#
# TTK Button
#
@dataclass()
class Button(PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Button, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Button', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    borderwidth: str = field(default='2', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.RAISED, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                          'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                      tkinter.GROOVE)})
    text: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    button_1: str = field(default='', metadata={'type': STRING_EVENT_OPTION, 'template': '<Button-1>', 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Button(self.{self.parent})\n'
        return code


#
# TTK Radiobutton
#
@dataclass()
class Radiobutton(PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Radiobutton, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Radiobutton', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    borderwidth: str = field(default='2', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.FLAT, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                        'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                    tkinter.GROOVE)})
    value: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    text: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    variable: str = field(default='', metadata={'type': STRING_VAR_OPTION, 'template': CONFIG_CODE,
                                                'options': None})
    button_1: str = field(default='', metadata={'type': STRING_EVENT_OPTION, 'template': '<Button-1>', 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Radiobutton(self.{self.parent})\n'
        return code


#
# TTK Checkbutton
#
@dataclass()
class Checkbutton(PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Checkbutton, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Checkbutton', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    borderwidth: str = field(default='2', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.FLAT, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                        'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                    tkinter.GROOVE)})
    onvalue: str = field(default='1', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    offvalue: str = field(default='0', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    text: str = field(default='', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    variable: str = field(default='', metadata={'type': STRING_VAR_OPTION, 'template': CONFIG_CODE,
                                                'options': None})
    button_1: str = field(default='', metadata={'type': STRING_EVENT_OPTION, 'template': '<Button-1>', 'options': None})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Checkbutton(self.{self.parent})\n'
        return code


#
# TTK Frame
#
@dataclass()
class Frame(PytedContainerWidget, PytedPlacedWidget):

    # class attributes (or as close as we can get to class attributes)
    type: type = field(default=tkinter.Frame, init=False)
    tab: str = field(default='tkinter', init=False)
    label: str = field(default='Frame', init=False)
    is_on_toolbox: bool = field(default=True, init=False)

    # instance attributes
    borderwidth: str = field(default='2', metadata={'type': SINGLE_INPUT, 'template': CONFIG_CODE, 'options': None})
    relief: str = field(default=tkinter.GROOVE, metadata={'type': SINGLE_OPTION, 'template': CONFIG_CODE,
                                                          'options': (tkinter.FLAT, tkinter.RAISED, tkinter.SUNKEN,
                                                                      tkinter.GROOVE)})

    def generate_code(self):
        code = f'self.{self.name} = tkinter.Frame(self.{self.parent})\n'
        return code
