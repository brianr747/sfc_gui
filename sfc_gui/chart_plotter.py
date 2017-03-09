import sys

import matplotlib
matplotlib.use('TKagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot
from sfc_models.models import Model
import sfc_gui.utils

if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
    from Tkinter import ttk
else:
    import tkinter as tk
    from tkinter import *
    from tkinter import ttk

class ChartPlotterWindow(tk.Tk):
    def __init__(self, parent, mod):
        """

        :param parent:
        :param mod: Model
        """
        tk.Tk.__init__(self, parent)
        self.Parent = parent
        self.CanvasFigure = None
        self.Line = None
        self.Canvas = None
        self.Model = mod
        self.TimeSeriesList = []
        self.Pos = 0
        self.SetUp()

    def SetUp(self):
        self.TimeSeriesList = sfc_gui.utils.sort_series(
            list(self.Model.EquationSolver.TimeSeries.keys()))
        self.SeriesBoxValue = StringVar()
        content = ttk.Frame(self)
        frame = ttk.Frame(content, borderwidth=5, relief='sunken')
        self.BoxWidget = ttk.Combobox(content, textvariable=self.SeriesBoxValue)
        self.BoxWidget.state(['readonly',])
        self.BoxWidget['values'] = self.TimeSeriesList
        # self.SeriesBoxValue.trace('w', self.ComboChange())
        self.BoxWidget.bind('<<ComboboxSelected>>', self.ComboChange)
        self.BoxWidget.current(0)
        button = tk.Button(content, text='Next',
                           command=self.OnButtonClick)
        button2 = tk.Button(content, text='Quit',
                           command=self.quit)
        self.CanvasFigure = matplotlib.pyplot.figure(1)
        Fig = matplotlib.figure.Figure(figsize=(4.5, 3), dpi=90)
        subplot = Fig.add_subplot(111)
        x = []
        y = []
        self.Line, = subplot.plot(x, y, 'bo-')
        self.Canvas = FigureCanvasTkAgg(Fig, master=content)
        self.OnButtonClick()
        content.grid(column=0, row=0)
        frame.grid(column=0, row=0, columnspan=4, rowspan=2)
        self.BoxWidget.grid(row=0, column=0, columnspan=2)
        button.grid(column=2, row=0)
        button2.grid(column=3, row=0)
        self.Canvas.get_tk_widget().grid(column=0, row=1, columnspan=4)
        self.Canvas.show()
        self.resizable(width=True, height=True)
        self.update()

    def ComboChange(self, event):
        print('Bink')
        self.OnButtonClick()

    def OnButtonClick(self):
        x = self.Model.GetTimeSeries('k')
        try:
            y = self.Model.GetTimeSeries(self.BoxWidget.get())
        except KeyError:
            return
        self.Line.set_data(x,y)
        # Based on stackoverflow "How do I Refresh a matplotlib plot in a Tkinter window?"
        # self.Canvas = FigureCanvasTkAgg(Fig, master=self)
        ax = self.Canvas.figure.gca()
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y)-1, max(y)+1)
        self.Canvas.draw()




