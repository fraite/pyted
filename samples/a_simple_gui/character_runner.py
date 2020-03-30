import samples.a_simple_gui.character_gui as character_gui


def test_none():
    gui = character_gui.gui_1()
    print(gui)


def test_dict():
    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(my_dict)
    print(gui)


def test_attr():
    gui_binder = character_gui.GuiBinder()
    gui_binder.first_name = 'Henry'

    def custom_exit():
        print('closing...')

    gui_binder.win_close = custom_exit

    _gui = character_gui.gui_1(gui_binder)
    print(gui_binder.first_name)


if __name__ == "__main__":
    print('Use character gui as a simple dialogue box')
    test_none()

    print('')
    print('Pass data to character gui before opening using a dict')
    test_dict()

    print('')
    print('Pass data to character gui using an object and add in custom function for closing')
    test_attr()
