# Starting the user GUI

The saved pyted user GUI file includes a helper function to allow the user GUI to be displayed easily. It also provides
basic functionality to get data into and out of the user GUI. The name of the helper function is the name of the
TopLevel widget given in pyted.

To start a user GUI, the module containing the user GUI is imported and then the helper function is run, remembering
 that the name of the function is the TopLevel widget name in pyted. In the future it is possible that more than one
user GUI can sit within a single module. The following script shows an example:

    import character_gui
    gui = character_gui.gui_1()

By passing some optional arguments into the gui_1() method above the way user GUI starts can be altered. The following
arguments can be used.

* parent - assigns the user GUI to be the child of tkinter widget given (default None, the user GUI will be
 a new root widget with no parent)
* mainloop - if set to True the window will enter into the tkinter mainloop and the window will have to be closed before
  the python script continues. If False then the python script will continue. The user must arrange for the tkinter
  mainloop to be started. Does not fully work yet.
* frame - rather than a new TopLevel window being created, the user GUI will be placed in the frame or Toplevel widget
  specified. The mainloop flag is ignored and the user must ensure that tkinter mainloop is implemented.

In the future some form of modal dialogue boxes may be implemented.