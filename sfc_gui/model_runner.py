# coding=utf-8
"""
model_runner.py

Creates a GUI that runs SFC models. Allows quick and easy examination of equation creation.
"""

import os
import sys

from sfc_models.models import Model
import sfc_gui.utils
import sfc_gui.module_loader
from sfc_gui.utils import WidgetHolder

if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
    from Tkinter import ttk
    import Tkinter.filedialog as fdog
else:
    import tkinter as tk
    from tkinter import *
    from tkinter import ttk
    import tkinter.filedialog as fdog


if sys.version_info[0] >=  3 and sys.version_info[1] >= 4:
    from importlib import reload as reloader
    from importlib import import_module as loader
else:
    from imp import reload as reloader
    from imp import import_module as loader

class ModelRunner(tk.Tk):
    def __init__(self, parent):
        """

        :param parent:
        """
        tk.Tk.__init__(self, parent)
        self.MinWidth = 500
        self.MinHeight = 600
        self.wm_title('sfc_models Model Runner')
        self.WidgetsChooser = WidgetHolder()
        self.FrameChooser = self.CreateChooser(self.WidgetsChooser)
        self.WidgetsModelViewer = WidgetHolder()
        self.FrameModelViewer = self.CreateModelViewer(self.WidgetsModelViewer)

        self.FrameChooser.tkraise()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.resizable(width=True, height=True)
        self.Model = None

    def CreateChooser(self, widgetholder):
        frame = ttk.Frame(self)
        inner_frame = ttk.Frame(frame, borderwidth=5, relief='sunken', width=self.MinWidth,
                          height=self.MinHeight)
        widgetholder.AddEntry(frame, 'directory')
        widgetholder.Data['directory'].set(os.getcwd())
        label_dir = Label(frame, text='Working Directory')
        button_choose = ttk.Button(frame, text='Choose', command=self.OnChooseDir)
        widgetholder.AddEntry(frame, 'logdir')
        default = os.path.join(widgetholder.Data['directory'].get(), 'output')
        if os.path.isdir(default):
            logdir = default
        else:
            logdir = ''
        widgetholder.Data['logdir'].set(logdir)
        # Log directory
        label_log = Label(frame, text='Log Directory')
        button_choose_log = ttk.Button(frame, text='Choose', command=self.OnChooseDir)
        # Model row
        label_model = Label(frame, text='Model File')
        widgetholder.AddListBox(frame, 'models', height=12)
        widgetholder.Widgets['models'].bind('<<ListboxSelect>>', self.OnChangeModel)
        widgetholder.AddEntry(frame, 'model_desc', readonly=True)
        widgetholder.AddVariableLabel(frame, 'is_valid')
        widgetholder.AddButton(frame, 'run_button', command=self.OnRunModel,
                               text='Load', state='disabled')
        # Grid'em, Danno!
        frame.grid(row=0, column=0, rowspan=4, columnspan=3, sticky=['n', 's', 'w', 'e'])
        # Working directory
        label_dir.grid(row=0, column=0)
        widgetholder.Widgets['directory'].grid(row=0, column=1, sticky=['w', 'e'])
        button_choose.grid(row=0, column=2, sticky='w', padx=5)
        # Log dir
        label_log.grid(row=1, column=0)
        widgetholder.Widgets['logdir'].grid(row=1, column=1, sticky=['w', 'e'])
        button_choose_log.grid(row=1, column=2, sticky='w', padx=5)
        # Model rows
        label_model.grid(row=2, column=0)
        widgetholder.Widgets['models'].grid(row=2, column=1, sticky=['w', 'e','n', 's'], rowspan=3, pady=5)
        widgetholder.Widgets['model_desc'].grid(row=2, column=2, sticky=['w', 'e'], padx=5)
        widgetholder.Widgets['is_valid'].grid(row=3, column=2, sticky=['w', 'e'])
        widgetholder.Widgets['run_button'].grid(row=4, column=2, pady=5)
        # Column config [Not working?]
        inner_frame.grid(row=0, column=0, rowspan=5, columnspan=3, sticky=('N', 'S', 'E', 'W'))
        frame.columnconfigure(1, weight=4)
        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)
        frame.rowconfigure(3, weight=1)
        # Populate list
        self.DirectoryChanged()
        return frame

    def CreateModelViewer(self, widgetholder):
        frame = ttk.Frame(self)
        inner_frame = ttk.Frame(frame, borderwidth=5, relief='sunken', width=self.MinWidth,
                          height=self.MinHeight)
        widgetholder.AddVariableLabel(frame, 'model_name')
        widgetholder.AddVariableLabel(frame, 'model_state')
        widgetholder.AddButton(frame, 'back', text='Back', command=self.OnModelViewerBack)
        # widgetholder.AddListBox(frame, 'country', height=5, callback=self.OnChangeCountry)
        widgetholder.AddTree(frame, 'equations', columns=('Equation', 'Comment'))
        # Push a configuration variable into the WidgetHolder
        widgetholder.Data['parameter_final_equation'] = 'Final Equations (All)'
        scrolly = ttk.Scrollbar(frame, orient=VERTICAL,
                                command=self.WidgetsModelViewer.Widgets['equations'].yview)
        self.WidgetsModelViewer.Widgets['equations']['yscrollcommand'] = scrolly.set
        # Gridding
        frame.grid(row=0, column=0,  sticky=('N', 'S', 'E', 'W'))
        self.WidgetsModelViewer.Widgets['model_name'].grid(row=0, column=0)
        self.WidgetsModelViewer.Widgets['model_state'].grid(row=0, column=1)
        self.WidgetsModelViewer.Widgets['back'].grid(row=0, column=2)
        self.WidgetsModelViewer.Widgets['equations'].grid(row=1, column=0, columnspan=3,
                                                          sticky=('N', 'S', 'W', 'E'))
        scrolly.grid(row=1, column=3, sticky=('N', 'S'))
        inner_frame.grid(row=0, column=0, rowspan=5, columnspan=3, sticky=('N', 'S', 'E', 'W'))
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)
        return frame

    def OnModelViewerBack(self):
        self.FrameChooser.tkraise()

    def GetModelName(self):
        return self.WidgetsChooser.GetListBox('models')

    def OnChangeCountry(self, event):
        print('Bink!')

    def OnRunModel(self):
        name = self.GetModelName()
        if name is None:
            # Shouldn't reach here; GUI logic error
            raise ValueError('No model selected? GUI logic error.')
        python_mod = self.Importer(name)
        self.Model = python_mod.build_model()
        if type(self.Model) is not Model:
            raise ValueError('Expected a Model, got {0} instead'.format(type(Model)))
        self.UpdateModelViewer()
        self.FrameModelViewer.tkraise()

    def UpdateModelViewer(self):
        name = self.GetModelName()
        self.WidgetsModelViewer.Data['model_name'].set(name)
        self.WidgetsModelViewer.Data['model_state'].set(self.Model.State)

        treewidget = self.WidgetsModelViewer.Widgets['equations']
        country_list =   [x.Code for x in self.Model.CountryList]
        final_name = 'FINAL*EQUATIONS'
        root_list = [final_name,] + country_list
        # First: Eliminate countries (and children) that do not exist.
        on_tree = treewidget.get_children()
        # Cannot iterate on get_children(), as we modify the output with every delete!
        for name in on_tree:
            if name not in root_list:
                treewidget.delete(name)
        # FINAL_EQUATIONS
        if final_name not in on_tree:
            treewidget.insert('', 'end',final_name,
                              text=self.WidgetsModelViewer.Data['parameter_final_equation'],
                              open=False)
            # Insert final equations here...
        for country_obj in self.Model.CountryList:
            country_code = country_obj.Code
            if country_obj.Code not in on_tree:
                treewidget.insert('', 'end', country_obj.Code, text=country_obj.Code, open=False)
            country_children = treewidget.get_children(country_obj.Code)
            sectors = {}
            for sector in country_obj.SectorList:
                sectors[country_code + '*' + sector.Code] = sector
            codes = list(sectors.keys())
            codes.sort()
            for sector_code in country_children:
                if sector_code not in codes:
                    treewidget.delete(sector_code)
            for sector_code in codes:
                sector_obj = sectors[sector_code]
                if sector_code not in country_children:
                    treewidget.insert(country_code, 'end',
                                      sector_code, text=sector_obj.Code,
                                      open=False)
                    variables_on_tree = treewidget.get_children(sector_code)
                    variables = sector_obj.EquationBlock.GetEquationList()
                    variable_lookup = {}
                    for var in variables:
                        variable_lookup[sector_code+'*'+var] = sector_obj.EquationBlock[var]
                    for var_code in variables_on_tree:
                        if var_code not in variable_lookup:
                            treewidget.delete(var_code)
                    for var_code in variable_lookup.keys():
                        eqn = variable_lookup[var_code]
                        eqn_str = "{0} = {1}".format(eqn.LeftHandSide, eqn.GetRightHandSide())
                        if var_code not in variables_on_tree:
                            treewidget.insert(sector_code, 'end', var_code,
                                              text=eqn.LeftHandSide,
                                              values=(eqn_str, eqn.Description))
                        else:
                            treewidget.set(var_code, values=(eqn_str, eqn.Description))
        print(treewidget.get_children())
        # country_list = [self.WidgetsModelViewer.Data['parameter_final_equation'],]
        # for c in self.Model.CountryList:
        #     country_list.append(c.Code)
        # self.WidgetsModelViewer.Data['country'].set(country_list)

    def OnChooseDir(self):
        target = fdog.askdirectory(title='Set Working Directory')
        if target == () or target == '':
            return
        self.WidgetsChooser.Data['directory'].set(target)
        logdir = os.path.join(target, 'output')
        if os.path.isdir(logdir):
            self.WidgetsChooser.Data['logdir'].set(logdir)
        self.DirectoryChanged()

    def OnChooseLogDir(self):
        target = fdog.askdirectory(title='Set Working Directory')
        if target == () or target == '':
            return
        self.WidgetsChooser.Data['logdir'].set(target)

    def OnChangeModel(self, event):
        idx = self.WidgetsChooser.Widgets['models'].curselection()
        if len(idx) == 0:
            self.WidgetsChooser.Data['model_desc'].set('')
            return
        else:
            idx = idx[0]
        mlist =  self.WidgetsChooser.Data['models'].get()
        mlist = eval(mlist)
        name = mlist[idx]
        info = self.ValidateFile(name)
        self.WidgetsChooser.Data['model_desc'].set(info['description'])
        if info['is_valid']:
            self.WidgetsChooser.Data['is_valid'].set('')
            self.WidgetsChooser.Widgets['run_button'].state(['!disabled'])
        else:
            self.WidgetsChooser.Data['is_valid'].set('Invalid File')
            self.WidgetsChooser.Widgets['run_button'].state(['disabled'])

    def DirectoryChanged(self):
        os.chdir(self.WidgetsChooser.Data['directory'].get())
        flist = os.listdir('.')
        acceptable = []
        for f in flist:
            if not f.endswith('.py'):
                continue
            header = 'sfcmod_'
            if not f.startswith(header):
                continue
            f = f[:-3]
            acceptable.append(f)
        self.WidgetsChooser.Data['models'].set(acceptable)

    def Importer(self, name):
        if type(name) is not str:
            name = name[0]
        fpath = os.path.join('.', name + '.py')
        return sfc_gui.module_loader.loader(name, fpath)

    def ValidateFile(self, name):
        mod = self.Importer(name)
        out = {}
        is_valid = True
        if 'get_description' not in dir(mod):
            out['description'] = 'Missing get_description()'
        else:
            out['description'] = mod.get_description()
        if 'build_model' not in dir(mod):
            is_valid = False
        out['is_valid'] = is_valid
        return out









if __name__ == '__main__':
    window = ModelRunner(None)
    window.mainloop()
