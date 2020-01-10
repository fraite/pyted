import tkinter
import pyted.monet_widget_types as pyted_widget_types


class Widgets:
    """Widgets that form the GUI

    Holds all the widgets, including variables, that form the GUIs
    """

    def __init__(self):
        self.widget_list = []
        # Project widget
        # widget = pyted_widgets.Label()
        widget = pyted_widget_types.Project()
        widget.name = 'GuiCollection'
        widget.comment = 'a test GUI'
        self.widget_list.append(widget)
        # Top level window
        widget = pyted_widget_types.TopLevel()
        widget.name = 'gui_1'
        widget.comment = 'A demo window'
        widget.window_title = 'My demo window'
        widget.number_columns = '4'
        widget.number_rows = '4'
        widget.padx = '5'
        widget.pady = '5'
        self.widget_list.append(widget)

    def find_top_widget(self) -> pyted_widget_types.PytedGridContainerWidget:
        for pyte_widget in self.widget_list:
            try:
                if pyte_widget.type == tkinter.Toplevel:
                    return pyte_widget
            except AttributeError:
                pass
        raise Exception('No TopLevel widget defined in project')

    def find_pyte_widget_from_m_name(self, m_name) -> pyted_widget_types.PytedWidget:
        for pyte_widget in self.widget_list:
            if pyte_widget.name == m_name:
                return pyte_widget
        raise Exception(f'pyte widget with name {m_name} can not be found')

    def find_pyte_widget_from_tk(self, tk_name) -> pyted_widget_types.PytedWidget:
        for pyte_widget in self.widget_list:
            try:
                if pyte_widget.tk_name == tk_name:
                    return pyte_widget
            except AttributeError:
                pass
        raise Exception(f'pyte widget with tk_name {tk_name} can not be found')

    def find_pyte_parent(self, pyte_widget: pyted_widget_types) -> pyted_widget_types:
        """
        Find the pyte_widget that is the parent of a pyte_widget

        :param pyte_widget: the pyte widget
        :return: the pyte_widget parent
        """
        for w in self.widget_list:
            if w.name == pyte_widget.parent:
                parent_widget = w
                break
        else:
            parent_widget = None
        return parent_widget

    def find_tk_parent(self, pyte_widget: pyted_widget_types) -> tkinter.Widget:
        """
        Find the tk_widget that is the parent of a pyte_widget

        :param pyte_widget: the pyte widget
        :return: the tk_widget parent
        """

        for w in self.widget_list:
            if w.name == pyte_widget.parent:
                parent_tk_widget = w.tk_name
                break
        else:
            parent_tk_widget = None
        return parent_tk_widget

    def is_child_container(self, pyte_widget, parent_pyte_widget_name):
        """Is pyte_widget a child of parent_pyte_widget_name (or the same widget)"""
        if pyte_widget.name == self.find_top_widget().name:
            if parent_pyte_widget_name == self.find_top_widget().name:
                return True
            else:
                return False
        elif pyte_widget.name == parent_pyte_widget_name:
            return True
        elif pyte_widget.parent == self.find_top_widget().name:
            return False
        else:
            for i_pyte_widget in self.widget_list:
                if pyte_widget.parent == i_pyte_widget.name:
                    return self.is_child_container(i_pyte_widget, parent_pyte_widget_name)
            else:
                raise Exception('could not find widget with name pyte_widget.parent')

    def get_pyte_widget(self, tk_widget):
        """Get pyte widget that has tk_widget in the user form"""
        for pyte_widget in self.widget_list:
            if pyte_widget.label != 'Project':
                if tk_widget == pyte_widget.tk_name:
                    return pyte_widget
        raise Exception(f"pyte widget not found for tk widget {tk_widget}")

    def generate_unique_name(self, new_widget: pyted_widget_types) -> str:
        """
        Generate a unique name for a given widget

        Returns a unique name for a given widget, generally of in the form of the widget type and a number.

        :param new_widget: widget to be named
        :return: unique name for widget
        """
        potential_number = 1
        no_duplicate_found = False
        while not no_duplicate_found:
            for pw in self.widget_list:
                if pw.name == new_widget.label.lower() + str(potential_number):
                    potential_number = potential_number + 1
                    break
            else:
                no_duplicate_found = True
        return new_widget.label.lower() + str(potential_number)
