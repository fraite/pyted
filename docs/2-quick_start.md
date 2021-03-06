# Pyted Quick Start

# Introduction
As the project is starting out, there is limited documentation. This quick start document aims to show some of the
 features of
the program.

# Installing the program
Download or clone the entire github repository. Make sure that Python 3.7 or a newer version is
installed on your machine.

# Running the program
Run the pyted.py script in python. The pyted GUI should appear.


![Start page](pictures/2-1-start_page.png)

# Designing a new user GUI

The pyted GUI is divided into 3 columns: the centre column shows the design frame
that the user is designing, the left column has a widget navigator that shows all the widgets in the user form, and
the right hand column shows a widget picker and a list of all attributes of the selected widget.

## Adding and deleting new widgets

To add a new widget to the design frame, select a widget from the widget picker in the top right of the program GUI.
Tabs
collect widget types together so that they can be easily found.
 
![Widget picker](pictures/2-2-added_entry-annotated.png)
 
 For example the "Label" widget is found under the
"tkinter" tab and the ttk version of the widget "TLabel" is found under the "ttk" tab. Press the "Label" button in the
"tkinter" tab and move the mouse over the design frame (the square in the centre of the program GUI
with dots). A label widget will appear under the mouse on the design frame and will move around as the user moves the
mouse. When the label is in the desired location, the left mouse is pressed and the label will be placed into the design
frame. The widget navigator on the left of the GUI will be updated to show the new widget and the list of attributes on
the right of the GUI will show a list of attributes associated with the new label widget. The mouse will go back into
pointer mode to allow widgets on the design frame to be selected.

The last placed widget will have four red handles, or if the pointer function is selected then the last selected widget,
and this denotes the widget as the selected widget. The attributes of the widget selected are shown on the right hand
side of the GUI. These attributes can be changed.

For example by selecting the first label widget created, it can be seen that the label name is "label1" and that the
text of the label is "label1". The text can be changed to say "First Name" and the name to "first_name_label".

To select a widget go to the widget picker on the top right of the pyted GUI, select the pointer button, and then select
the desired widget in the design frame. Alternatively select the widget in the widget navigator on the left of the pyted
GUI.

To delete a widget, just select the widget and press the delete key.

## Resizing the design frame grid and previewing the user form

The design frame places the widgets on a grid, with dots showing each grid position. The grid can be resized using the
number_columns and number_rows attributes for the TopLevel widget, called "gui_1" by default. Empty columns and rows are
shown in the design frame but when the design frame is used tkinter will not show empty columns and rows.
In the file menu
preview can be selected to view how the user form will look when used.

## Container widgets, row and column spanning

Row and column spanning has not yet been implemented, but the same effect can be obtained using container widgets. The
simplest container widget is the frame widget. This can be added to the user frame in the same way that
any other widget is added. The frame widget grid can be resized in the same way as the TopLevel widget by changing the
number_columns and number_rows attributes. If there are no widgets inside the frame widget, then when the user form is
previewed the frame will not be visible.

## Adding tkinter variables and associating them with widgets

Tkinter variables can be created by choosing the Project tab in the widget picker on the top right of the Pyted GUI and
selecting StringVar, which is the only tkinter variable implemented so far. When clicked a StringVar is created, as can
be seen in the widget navigator on the left of the Pyted GUI and the StringVar attributes are shown. The attributes can
be changed as desired, for example the name of the StringVar can be changed from "stringvar1" to "first_name".

The tkinter variable can then be associated to other widgets. For example create an Entry widget (or select an Entry
widget if already created on the design frame). The textvariable attribute can then be changed to any tkinter variable
created.

For the Radiobutton widget, only one Radiobutton can be selected in a group at one point in time. A group is identified
by having the same tkinter variable associated to all the Radiobutton widgets in the same group.

## Loading and Saving user forms

The created user form can then be save by going into the file menu and selecting the save menu item. Loading previously
saved user forms is also a menu item under the file menu. For example it is possible to load "character_gui.py" from
the sample directory of pyted.

![character_gui.py](pictures/2-3-character_gui.png) 

The character_gui shows the use of a number of different widgets and tkinter variables.

# Using saved user forms

The saved file is actually a Python script that can be run or loaded as a module. This script does not import any
modules other than tkinter so should not have any dependencies. Additionally this script can work with any version of
Python 3 and does not need Python 3.7 or newer. An example of a saved file is given in the "samples/a_simple_gui"
directory in the file "character_gui.py".

When the saved file is run as a script it will display the user form and then print all the tkinter variables defined.
To make use of the saved file it can be imported by another Python 3 script. There are a number of ways to do this and
these can be seen in the "character_runner.py" file, found in the sample directory.

## Adding code directly to the saved file

It is fairly simple to add python code to the gui code to add extra functionality. This has the disadvantage that if
any changes
need to be made to the GUI it will no longer be possible to use pyted to make the change. The methods below allow
changes to be made to the GUI id required in the future. The methods also promote separation
of GUI code from the logic of the program, which is generally considered good coding style.

## Dictionary dialogue box method

Once the saved file is imported, the user form can be called by a function call. For example, to use the
"python_characters.py" file in the sample directory::

    import character_gui as character_gui
    gui = character_gui.gui_1()
    print(gui)

The above example will show the python_characters gui and wait for the user to interact with the gui before
closing the gui.
Once closed, all the tkinter variables defined in the gui will be returned in the form of a dictionary. By associating
widgets with tkinter variables the states of the widgets in the gui is discovered.

The default values in the python_characters gui will be defined by the set value of the tkinter variables.

## Input dictionary dialogue box method

The input dictionary dialogue box method is similar to the dictionary dialogue box method but a dictionary object is
passed as an argument in the function to define the default values::

    import character_gui as character_gui

    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(my_dict)

The above example puts the default values in the my_dict dictionary and uses this dictionary as an argument in the
function call. The my_dict object is changed by gui_1() function and the my_dict value takes on the values as selected
by the user in the dialogue box.

By using the returned value (gui in the above example) rather than looking at the input dict (my_dict in the 
above example) the state of the gui can be reviewed, including which button has been pressed. This is can be
demonstrated by replacing the last print statement as shown below.

    import samples.character_gui as character_gui

    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(gui)

# Conclusions

The above shows some of the features of the pyted program. There are still plenty of other features and
even more features to implement.