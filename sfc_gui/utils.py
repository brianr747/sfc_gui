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

    def AddEntry(self, parent, name):
        self.Data[name] = StringVar()
        self.Widgets[name] = Entry(parent, textvariable=self.Data[name])

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
    return eqn_str, desc

