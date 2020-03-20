# Code used for save and load
import inspect
import importlib.resources as pkg_resources

from pyted import monet_widget_types
from pyted.pyted_code.widgets import Widgets


def generate_code(widgets: Widgets) -> str:
    widget_list = widgets.widget_list
    parent_widget = widget_list[0].name
    code = ''
    code = code + f'import tkinter\n'
    # TODO check to see if ttk is needed
    code = code + f'from tkinter import ttk\n'
    # code = code + f'print(ttk.Style().theme_names())\n'
    # code = code + f'print(ttk.Style().theme_use())\n'
    # code = code + f'print(ttk.Style().theme_use("clam"))\n'
    #
    code = code + f'\n'
    code = code + f'\n'

    code = code + f'class GuiBinder:\n'
    code = code + f'    """binder for {parent_widget}"""\n'
    code = code + f'\n'
    code = code + f'    def __init__(self):\n'
    code = code + f'        pass\n'

    code = build_binder_class(code, widget_list)

    # with open('init_tk_var.txt', 'r') as file:
    #     code_bit = file.read()

    code = code + f'\n'
    code = code + f'\n'
    code_bit = pkg_resources.read_text('pyted.save_load_package.code_bits', 'init_tk_var')
    code = code + code_bit
    code = code + f'\n'
    code = code + f'\n'

    code = code + f'class {parent_widget}:\n'
    code = code + f'    """{parent_widget}"""\n'
    code = code + f'\n'
    code = code + f'    def __init__(self, gui_binder=None, parent=None, modal=True):\n'
    code = code + f'        self.gui_binder = gui_binder\n'
    code = code + f'        self.parent = parent\n'

    # if no parent passed generate a root top level widow, otherwise generate a new top level window
    code = code + f'        if parent is None:\n'
    code = code + f'            root = tkinter.Tk()\n'
    code = code + f'            top_level = root\n'
    code = code + f'        else:\n'
    code = code + f'            # find root\n'
    code = code + f'            root = parent\n'
    code = code + f'            while root.master is not None:\n'
    code = code + f'                root = parent.master\n'
    code = code + f'            # generate top level window\n'
    code = code + f'            top_level = tkinter.Toplevel(parent)\n'

    code = place_widgets(code, None, widget_list)
    code = code + f'        top_level.protocol("WM_DELETE_WINDOW", self.win_close)'
    code = code + f'\n'
    code = code + f'\n'

    code_bit = pkg_resources.read_text('pyted.save_load_package.code_bits', 'widget_init_end')
    code = code + code_bit
    code = code + f'\n'
    code = code + f'\n'

    # find top level widget
    top_level_widget = None
    # TODO: change to filter
    for pyted_widget in widget_list:
        if pyted_widget.label == 'Toplevel':
            top_level_widget = pyted_widget
            break

    code_bit = pkg_resources.read_text('pyted.save_load_package.code_bits', 'win_close')
    code_bit = code_bit.replace('{top_level_name}', top_level_widget.name)
    code = code + code_bit
    code = code + f'\n'
    code = code + f'\n'

    code = code + f'def {top_level_widget.name}(gui_binder=None, parent=None, modal=True):\n'
    code = code + f'    appl = {parent_widget}(gui_binder, parent, modal)\n'
    # code = code + f'    return appl\n'
    code_bit = pkg_resources.read_text('pyted.save_load_package.code_bits', 'gui_runner_method')
    # code_bit = code_bit.replace('{top_level_name}', top_level_widget.name)
    code = code + code_bit
    code = code + f'\n'
    code = code + f'\n'

    code = code + f'if __name__ == "__main__":\n'
    # code = code + f'    root = tkinter.Tk()\n'
    # code = code + f'    app = {parent_widget}()\n'
    # code = code + f'    root.mainloop()\n'
    code = code + f'    gui = {top_level_widget.name}()\n'
    code = code + f'    print(gui)\n'
    code = code + f'\n'
    return code


def build_binder_class(code, widgets):
    # generate StringVar in init
    for pyte_widget in widgets:
        if isinstance(pyte_widget, monet_widget_types.StringVar):
            code = code + f'        self.{pyte_widget.name} = "{pyte_widget.set}"\n'
    code = code + '\n'
    # generate event methods
    for pyte_widget in widgets:
        for attr, v in pyte_widget.get_code_template().items():
            attr_template = pyte_widget.get_code_template(attr)
            if attr_template.startswith('<'):
                attr_value = getattr(pyte_widget, attr)
                if attr_value != '':
                    code = code + f'    def {attr_value}(self, obj, event):\n'
                    code = code + f'        return\n'
                    code = code + '\n'
    code = code + f'    def win_close(self):\n'
    code = code + f'        pass\n'
    return code


