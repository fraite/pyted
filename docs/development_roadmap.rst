===================
Development Roadmap
===================

Pyted is still experimental and there is much to develop.

Development so far
==================

Development has focused on the following goals

Creating a GUI is easy
----------------------
To keep the creating of a GUI simple

* the method of creating the GUI is similar to existing tools, i.e. drag and drop widgets
* layout is similar to other tools, e.g. Netbeans

Using the GUI is easy
---------------------

The method of saving and using the designed GUI in other code is as simple as possible

* does not rely on dependencies on non-standard Python libraries
* uses limited non-standard Python function calls, and these should be as similar as existing functions

The GUI generated is flexible
-----------------------------

To allow for resizing and easy layout, the Grid layout seems the best so this is supported. Currently only modal GUI
windows can be generated. Can this be improved?

Future Development
==================

* Allow more than one Toplevel window to be in a save file
* review widget placement method, perhaps revert to pointer mode once widget is placed unless toolbox double clicked?
* implement row and column span
* improve how events are handled, can an OK / Cancel button be easily implemented?
* used pyted to design pyted's gui
* implement modeless dialogue boxes
* implement a help system
* split tkinter and ttk widgets
* implement ttk themes
* implement all config options for widgets
* implement all widgets