import temperature_conversion as tc

class GuiBinder:
    """binder for GuiCollection"""

    def __init__(self):
        pass
        self.temperature_c = ""
        self.temperature_f = ""

    def entry_c_return_(self, event, obj):
        self.convert_c_to_f()

    def entry_c_focus_out(self, event, obj):
        self.convert_c_to_f()

    def entry_f_return_(self, event, obj):
        self.convert_f_to_c()

    def entry_f_focus_out(self, event, obj):
        self.convert_f_to_c()

    def win_close(self):
        return

    def convert_c_to_f(self):
        try:
            self.temperature_f = round(float(self.temperature_c) * 9/5 + 32, 2)
        except ValueError:
            pass

    def convert_f_to_c(self):
        try:
            self.temperature_c = round((float(self.temperature_f) - 32)
                                       * 5/9, 2)
        except ValueError:
            pass

def test_event():
    gui_binder = GuiBinder()
    app = tc.gui_1(gui_binder=gui_binder)


if __name__ == "__main__":

    test_event()