def place_widgets(code, m_parent_widget, widget_list):

    # top level widgets have no parents so m_parent_widget passed is None, so name will be None
    if m_parent_widget is None:
        parent_widget_name = None
    else:
        parent_widget_name = m_parent_widget.name

    for pyte_widget in widget_list:
        if pyte_widget.parent == parent_widget_name:
            code = code + f'        # new_widget({pyte_widget.label})\n'
            code = code + f'        ' + pyte_widget.generate_code()
            # add rowconfigure and columnconfigure code for container widgets
            if isinstance(pyte_widget, monet_widget_types.PytedGridContainerWidget):
                for row, row_config in pyte_widget.get_row_configuration().items():
                    code = code + f'        self.{pyte_widget.name}.rowconfigure({row}'
                    for attr, v in row_config.items():
                        code = code + f', {attr}="{v}"'
                    code = code + ')\n'
                for column, column_config in pyte_widget.get_column_configuration().items():
                    code = code + f'        self.{pyte_widget.name}.columnconfigure({column}'
                    for attr, v in column_config.items():
                        code = code + f', {attr}="{v}"'
                    code = code + ')\n'
            # add code for each attribute using attr_template to select template
            for attr, v in pyte_widget.get_code_template().items():
                attr_template = pyte_widget.get_code_template(attr)
                if attr_template == monet_widget_types.CONFIG_CODE:
                    attr_value = getattr(pyte_widget, attr)
                    if attr == 'textvariable' or attr == 'variable':
                        if attr_value != '':
                            code = code + f'        self.{pyte_widget.name}.config({attr}=self.{attr_value})\n'
                    elif isinstance(attr_value, list):
                        code = code + f'        self.{pyte_widget.name}.config({attr}={attr_value})\n'
                    else:
                        code = code + f'        self.{pyte_widget.name}.config({attr}="{attr_value}")\n'
                elif attr_template == monet_widget_types.GRID_CODE:
                    attr_value = getattr(pyte_widget, attr)
                    code = code + f'        self.{pyte_widget.name}.grid({attr}="{attr_value}")\n'
                elif attr_template == monet_widget_types.GRID_SIZE_CODE:
                    attr_value = getattr(pyte_widget, attr)
                    code = code + f'        # self.{pyte_widget.name}.grid_size({attr}="{attr_value}")\n'
                elif attr_template == monet_widget_types.TITLE_CODE:
                    attr_value = getattr(pyte_widget, attr)
                    code = code + f'        self.{pyte_widget.name}.title("{attr_value}")\n'

                elif attr_template == monet_widget_types.GRID_CODE:
                    pass
                    # if self.selected_widget is None:
                    #     # not moving widget
                    #     if attr == 'row':
                    #         tk_widget.grid(row=getattr(pyte_widget, attr))
                    #     elif attr == 'column':
                    #         tk_widget.grid(column=getattr(pyte_widget, attr))
                    # else:
                    #     # TODO: implement grid moving
                    #     print('trying to move grid, or resize grid, but not implemented')
                elif attr_template == monet_widget_types.BESPOKE_CODE and attr == 'remove':
                    attr_value = getattr(pyte_widget, attr)
                    if attr_value:
                        code = code + f'        self.{pyte_widget.name}.grid_remove()\n'
                elif attr_template == monet_widget_types.VAR_SET_CODE:
                    code = code + f'        self.{pyte_widget.name}.set("{pyte_widget.set}")\n'
                    code = code + f'        init_tk_var(self.{pyte_widget.name}, gui_binder,' \
                                  f' "{pyte_widget.name}")\n'
                elif attr_template.startswith('<'):
                    # print(pyte_widget.name, attr_template, getattr(pyte_widget, attr))
                    event_method = getattr(pyte_widget, attr)
                    if event_method != '':
                        code = code + f'        if gui_binder is not None and not isinstance(gui_binder, dict):\n'
                        code = code + f'            self.{pyte_widget.name}.bind("{attr_template}", lambda\n' \
                                      f'                             event, arg1=self.{pyte_widget.name}:\n' \
                                      f'                             gui_binder.{event_method}(event, arg1))\n'
            if (isinstance(pyte_widget, monet_widget_types.PytedGridContainerWidget) and
                    isinstance(m_parent_widget, monet_widget_types.Notebook)):
                tab_text = getattr(pyte_widget, 'tab_text')
                code = code + f'        self.{parent_widget_name}.add(self.{pyte_widget.name}, text="{tab_text}")\n'
            if (isinstance(pyte_widget, monet_widget_types.PytedGridContainerWidget) or
                    isinstance(pyte_widget, monet_widget_types.Project) or
                    isinstance(pyte_widget, monet_widget_types.Notebook)):
                code = place_widgets(code, pyte_widget, widget_list)
    return code


