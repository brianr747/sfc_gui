"""
License/Disclaimer
------------------

Copyright 2017 Brian Romanchuk

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
        self.EquationString = StringVar()
        self.DescriptionString = StringVar()
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

        self.Equation = tk.Entry(content, state=['readonly'], textvariable=self.EquationString)
        self.EntryDescription = tk.Entry(content, state=['readonly',], textvariable=self.DescriptionString)
        self.CanvasFigure = matplotlib.pyplot.figure(1)
        Fig = matplotlib.figure.Figure(figsize=(7.5, 5), dpi=90)
        subplot = Fig.add_subplot(111)
        x = []
        y = []
        self.Line, = subplot.plot(x, y, 'bo-')
        self.Canvas = FigureCanvasTkAgg(Fig, master=content)
        self.OnButtonClick()
        content.grid(column=0, row=0)
        frame.grid(column=0, row=0, columnspan=7, rowspan=3)
        self.BoxWidget.grid(row=0, column=0, columnspan=2)
        button.grid(column=5, row=0)
        button2.grid(column=6, row=0)
        self.EntryDescription.grid(row=0, column=2, columnspan=3, sticky=['w','e'])
        self.Equation.grid(row=1, column=0, columnspan=7, sticky=['w', 'e'])
        self.Canvas.get_tk_widget().grid(column=0, row=2, columnspan=7, sticky=['n', 's', 'e', 'w'])
        content.columnconfigure(2, weight=1)
        content.columnconfigure(3, weight=1)
        content.columnconfigure(4, weight=1)
        content.rowconfigure(2, weight=1)
        self.Canvas.show()
        self.resizable(width=True, height=True)
        self.update()

    def ComboChange(self, event):
        self.OnButtonClick()

    def OnButtonClick(self):
        x = self.Model.GetTimeSeries('k')
        series_name = self.BoxWidget.get()
        desc = ''
        eqn = ''
        try:
            eq = self.Model.FinalEquationBlock[series_name]
            eqn = eq.GetRightHandSide()
            desc = eq.Description
            eqn_str = '{0} = {1}'.format(series_name, eqn)
        except KeyError:
            # k is one variable that will not be in the FinalEquationBlock
            eqn_str = ''
        self.EquationString.set(eqn_str)
        self.DescriptionString.set(desc)
        try:
            y = self.Model.GetTimeSeries(series_name)
        except KeyError:
            return
        self.Line.set_data(x,y)
        # Based on stackoverflow "How do I Refresh a matplotlib plot in a Tkinter window?"
        # self.Canvas = FigureCanvasTkAgg(Fig, master=self)
        ax = self.Canvas.figure.gca()
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y)-1, max(y)+1)
        self.Canvas.draw()


# Yes, I should not be duplicating the code; I just want to mess around with various GUI options.
# This sucker will be rebuilt from scratch once I understand how tkinter works.
class ChartPlotterWindow2(tk.Tk):
    def __init__(self, parent, mod):
        """

        :param parent:
        :param mod: Model
        """
        tk.Tk.__init__(self, parent)
        self.Parent = parent
        self.Model = mod
        self.EquationString = StringVar()
        self.DescriptionString = StringVar()
        self.TimeSeriesList = sfc_gui.utils.sort_series(
            list(self.Model.EquationSolver.TimeSeries.keys()))
        self.SeriesBoxValue = StringVar()
        content = ttk.Frame(self)
        frame = ttk.Frame(content, borderwidth=5, relief='sunken')
        self.SeriesBoxValue = StringVar(value=self.TimeSeriesList)
        self.BoxWidget = tk.Listbox(content, listvariable=self.SeriesBoxValue, height=30)
        #self.BoxWidget.state(['readonly',])
        self.BoxWidget.bind('<<ComboboxSelected>>', self.ComboChange)
        #self.BoxWidget.current(0)
        button = tk.Button(content, text='Next',
                           command=self.OnButtonClick)
        button2 = tk.Button(content, text='Quit',
                           command=self.quit)

        self.Equation = tk.Entry(content, state=['readonly'], textvariable=self.EquationString)
        self.EntryDescription = tk.Entry(content, state=['readonly',], textvariable=self.DescriptionString)
        self.CanvasFigure = matplotlib.pyplot.figure(1)
        Fig = matplotlib.figure.Figure(figsize=(7.5, 5), dpi=90)
        subplot = Fig.add_subplot(111)
        x = []
        y = []
        self.Line, = subplot.plot(x, y, 'bo-')
        self.Canvas = FigureCanvasTkAgg(Fig, master=content)
        self.OnButtonClick()
        content.grid(column=0, row=0)
        frame.grid(column=0, row=0, columnspan=7, rowspan=3)
        self.BoxWidget.grid(row=0, column=0, columnspan=2, rowspan=3, sticky=['n','w','e'])
        button.grid(column=5, row=0)
        button2.grid(column=6, row=0)
        self.EntryDescription.grid(row=0, column=2, columnspan=3, sticky=['w','e'])
        self.Equation.grid(row=1, column=2, columnspan=5, sticky=['w', 'e'])
        self.Canvas.get_tk_widget().grid(column=3, row=2, columnspan=5, sticky=['n', 's', 'e', 'w'])
        content.columnconfigure(2, weight=1)
        content.columnconfigure(3, weight=1)
        content.columnconfigure(4, weight=1)
        content.rowconfigure(2, weight=1)
        self.Canvas.show()
        self.resizable(width=True, height=True)
        self.update()

    def ComboChange(self, event):
        self.OnButtonClick()

    def OnButtonClick(self):
        x = self.Model.GetTimeSeries('k')
        idx = self.BoxWidget.curselection()
        if len(idx) == 0:
            idx = 0
        else:
            idx = idx[0]
        series_name = self.TimeSeriesList[idx]
        desc = ''
        eqn = ''
        try:
            eq = self.Model.FinalEquationBlock[series_name]
            eqn = eq.GetRightHandSide()
            desc = eq.Description
            eqn_str = '{0} = {1}'.format(series_name, eqn)
        except KeyError:
            # k is one variable that will not be in the FinalEquationBlock
            eqn_str = ''
        self.EquationString.set(eqn_str)
        self.DescriptionString.set(desc)
        try:
            y = self.Model.GetTimeSeries(series_name)
        except KeyError:
            return
        self.Line.set_data(x,y)
        # Based on stackoverflow "How do I Refresh a matplotlib plot in a Tkinter window?"
        # self.Canvas = FigureCanvasTkAgg(Fig, master=self)
        ax = self.Canvas.figure.gca()
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y)-1, max(y)+1)
        self.Canvas.draw()


