# Development Roadmap

Pyted is still experimental and there is much to develop.

# Development so far

Development has focused on the following goals

## Creating a GUI is easy
To keep the creating of a GUI simple

* the method of creating the GUI is similar to existing tools, i.e. drag and drop widgets
* layout is similar to other tools, e.g. Netbeans

## Using the GUI is easy

The method of saving and using the designed GUI in other code is as simple as possible

* does not rely on dependencies on non-standard Python libraries
* uses limited non-standard Python function calls, and these should be as similar as existing functions

## The GUI generated is flexible

To allow for resizing and easy layout, the Grid layout seems the best so this is supported.

# Future Development

## Tkinter variables

Tkinger variables are used to connect attributes in the bound object to widget values. The following could be improved:

* Bound object attribute names must be the same a tkinter variable names. Sometimes this may be a problem, particularly
if the bound object has nested classes leading to attributes names such as my_car.engine.size. It could be possible
to assign tkinter variable names to arbitrary object names, perhaps defaulting to the variable name if not defined.
* Tkinter variable names can only be used as variables for a small number of widget attributes. Some more general form
of linking could be devised. 

## Bound objects

Two methods exist for allowing interactive GUIs. One method is to subclass the user GUI and override the methods
corresponding to events. A second is to bind an object to the GUI. Are there any better ways?

### tkinter events in bound objects

Events bindings in tkinter are currently defined in pyted as an attribute of a widget object with each event type
held as an attribute. The attribute name corresponds to the event name and the attribute value holds the name of the
function that is called by the event. The following improvements could be made:

* The function called by the event is limited to the name of widget combined with the name of the event. Arbitrary
function names should be allowed. It is possible that the same function can be called by different widgets or events.
* existing function names defined in pyted should be in the list
* Move to a system where the events are not held as attributes but in a dictionary. Currently the attribute name is
different to the event name as many event names are not allowed as attributes, for example "return". Each event has
an attribute even if it is not bound leading to a large number of attributes needed for all possible events. A
dictionary would hold just the event name and the corresponding bound function.

### bound object discovery in pyted

At present any object can be bound to a pyted user GUI but the name of the attributes must be the same as the tkinter
variable and functions must be the same name as the events defined in pyted.

* Allow pyted to load the bound object in and offer the bound object attributes to be selected as tkinter variable names
and bound object functions to be selected as function names bound to events. This could be by passing the object as
an argument when pyted is started, or selected in the menu.

# # Misc

* allow widget attributes to be linked to a binder attribute, in the same way that tkinter variables are. This would
allow widget attributes to be initialised, changed, and read as the GUI is open
* allow widget methods to be accessed. would be needed to read and set listboxes.
* a win_close method has been implemented. a win_init method could set up widget attributes not linked to 
tkinter variables
* Allow more than one Toplevel window to be in a save file
* implement row and column span
* used pyted to design pyted's gui
* implement a help system
* split tkinter and ttk widgets in the monet_widget_types
* implement ttk themes
* implement all config options for widgets
* implement all widgets
* allow for resizing of TopLevel to be on or off
* menus
* modal dialogue boxes, probably by passing a modal=True argument when starting a user GUI
* change '_cancel' name to another name say '_cancel_or_button_pressed'. Also make it not private (remove 
  prefix '_') and add checking that pyted widgets names (including tkinter variables) do not use same names.
* represent pyted widget as a dictionary rather than a dataclass.
