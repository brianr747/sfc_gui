# coding=utf-8
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
import sfc_gui.utils as utils
from sfc_gui.utils import WidgetHolder

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
        self.TimeSeriesList = utils.sort_series(
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
    def __init__(self, parent, mod, time_cut_off=None):
        """

        :param parent:
        :param mod: Model
        """
        tk.Tk.__init__(self, parent)
        self.wm_title('sfc_models Chart Plotter')
        self.SourceOptions = ('Time Series', 'Initial Steady State', 'Convergence Trace')
        self.Parent = parent
        self.Model = mod
        self.TimeAxisVariable = None
        self.TimeAxisMinimum = None
        self.TimeRange = None
        self.TimeStart = None
        self.TimeSeriesList = None
        # WidgetSettings frame window
        self.WidgetSettings = WidgetHolder()
        self.FrameSettings = self.CreateSettingsFrame(self.WidgetSettings)
        self.SetSettings()
        # Graph Frame
        self.WidgetGraph = WidgetHolder()
        self.FrameGraph = self.CreateGraphFrame(self.WidgetGraph)
        self.LastSource = None
        self.TimeSeriesHolder = self.SetTimeSeriesHolder()
        self.UpdateContentFrame()
        self.FrameGraph.tkraise()
        self.resizable(width=True, height=True)
        self.update()

    def SetTimeSeriesHolder(self):
        opt = self.WidgetSettings.Data['source'].get()
        if opt == self.LastSource:
            return
        if opt == self.SourceOptions[0]:
            holder = self.Model.EquationSolver.TimeSeries
        if opt == self.SourceOptions[1]:
            holder = self.Model.EquationSolver.TimeSeriesInitialSteadyState
        if opt == self.SourceOptions[2]:
            holder = self.Model.EquationSolver.TimeSeriesStepTrace
        self.TimeSeriesHolder = holder
        self.TimeAxisVariable = self.TimeSeriesHolder.TimeSeriesName
        if self.TimeAxisVariable not in holder:
            holder[self.TimeAxisVariable] = [0.0, 1.0]
        self.TimeAxisMinimum = int(self.GetTimeSeries(self.TimeAxisVariable)[0])
        self.TimeRange = None
        self.TimeStart = self.TimeAxisMinimum
        self.TimeSeriesList = holder.GetSeriesList()
        # self.SeriesBoxValue.set(value=self.TimeSeriesList)
        self.WidgetGraph.Data['equationlist'].set(value=self.TimeSeriesList)
        self.LastSource = opt
        return holder

    def GetTimeSeries(self, series_name):
        ser = self.TimeSeriesHolder[series_name]
        return ser

    def CreateSettingsFrame(self, widgetholder):
        frame = ttk.Frame(self, borderwidth=5, relief='sunken')

        button = tk.Button(frame, text='Apply', command=self.OnSettingsApply)
        button2 = tk.Button(frame, text='Cancel',
                            command=self.OnSettingsBack)
        label = tk.Label(frame, text='Time Series Range Limit [{0}]'.format(self.TimeAxisVariable))
        widgetholder.AddEntry(frame, 'cutoff')
        label_start = tk.Label(frame, text='Time Series Start [{0}]'.format(self.TimeAxisVariable))
        widgetholder.AddEntry(frame, 'start')
        widgetholder.AddRadioButtons(frame, 'source', self.SourceOptions)
        widgetholder.Data['source'].set(self.SourceOptions[0])
        buttonrow = 5
        frame.grid(row=0, column=0)
        button.grid(row=buttonrow, column=0)
        button2.grid(row=buttonrow, column=1)
        label.grid(row=0, column=0, columnspan=2)
        widgetholder.Widgets['cutoff'].grid(row=1, column=0, columnspan=2)
        label_start.grid(row=2, column=0, columnspan=2)
        widgetholder.Widgets['start'].grid(row=3, column=0, columnspan=2)
        widgies = widgetholder.Widgets['source']
        for i in range(0, len(widgies)):
            widgies[i].grid(row=3, column=i)
        return frame

    def CreateGraphFrame(self, widgetholder):
        content = ttk.Frame(self, borderwidth=5, relief='sunken')
        widgetholder.AddListBox(content, 'equationlist', height=30)
        button = tk.Button(content, text='Settings', command=self.OnButtonClick)
        button2 = tk.Button(content, text='Quit', command=self.quit)
        widgetholder.AddEntry(content, 'equation', readonly=True)
        widgetholder.AddEntry(content, 'description', readonly=True)
        widgetholder.AddMatplotLib(content, 'graph')
        widgetholder.Widgets['equationlist'].bind('<<ListboxSelect>>', self.OnListEvent)
        # Gridding
        content.grid(column=0, row=0)
        widgetholder.Widgets['equationlist'].grid(row=0, column=0, columnspan=1, rowspan=3, sticky=['n', 'w', 'e'])
        button.grid(column=5, row=0)
        button2.grid(column=6, row=0)
        widgetholder.Widgets['description'].grid(row=0, column=1, columnspan=4, sticky=['w','e'])
        widgetholder.Widgets['equation'].grid(row=1, column=1, columnspan=6, sticky=['w', 'e'])
        widgetholder.GetMatplotlibInfo('graph', 'canvas').get_tk_widget().grid(column=2, row=2,
                                        columnspan=5, sticky=['n', 's', 'e', 'w'])
        content.columnconfigure(2, weight=1)
        content.columnconfigure(3, weight=1)
        content.columnconfigure(4, weight=1)
        content.rowconfigure(2, weight=1)
        return content


    def SetSettings(self):
        self.WidgetSettings.Data['cutoff'].set(str(self.TimeRange))
        self.WidgetSettings.Data['start'].set(str(self.TimeStart))

    def OnButtonClick(self):
        self.SetSettings()
        self.FrameSettings.tkraise()

    def OnSettingsBack(self):
        self.FrameGraph.tkraise()

    def OnSettingsApply(self):
        start = self.WidgetSettings.Data['start'].get()
        try:
            start_n = utils.get_int(start, accept_None=True)
        except:
            return
        if start_n is None:
            self.TimeStart = self.TimeAxisMinimum
        else:
            self.TimeStart = max(start_n, self.TimeAxisMinimum)
        val = self.WidgetSettings.Data['cutoff'].get()
        try:
            val_n = utils.get_int(val)
        except:
            return
        if val_n is None:
            self.TimeRange = None
        elif val_n < 1:
            return
        else:
            self.TimeRange = val_n
        self.SetTimeSeriesHolder()
        self.UpdateContentFrame()
        self.FrameGraph.tkraise()

    def OnListEvent(self, event):
        self.UpdateContentFrame()

    def UpdateContentFrame(self):
        # Do the cutoff inside the GUI, as we may switch to alternative
        # time series sources.
        x = self.GetTimeSeries(self.TimeAxisVariable)
        # idx = self.WidgetListVariableNames.curselection()
        idx = self.WidgetGraph.Widgets['equationlist'].curselection()
        if len(idx) == 0:
            idx = 0
        else:
            idx = idx[0]
        series_name = self.TimeSeriesList[idx]
        try:
            y = self.GetTimeSeries(series_name)
        except KeyError:
            return
        desc = ''
        eqn = ''
        eqn_str, desc = utils.get_series_info(series_name, self.Model)
        self.WidgetGraph.Data['equation'].set(eqn_str)
        self.WidgetGraph.Data['description'].set(desc)
        if self.TimeStart > self.TimeAxisMinimum:
            if self.TimeStart <  self.TimeAxisMinimum + len(x):
                x = x[self.TimeStart - self.TimeAxisMinimum:]
                y = y[self.TimeStart - self.TimeAxisMinimum:]
        if self.TimeRange is not None and len(x) > self.TimeRange:
            x = x[0:self.TimeRange]
            y = y[0:self.TimeRange]
        self.WidgetGraph.GetMatplotlibInfo('graph', 'line').set_data(x,y)
        # self.Line.set_data(x,y)
        # Based on stackoverflow "How do I Refresh a matplotlib plot in a Tkinter window?"
        # self.Canvas = FigureCanvasTkAgg(Fig, master=self)
        # ax = self.Canvas.figure.gca()
        # ax.set_xlim(min(x), max(x))
        # ax.set_ylim(min(y)-1, max(y)+1)
        # ax.set_xlabel(self.TimeAxisVariable)
        # self.Canvas.draw()

        canvas = self.WidgetGraph.GetMatplotlibInfo('graph', 'canvas')
        ax = canvas.figure.gca()
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y)-1, max(y)+1)
        ax.set_xlabel(self.TimeAxisVariable)
        canvas.draw()