def parse_code(f):
    # widgets = []
    current_class = None

    # ignore imports and blank lines
    while True:
        current_line = f.readline()
        if current_line.startswith('import') or current_line.startswith('from'):
            pass
        elif current_line.strip() == '':
            pass
        else:
            break

    # read in the class statement for the binder class
    if current_line.startswith('class'):
        pass
    else:
        raise Exception('binder class statement not in correct location')

    f.readline()

    # ignore binder class and any other lines until GUI class starts
    while True:
        current_line = f.readline()
        if current_line.startswith('class'):
            break

    # read in the class statement
    if current_line.startswith('class'):
        for word in current_line[5:].split():
            if current_class is None:
                current_class = word[:-1]
    else:
        raise Exception('class statement not in correct location')

    # read in the comment
    current_line = f.readline()
    if current_line.startswith('    """'):
        current_line2 = current_line.strip()
        comment = current_line2[3:-3]
    else:
        raise Exception('comment statement not in correct location')

    # read in blank line
    current_line = f.readline()
    current_line2 = current_line.strip()
    if not current_line2 == '':
        raise Exception('blank line should follow class comment')

    # read in the def __init__(self, parent) line
    current_line = f.readline()
    if current_line[:22] == '    def __init__(self,':
        pass
    else:
        raise Exception('def __init__ statement not in correct location: ', current_line[:22])

    # read next line, but ignore comments and blank lines
    while True:
        current_line = f.readline()
        if current_line.startswith('    """'):
            pass
        elif current_line.strip() == '':
            pass
        else:
            break

    widgets = []
    # TODO: use one loop to load all types of widgets
    # create project using information above
    current_line2 = current_line.strip()
    if current_line2 == 'self.gui_binder = gui_binder':
        pass
    else:
        raise Exception('"self.gui_binder = gui_binder" missing')
    current_line = f.readline()
    current_line2 = current_line.strip()
    # if current_line2 == 'self.parent = parent':
    #     pass
    # else:
    #     raise Exception('"self.parent = parent" missing')
    while current_line2 != '# new_widget(Project)':
        current_line = f.readline()
        current_line2 = current_line.strip()
    if current_line2 == '# new_widget(Project)':
        pass
    else:
        raise Exception('project comment missing')
    current_line = f.readline()
    current_line2 = current_line.strip()
    if current_line2 == '# project_name = ' + current_class + '':
        pass
    else:
        raise Exception('project widget not set up correctly')
    widget = monet_widget_types.Project()
    widget.name = current_class
    widgets.append(widget)

    # load variables
    current_line = f.readline()
    current_line2 = current_line.strip()
    while not current_line2.startswith('# new_widget(Toplevel)'):
        if current_line2.startswith('# new_widget('):
            widget_label = current_line2[13:-1]
            for name, obj in inspect.getmembers(monet_widget_types):
                if inspect.isclass(obj) and obj:
                    try:
                        obj_label = obj.label
                    except AttributeError:
                        obj_label = None
                    if widget_label == obj_label:
                        widget = obj()
                        break
            else:
                raise Exception('widget label not found')
        else:
            raise Exception('did not start with comment describing next widget}')
        current_line = f.readline()
        current_line2 = current_line.strip()
        if current_line2.startswith('self.'):
            widget.name = current_line2.split(' ')[0].split('.')[1]
            # widget.parent = current_line2.split('=')[1].split('.')[2][:-1]
            widget.parent = current_class
        else:
            raise Exception('line to create widget does not start with self.')
        current_line = f.readline()
        current_line2 = current_line.strip()
        while current_line2.startswith('self.') or current_line2.startswith('# self.'):
            load_widget_attr(f, widget, current_line2)
            current_line = f.readline()
            current_line2 = current_line.strip()
            # ignore any blank lines or init_tk_var lines
            while current_line2 == '' or current_line2.startswith('init_tk_var'):
                current_line = f.readline()
                current_line2 = current_line.strip()
        widgets.append(widget)

    # create top level widget using information above
    # current_line = f.readline()
    # current_line2 = current_line.strip()
    if current_line2 == '# new_widget(Toplevel)':
        pass
    else:
        raise Exception('top level comment missing:', current_line2)
    current_line = f.readline()
    current_line2 = current_line.strip()
    # if current_line2 == 'self.' + current_class + ' = parent':
    #     pass
    # else:
    #     raise Exception('top level widget not set up correctly')
    if current_line2.startswith('self.'):
        toplevel_name = current_line2.split(' ')[0].split('.')[1]
    else:
        raise Exception('line to create toplevel does not start with self.')

    widget = monet_widget_types.TopLevel()
    widget.name = toplevel_name
    widget.comment = comment
    # read in top level widget attributes
    current_line = f.readline()
    while current_line:
        current_line2: str = current_line.strip()
        if current_line2.strip() == '':
            pass
        elif current_line2.startswith('self.' + toplevel_name) or current_line2.startswith('# self.' + toplevel_name):
            if current_line2.startswith('# '):
                current_line2 = current_line2[2:]
            current_line2 = current_line2[len('self.' + toplevel_name + '.'):]
            if current_line2.startswith(monet_widget_types.CONFIG_CODE):
                method_name_length = len(monet_widget_types.CONFIG_CODE) + 1
                attr_name = current_line2[method_name_length:-1].split('=')[0]
                attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
                setattr(widget, attr_name, attr_value)
            elif (current_line2.startswith(monet_widget_types.GRID_CODE) and
                  not current_line2.startswith(monet_widget_types.GRID_SIZE_CODE)):
                method_name_length = len(monet_widget_types.GRID_CODE) + 1
                attr_name = current_line2[method_name_length:-1].split('=')[0]
                attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
                setattr(widget, attr_name, attr_value)
            elif current_line2.startswith(monet_widget_types.GRID_SIZE_CODE):
                method_name_length = len(monet_widget_types.GRID_SIZE_CODE) + 1
                attr_name = current_line2[method_name_length:-1].split('=')[0]
                attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
                setattr(widget, attr_name, attr_value)
            elif current_line2.startswith(monet_widget_types.TITLE_CODE):
                widget.window_title = current_line2[7:-2]
            elif current_line2.startswith(monet_widget_types.ROW_CONFIGURE):
                current_line2 = current_line2[len(monet_widget_types.ROW_CONFIGURE) + 1:]
                row = current_line2.split(',')[0]
                current_line2 = current_line2[len(row) + 2:-1]
                for args in current_line2.split(','):
                    attr = args.strip().split('=')[0]
                    val = args.strip().split('=')[1][1:-1]
                    widget.set_row_configuration(row, attr, val)
            elif current_line2.startswith(monet_widget_types.COLUMN_CONFIGURE):
                current_line2 = current_line2[len(monet_widget_types.COLUMN_CONFIGURE) + 1:]
                column = current_line2.split(',')[0]
                current_line2 = current_line2[len(column) + 2:-1]
                for args in current_line2.split(','):
                    attr = args.strip().split('=')[0]
                    val = args.strip().split('=')[1][1:-1]
                    widget.set_column_configuration(column, attr, val)
        else:
            break
        current_line = f.readline()
    widgets.append(widget)

    # read in other widgets
    while not current_line2.startswith('top_level.protocol') and not current_line2.startswith('def'):
        if current_line2.startswith('# new_widget('):
            widget_label = current_line2[13:-1]
            for name, obj in inspect.getmembers(monet_widget_types):
                if inspect.isclass(obj) and obj:
                    obj_label = getattr(obj, 'label', None)
                    if widget_label == obj_label:
                        widget = obj()
                        break
            else:
                raise Exception('widget label not found')
        else:
            raise Exception(f'did not start with comment describing next widget: {current_line2}')
        current_line = f.readline()
        current_line2 = current_line.strip()
        if current_line2.startswith('self.'):
            widget.name = current_line2.split(' ')[0].split('.')[1]
            widget.parent = current_line2.split('=')[1].split('.')[2][:-1]
        else:
            raise Exception('line to create widget does not start with self.')
        current_line = f.readline()
        current_line2 = current_line.strip()
        while current_line2.startswith('self.') or current_line2.startswith('# self.'):
            if current_line2.startswith(f'self.{widget.parent}.add(self.{widget.name}, text="'):
                # adding frame to notebook
                tab_text = current_line2.split('="')[1].split('"')[0]
                setattr(widget, 'tab_text', tab_text)
            else:
                load_widget_attr(f, widget, current_line2)
            current_line = f.readline()
            current_line2 = current_line.strip()
            while current_line2 == '' or current_line2.startswith("if gui_binder is not None and not"):
                current_line = f.readline()
                current_line2 = current_line.strip()
        widgets.append(widget)

    return widgets


