import character_gui as character_gui


def test_none():
    gui = character_gui.gui_1()
    print(gui)


def test_dict():
    my_dict = {'first_name': 'Henry', 'country': 'USA'}
    gui = character_gui.gui_1(my_dict)
    print(my_dict)
    print(gui)


def test_bound_object():

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


def test_sub_class():

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


if __name__ == "__main__":

    print('Use character GUI as a simple dialogue box with no input')
    test_none()

    print('')
    print('Pass data to character gui before opening using a dict')
    test_dict()

    print('')
    print('pass bound object to character gui')
    test_bound_object()

    print('')
    print('Subclass the GuiCollection class, and use the subclass')
    test_sub_class()
