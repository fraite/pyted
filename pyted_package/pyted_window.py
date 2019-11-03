import tkinter
from tkinter import ttk


class PytedWindow:
    """The toolbox panel"""

    def __init__(self, root, pyte_code):
        self.pyte_code = pyte_code
        self.win = root
        self.win.title('Pyted')
        root.bind('<Escape>', pyte_code.escape_key_callback)
        root.bind('<Delete>', pyte_code.delete_key_callback)

        # add size grip
        #
        ttk.Sizegrip(self.win).grid(column=999, row=999, sticky=(tkinter.S, tkinter.E))

        # Set up a menu
        #
        self.menu = tkinter.Menu(self.win)
        file_menu = tkinter.Menu(self.menu, tearoff=0)
        file_menu.add_command(label='Load', command=pyte_code.menu_file_load)
        file_menu.add_command(label='Save', command=pyte_code.menu_file_save)
        file_menu.add_separator()
        file_menu.add_command(label='preview', command=pyte_code.menu_preview)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=self.win.quit)
        self.win.config(menu=self.menu)
        self.menu.add_cascade(label='File', menu=file_menu)

        # Set up Buttons at the top
        #
        # self.b_source = ttk.Button(self.win, text='Design',
        #                           command=self.design_click)
        # self.b_source.grid(row=0, column=0)
        # self.b_source = ttk.Button(self.win, text='Source',
        #                           command=self.source_click)
        # self.b_source.grid(row=0, column=1)

        # setup widget navigator
        self.navigator_frame = ttk.Frame(self.win)
        self.navigator_frame.grid(column=1, row=1, sticky='NWES')
        self.navigator_frame['padding'] = (5, 10)
        self.navigator_frame['relief'] = tkinter.GROOVE
        self.navigator_tree = ttk.Treeview(self.navigator_frame, takefocus=True, selectmode=tkinter.BROWSE)
        self.navigator_tree['columns'] = 'widget_type'
        self.navigator_tree.column('widget_type', width=100, anchor=tkinter.CENTER)
        self.navigator_tree.heading('widget_type', text='Widget Type')
        self.navigator_tree.tag_bind('project', '<ButtonRelease-1>',
                                     self.pyte_code.navigator_tree_clicked)
        self.navigator_tree.tag_bind('toplevel', '<ButtonRelease-1>',
                                     self.pyte_code.navigator_tree_clicked)
        self.navigator_tree.tag_bind('var', '<ButtonRelease-1>',
                                     self.pyte_code.navigator_tree_clicked)
        self.navigator_tree.tag_bind('widget', '<ButtonRelease-1>',
                                     self.pyte_code.navigator_tree_clicked)
        self.navigator_tree.grid(column=0, row=1, sticky=(tkinter.N + tkinter.S))
        self.scrollbar_navigator = ttk.Scrollbar(self.navigator_frame, orient=tkinter.VERTICAL,
                                                 command=self.navigator_tree.yview)
        self.scrollbar_navigator.grid(column=1, row=1, sticky='NS')
        self.navigator_tree['yscrollcommand'] = self.scrollbar_navigator.set

        # setup toolbox
        #
        self.toolbox_notebook = ttk.Notebook(self.win)
        self.toolbox_notebook.grid(column=5, row=0, columnspan=2, sticky=tkinter.E + tkinter.W + tkinter.N + tkinter.S)
        # set up background to user frame area
        #
        style = ttk.Style()
        style.configure("BW.TFrame", foreground="black", background="white")
        self.background_user_frame = ttk.Frame(self.win, borderwidth=1, style="BW.TFrame", relief=tkinter.SUNKEN)
        self.background_user_frame.config(padding=10)
        self.background_user_frame.grid(row=0, column=3, rowspan=2, sticky='NWES')
        self.background_user_frame.config()

        # set up User frame
        #
        self.user_frame = ttk.Frame(self.background_user_frame, borderwidth=2)
        self.user_frame.grid(row=0, column=0)

        # Set up Attributes and Events edit area
        #
        # self.win.bind("<Button-1>", self.wincallback)
        self.attribute_event_note2 = ttk.Notebook(self.win)
        self.attribute_event_note2.grid(column=5, row=1, columnspan=2, sticky='NWES')
        #
        # attributes tab (a frame)
        self.attribute_tab_frame = ttk.Frame(self.attribute_event_note2)
        self.attribute_event_note2.add(self.attribute_tab_frame, text='Attributes')
        # the canvas
        self.attr_canvas = tkinter.Canvas(self.attribute_tab_frame, bd=0, highlightthickness=0)
        self.attr_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        # self.attr_canvas.grid(row=0, column=0)
        self.scrollbar_attributes2 = ttk.Scrollbar(self.attribute_tab_frame, orient=tkinter.VERTICAL,
                                                   command=self.attr_canvas.yview)
        self.scrollbar_attributes2.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
        # self.scrollbar_attributes2.grid(row=0, column=1, sticky="NS")
        self.attr_canvas['yscrollcommand'] = self.scrollbar_attributes2.set
        self.attribute_frame2 = ttk.Frame(self.attr_canvas)
        self.attr_canvas.create_window((0, 0), window=self.attribute_frame2, anchor='nw')
        self.attribute_frame2.bind('<Configure>', self.frame_func)
        self.attribute_frame2.grid_columnconfigure(0, minsize=150)
        # self.attribute_frame2.grid(row=0, column=1, sticky='NSEW')
        # self.attribute_frame2['padding'] = (5, 10)
        # ttk.Label(self.attribute_frame2, text="Name").grid(row=0, column=0, sticky='W')
        ttk.Label(self.attribute_frame2, text="Value").grid(row=0, column=1, sticky='W')
        #
        # events tab (a frame)
        self.event_tab_frame = ttk.Frame(self.attribute_event_note2)
        self.attribute_event_note2.add(self.event_tab_frame, text='Events')
        # the canvas
        self.event_canvas = tkinter.Canvas(self.event_tab_frame, bd=0, highlightthickness=0)
        self.event_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        # self.attr_canvas.grid(row=0, column=0)
        self.event_scrollbar_attributes2 = ttk.Scrollbar(self.event_tab_frame, orient=tkinter.VERTICAL,
                                                         command=self.event_canvas.yview)
        self.event_scrollbar_attributes2.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
        # self.scrollbar_attributes2.grid(row=0, column=1, sticky="NS")
        self.event_canvas['yscrollcommand'] = self.event_scrollbar_attributes2.set
        self.event_frame2 = ttk.Frame(self.event_canvas)
        self.event_canvas.create_window((0, 0), window=self.event_frame2, anchor='nw')
        self.event_frame2.bind('<Configure>', self.frame_func)
        self.event_frame2.grid_columnconfigure(0, minsize=150)
        # self.attribute_frame2.grid(row=0, column=1, sticky='NSEW')
        # self.attribute_frame2['padding'] = (5, 10)
        # ttk.Label(self.attribute_frame2, text="Name").grid(row=0, column=0, sticky='W')
        ttk.Label(self.event_frame2, text="Value").grid(row=0, column=1, sticky='W')
        #
        # row/col tab (a frame)
        self.row_col_tab_frame = ttk.Frame(self.attribute_event_note2)
        self.attribute_event_note2.add(self.row_col_tab_frame, text='row/col')
        # the canvas
        self.row_col_canvas = tkinter.Canvas(self.row_col_tab_frame, bd=0, highlightthickness=0)
        self.row_col_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=tkinter.TRUE)
        # self.attr_canvas.grid(row=0, column=0)
        self.row_col_scrollbar_attributes2 = ttk.Scrollbar(self.row_col_tab_frame, orient=tkinter.VERTICAL,
                                                           command=self.row_col_canvas.yview)
        self.row_col_scrollbar_attributes2.pack(fill=tkinter.Y, side=tkinter.RIGHT, expand=tkinter.FALSE)
        # self.scrollbar_attributes2.grid(row=0, column=1, sticky="NS")
        self.row_col_canvas['yscrollcommand'] = self.row_col_scrollbar_attributes2.set
        self.row_col_frame2 = ttk.Frame(self.row_col_canvas)
        self.row_col_canvas.create_window((0, 0), window=self.row_col_frame2, anchor='nw')
        self.row_col_frame2.bind('<Configure>', self.frame_func)
        self.row_col_frame2.grid_columnconfigure(0, minsize=150)
        # self.attribute_frame2.grid(row=0, column=1, sticky='NSEW')
        # self.attribute_frame2['padding'] = (5, 10)
        # ttk.Label(self.attribute_frame2, text="Name").grid(row=0, column=0, sticky='W')
        ttk.Label(self.row_col_frame2, text="Value").grid(row=0, column=1, sticky='W')

        #
        # set resize behaviour
        self.win.columnconfigure(3, weight=1)
        self.win.rowconfigure(1, weight=1)
        self.attribute_frame2.columnconfigure(1, weight=1)
        self.attribute_frame2.rowconfigure(2, weight=1)
        self.event_frame2.columnconfigure(1, weight=1)
        self.event_frame2.rowconfigure(2, weight=1)
        self.navigator_frame.columnconfigure(1, weight=1)
        self.navigator_frame.rowconfigure(1, weight=1)
        self.win.grab_set()

    def frame_func(self, _event):
        self.attr_canvas.configure(scrollregion=self.attr_canvas.bbox('all'), width=self.attribute_frame2.winfo_width())