def load_widget_attr(f, widget, current_line2):
    # remove comment symbols used to denote pseudo python code
    if current_line2.startswith('# '):
        current_line2 = current_line2[2:]
    # remove self.widget_name. to get tkinter command
    current_line2 = current_line2[len('self.' + widget.name + '.'):]
    # decode tkinger command
    if current_line2.startswith(monet_widget_types.CONFIG_CODE + '('):
        method_name_length = len(monet_widget_types.CONFIG_CODE) + 1
        attr_name = current_line2[method_name_length:-1].split('=')[0]
        if attr_name == 'textvariable' or attr_name == 'variable':
            attr_value = current_line2[method_name_length:-1].split('=')[1][5:]
        elif current_line2[method_name_length:-1].split('=')[1].startswith('['):
            # list found
            attr_value = []
            for item in current_line2[method_name_length:-1].split('=')[1][1:-1].split(', '):
                attr_value.append(item[1:-1])
        else:
            # assume it is a string
            attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
        setattr(widget, attr_name, attr_value)
    elif current_line2.startswith(monet_widget_types.GRID_CODE + '('):
        method_name_length = len(monet_widget_types.GRID_CODE) + 1
        attr_name = current_line2[method_name_length:-1].split('=')[0]
        attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
        setattr(widget, attr_name, attr_value)
    elif current_line2.startswith(monet_widget_types.GRID_SIZE_CODE + '('):
        method_name_length = len(monet_widget_types.GRID_SIZE_CODE) + 1
        attr_name = current_line2[method_name_length:-1].split('=')[0]
        attr_value = current_line2[method_name_length:-1].split('=')[1][1:-1]
        setattr(widget, attr_name, attr_value)
    elif current_line2.startswith(monet_widget_types.GRID_REMOVE + '('):
        setattr(widget, 'remove', True)
    elif current_line2.startswith(monet_widget_types.VAR_SET_CODE + '('):
        method_name_length = len(monet_widget_types.VAR_SET_CODE) + 1
        attr_value = current_line2[method_name_length+1:-2]
        setattr(widget, monet_widget_types.VAR_SET_CODE, attr_value)
    elif current_line2.startswith(monet_widget_types.BIND_CODE + '('):
        method_name_length = len(monet_widget_types.BIND_CODE) + 1
        event = current_line2.split(',')[0][method_name_length+1:-1]
        attr_name = widget.get_attr_from_template(event)
        f.readline()  # read and ignore "event, arg1=self." line
        current_line = f.readline()
        current_line2 = current_line.strip()
        current_line2 = current_line2.split('.')[1]
        bind_function = current_line2.split('(')[0]
        setattr(widget, attr_name, bind_function)
    elif current_line2.startswith(monet_widget_types.ROW_CONFIGURE):
        current_line2 = current_line2[len(monet_widget_types.ROW_CONFIGURE) + 1:]
        row = current_line2.split(',')[0]
        current_line2 = current_line2[len(row) + 2:-1]
        for args in current_line2.split(','):
            attr = args.strip().split('=')[0]
            val = args.strip().split('=')[1][1:-1]
            widget.set_row_configuration(row, attr, val)
    elif current_line2.startswith(monet_widget_types.COLUMN_CONFIGURE):
        current_line2 = current_line2[len(monet_widget_types.COLUMN_CONFIGURE) + 1:]
        column = current_line2.split(',')[0]
        current_line2 = current_line2[len(column) + 2:-1]
        for args in current_line2.split(','):
            attr = args.strip().split('=')[0]
            val = args.strip().split('=')[1][1:-1]
            widget.set_column_configuration(column, attr, val)
    else:
        raise Exception('save_load_package.py>load_widget_attr> ' + widget.name + '> ' + current_line2)
    return
