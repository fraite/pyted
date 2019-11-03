import tkinter
import samples.python_actors as python_actors


class GuiBinder:
    """binder for GuiCollection"""

    def __init__(self):
        pass
        self.first_name = ""
        self.surname = ""
        self.country = "UK"
        self.writer = "1"
        self.director = "0"
        self.actor = "1"

    @staticmethod
    def entry1_button_1(_obj, _event):
        print('Entry')

    @staticmethod
    def win_close():
        print('Win close')


def test_event():
    root = tkinter.Tk()
    gui_binder = GuiBinder()
    _app = python_actors.gui_1(root, gui_binder)
    root.mainloop()


def test_attr():
    gui_binder = GuiBinder()
    gui_binder.first_name = 'First Name'
    _app = python_actors.gui_1(gui_binder)
    print(gui_binder.first_name)


def test_dict():
    my_dict = {'first_name': 'Terry', 'country': 'USA'}
    app = python_actors.gui_1(my_dict)
    print(my_dict)
    print(app)


def test_none():
    app = python_actors.gui_1()
    print(app)


if __name__ == "__main__":
    print('Use python_actors gui as a simple dialogue box')
    test_none()

    print('')
    print('Use python_actors gui as a more complex dialogue box')
    test_dict()

    print('')
    print('Pass a bespoke object as an argument to the dialogue box')
    test_attr()
