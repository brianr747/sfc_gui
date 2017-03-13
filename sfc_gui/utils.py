# coding=utf-8
"""

License/Disclaimer
------------------

Copyright 2016 Brian Romanchuk

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

import copy
import sys
import matplotlib
matplotlib.use('TKagg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot

if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
    from Tkinter import ttk
else:
    import tkinter as tk
    from tkinter import *
    from tkinter import ttk

class WidgetHolder(object):
    def __init__(self):
        self.Widgets = {}
        self.Data = {}
        self.ListBoxType = {}
        self.MatplotlibInfo = {}

    def AddEntry(self, parent, name, readonly=False):
        self.Data[name] = StringVar()
        if readonly:
            self.Widgets[name] = Entry(parent, state=['readonly',], textvariable=self.Data[name])
        else:
            self.Widgets[name] = Entry(parent, textvariable=self.Data[name])

    def AddButton(self, parent, name, text, command, state='!disabled'):
        self.Widgets[name] = ttk.Button(parent, text=text, command=command, state=state)

    def AddTree(self, parent, name, columns):
        self.Widgets[name] = ttk.Treeview(parent, columns=columns)

    def AddListBox(self, parent, name, height=10, single_select=True, callback=None):
        if single_select:
            select_mode = 'browse'
        else:
            select_mode='extended'
        self.ListBoxType[name] = select_mode
        self.Data[name] = StringVar()
        self.Widgets[name] = Listbox(parent, listvariable=self.Data[name], height=height,
                                     selectmode=select_mode)
        if callback is not None:
            self.Widgets[name].bind('<<ListboxSelect>>', callback)

    def GetListBox(self, name):
        """
        If single_select: returns string or None (no selection).

        If multi-select, always returns a list of strings (possibly empty).

        :param name:
        :return:
        """
        indices = self.Widgets[name].curselection()
        mlist =  self.Data[name].get()
        mlist = eval(mlist)
        if self.ListBoxType[name] == 'browse':
            if len(indices) == 0:
                return None
            else:
                return mlist[indices[0]]
        else:
            return [mlist[x[0]] for x in indices]




    def AddMatplotLib(self, parent, name):
        Fig = matplotlib.figure.Figure(figsize=(7.5, 5), dpi=90)
        subplot = Fig.add_subplot(111)
        x = []
        y = []
        self.MatplotlibInfo[name+"line"], = subplot.plot(x, y, 'bo-')
        self.MatplotlibInfo[name+'canvas'] = FigureCanvasTkAgg(Fig, master=parent)

    def AddRadioButtons(self, parent, name, options):
        self.Data[name] = StringVar()
        widgies = []
        for opt in options:
            widgies.append(ttk.Radiobutton(parent, text=opt, variable=self.Data[name], value=opt))
        self.Widgets[name] = widgies

    def AddVariableLabel(self, parent, name):
        self.Data[name] = StringVar()
        self.Widgets[name] = tk.Label(parent, textvariable=self.Data[name])

    def GetMatplotlibInfo(self, name, objectname):
        if not objectname in ('line', 'canvas'):
            raise ValueError('Unknown type of object')
        return self.MatplotlibInfo[name+objectname]


def sort_series(serlist):
    """
    Sort a list of series names alphabetically, except for 'k' and 't' (at the front).

    Works on a copy, and returns it. (Not an in-place sort.)

    This should be moved to sfc_models, since the same code appears there.

    :param serlist: list
    :return:
    """
    new_serlist = copy.copy(serlist)
    new_serlist.sort()
    if 't' in new_serlist:
        new_serlist.remove('t')
        new_serlist.insert(0, 't')
    if 'k' in new_serlist:
        new_serlist.remove('k')
        new_serlist.insert(0,'k')
    return new_serlist


def get_int(val, accept_None=True):
    try:
        val_n = int(val)
    except:
        if accept_None and val.lower() in ('none', 'na', ''):
            val_n = None
        else:
            raise
    return val_n


def get_series_info(series_name, mod):
    desc = ''
    eqn = ''
    try:
        eq = mod.FinalEquationBlock[series_name]
        eqn = eq.GetRightHandSide()
        desc = eq.Description
        eqn_str = '{0} = {1}'.format(series_name, eqn)
    except KeyError:
        # k is one variable that will not be in the FinalEquationBlock
        eqn_str = ''
    if series_name == 'k':
        desc = '[k] Time Axis'
        eqn_str = 'k = k (!)'
    if eqn_str == '' and series_name == 't':
        eqn_str = 't = k'
        desc = '[t] Automatically generated time axis; user may override as a global equation.'
    if eqn_str == '' and series_name == 'iteration':
        desc = 'The iteration step within the solver algorithm'
    if eqn_str == '' and series_name == 'iteration_error':
        desc = 'Fitting error for equations at each iteration of the solver.'
    return eqn_str, desc

