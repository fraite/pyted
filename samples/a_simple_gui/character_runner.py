import character_gui as character_gui


def test_none():
    gui = character_gui.gui_1()
    print(gui)


def test_dict():
    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(my_dict)
    print(gui)


if __name__ == "__main__":

    print('Use character GUI as a simple dialogue box with no input')
    test_none()

    print('')
    print('Pass data to character gui before opening using a dict')
    test_dict()

