# Getting data in an out

There are four main methods of using a user GUI. These are:
 
1. no argument in calling function
1. argument in calling function a dict
1. argument in calling function a user class with attributes and optionally methods
1. to sub-class the user GUI, which allows nearly complete control over the user GUI. 

The methods get more powerful going down the list but also more complex to implement. 

When a user Gui is started, widgets will be filled with initial values. The user will then optionally change these
values and then close the user GUI. When the user GUI was designed in pyted each method of closing the
window could be defined as an 'OK' or 'cancel'.

Examples are shown in the samples/c_data_in_out/character_data_io.py files, with similar examples shown in the following
sections.

## No gui_binder specified

The first argument when the user GUI is invoked is the gui_binder. If no argument is specified or the gui_binder is
set to None then no gui_binder is associated with the user GUI. An example is shown below:

    import character_gui
    gui = character_gui.gui_1()
    print(gui)

The data shown in the user GUI will be the default data as defined when the user GUI was designed in pyted.
 If 'OK' was selected, then a dictionary containing the user input
will be returned. If 'cancel' is selected an empty dictionary is returned.

## Dictionary gui_binder

A dictionary can be passed as the gui_binder argument when invoking the user GUI. An example is shown below:

    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(my_dict)
    print(gui)
 
Where the keys in the dictionary match the tkinter variables set in the user GUI, the values will be used to 
initialise the tkinter variables, and any widgets associated with the tkinter variables.
 
Once the user has made their input they will close the window. If the window was closed with 'OK' then the dictionary
is updated with with the new values. The return value of the function (held in the variable gui in the example
above) will contain all the values of the tkinter variables (and widgets associated with the tkinter variables)
plus an additional dictionary item '_button' with the text for the button pressed. An example result when the above
script is run is shown.

    {'first_name': 'Fred', 'country': 'UK'}
    {'_button': 'button1', 'first_name': 'Henry', 'surname': 'Wensleydale', 'country': 'USA', 'writer': '1',
     'director': '0', 'actor': '1', 'cheese': 'Stilton'}  

If 'cancel' is pressed then the dictionary remains unchanged and an empty dictionary returned.
  
    {'first_name': 'Henry', 'country': 'USA'}
    {}

## Object gui_binder

Where the gui_binder is not a dictionary but an object with attributes, the attributes that have the same name as
the tkinter variables will be associated with each other. Also events with the same name as the events bound to widgets
will be associated with each other.

    class BoundClass:

        def __init__(self):
            self.first_name = "Ted"
            self.surname = "Wolf"
            self.cheese = 'feta'
            self.country = "USA"
            self.writer = "0"
            self.director = "0"
            self.actor = "1"

        def entry1_button_1(self, event, obj):
            self.cheese = "I've changed"

    bound_obj = BoundClass()
    gui = character_gui.gui_1(bound_obj)
    print(bound_obj.first_name)
    print(f'favourite cheese is {gui.cheese.get()}, and _cancel is {gui._cancel}')

In the above example the user GUI shows the initial values set by the object. If the user selects the entry1 widget
(the "first name" entry box) by pressing the mouse right button (button_1) then the cheese combobox will change to
"I've changed". When the box is closed 'OK' the binder object is updated with the new values and the user GUI object
is returned. Since the user Gui object is closed, only the tkinter variables remain visible. For the example above the
following result could be seen if the first name "Ted" is changed to "Fred". 
Note that if the cancel button is pressed the variable '_cancel' in the user GUI object is set to True, and if 'OK' then
which button pressed is held.

    Fred
    favourite cheese is I've changed, and _cancel is button1

If the cancel button is pressed then the binder object is not updated. The user GUI object, as changed is returned but
the '_cancel' variable is set to True.

    Ted
    favourite cheese is I've changed, and _cancel is True

## Subclass user GUI

When more control of the user GUI is required, it is possible to subclass the GUI. An example is shown below:

    class GuiCol(character_gui.GuiCollection):

        def __init__(self):
            self.label1_text = 'not set'
            super(GuiCol, self).__init__()

        def entry1_button_1(self, event, obj):
            print('entry1 button 1 pressed')
            self.label1.config(text="I've changed")

        def win_init(self):
            self.label1.config(text='new label text')
            self.first_name.set('Tom')

        def win_close(self):
            self.label1_text = self.label1.cget('text')
            print('win closed', self.label1_text)

    app = GuiCol()
    print(f'tkinter variable first name = {app.first_name.get()}, \n'
          f'attribute _cancel = {app._cancel}, attribute label1_test = {app.label1_text}')

When the above script is run a user GUI will appear. The user GUI is initialised in the win_init(self) function so
that the first name shown is 'Tom'. If the user changes the name to 'Fred' the entry1_button_1 function is activated.
Once the OK button is pressed, the following is returned:

    entry1 button 1 pressed
    win closed I've changed
    tkinter variable first name = Fred, 
    attribute _cancel = button1, attribute label1_test = I've changed

## Summary

Three easy to use methods can be used to get data into and out of a user GUI. These are limited to getting information
from widgets that have
tkinter text variables assigned to them. A summary of how the data is returned is shown below:

The returned object from the function:

input gui binder  | OK returned                                     |   cancel returned
------------|-------------------------------------------------------|-----------------------------------
None        | dict of tkinter variables + _cancel=(button pressed)  | empty dict
input dict  | dict of tkinter variables + _cancel=(button pressed)  | empty dict
user object | app + _cancel=(button pressed)                       | app + _cancel=True

The returned gui binder is set to

input gui binder  | OK returned                              |   cancel returned
------------|------------------------------------------------|-----------------------------------
None        |  None                                          | None
input dict  | updated input dict                             | original input
user object | updated user object                            | original user object

  
 By binding a user object with attributes and functions to the user GUI it is also possible to make the user GUI
 interactive.
  By subclassing the user GUI class, more control of the GUI is possible but this adds to the complexity.