# coding=utf-8
"""
model_runner.py

Creates a GUI that runs SFC models. Allows quick and easy examination of equation creation.
"""

import os
import sys

from sfc_models.models import Model
from sfc_models.utils import Logger
import sfc_gui.utils
import sfc_gui.module_loader
import sfc_gui.chart_plotter
from sfc_gui.utils import WidgetHolder, Parameters

if sys.version_info[0] < 3:
    import Tkinter as tk
    from Tkinter import *
    from Tkinter import messagebox
    from Tkinter import ttk
    import Tkinter.filedialog as fdog
else:
    import tkinter as tk
    from tkinter import *
    from tkinter import messagebox
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
        self.Parent = parent
        self.Parameters = Parameters()
        self.MinWidth = 500
        self.MinHeight = 600
        try:
            new_dir = os.getenv('SFCMODELSGUIDIR')
            if new_dir is not None:
                os.chdir(new_dir)
        except:
            pass
        self.wm_title('sfc_models Model Runner')
        self.WidgetsChooser = WidgetHolder()
        self.FrameChooser = self.CreateChooser(self.WidgetsChooser)
        self.WidgetsModelViewer = WidgetHolder()
        self.FrameModelViewer = self.CreateModelViewer(self.WidgetsModelViewer)
        self.PreviousEquations = []
        self.CurrentEquations = []
        self.Sectors = []
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
        self.Parameters.LogDir = logdir
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

        top_frame = ttk.Frame(frame, borderwidth=5, relief='sunken' )
        widgetholder.AddVariableLabel(top_frame, 'model_name')
        widgetholder.AddVariableLabel(top_frame, 'model_state')
        widgetholder.AddVariableLabel(top_frame, 'num_sector_eqn')
        widgetholder.AddVariableLabel(top_frame, 'num_final_eqn')
        widgetholder.AddButton(frame, 'back', text='Back', command=self.OnModelViewerBack)
        # widgetholder.AddListBox(frame, 'country', height=5, callback=self.OnChangeCountry)
        widgetholder.AddButton(frame, 'fullcodes', 'Generate\nFullCodes',
                               command=self.OnGenerateFullCodes)
        widgetholder.AddButton(frame, 'fixaliases', 'Fix Aliases',
                               command=self.OnFixAliases)
        widgetholder.AddButton(frame, 'generate_eqn', 'Generate\nEquations',
                               command=self.OnGenerateEquations)
        widgetholder.AddTree(frame, 'equations', columns=('Equation', 'Comment'))
        # Push a configuration variable into the WidgetHolder
        widgetholder.Data['parameter_final_equation'] = 'Final Equations (All)'
        scrolly = ttk.Scrollbar(frame, orient=VERTICAL,
                                command=self.WidgetsModelViewer.Widgets['equations'].yview)
        self.WidgetsModelViewer.Widgets['equations']['yscrollcommand'] = scrolly.set
        label_name = ttk.Label(top_frame, text='Model Name: ')
        label_state = ttk.Label(top_frame, text="State: ")
        label_num_sector = ttk.Label(top_frame, text='# of Sector Equations')
        label_num_final = ttk.Label(top_frame, text='# of Final Equations')
        # Gridding
        frame.grid(row=0, column=0,  sticky=('N', 'S', 'E', 'W'))
        # Top Grid
        top_frame.grid(row=0, column = 0, columnspan=5, sticky=('W',))
        label_name.grid(row=0, column=0)
        self.WidgetsModelViewer.Widgets['model_name'].grid(row=0, column=1, padx=5)
        label_state.grid(row=0, column=2, sticky=('E'))
        self.WidgetsModelViewer.Widgets['model_state'].grid(row=0, column=3, padx=5)
        label_num_sector.grid(row=1, column=0)
        self.WidgetsModelViewer.Widgets['num_sector_eqn'].grid(row=1, column=1, padx=5, sticky=('W',))
        label_num_final.grid(row=1, column=2)
        self.WidgetsModelViewer.Widgets['num_final_eqn'].grid(row=1, column=3, padx=5, sticky=('W',))
        self.WidgetsModelViewer.Widgets['back'].grid(row=0, column=4, sticky=('E'))
        self.WidgetsModelViewer.Widgets['equations'].grid(row=1, column=0, columnspan=5,
                                                          rowspan=5, sticky=('N', 'S', 'W', 'E'))
        scrolly.grid(row=1, column=6, rowspan=3, sticky=('N', 'S'))
        # self.WidgetsModelViewer.Widgets['fullcodes'].grid(row=1, column=4, sticky=('N', 'E'))
        # self.WidgetsModelViewer.Widgets['fixaliases'].grid(row=2, column=4, sticky=('N', 'E'))
        # self.WidgetsModelViewer.Widgets['generate_eqn'].grid(row=3, column=4, sticky=('N', 'E'))
        inner_frame.grid(row=0, column=0, rowspan=5, columnspan=6, sticky=('N', 'S', 'E', 'W'))
        #frame.columnconfigure(0, weight=1)
        #frame.columnconfigure(1, weight=1)
        #frame.columnconfigure(2, weight=1)
        #frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=2)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)
        run_frame = ttk.LabelFrame(frame, text='Run')
        run_frame.grid(row=0, column=7, rowspan=5, sticky=('N', 'S', 'E', 'W'))
        widgetholder.AddButton(run_frame, 'reload', 'Reload',
                               command=self.OnRunModel)
        label_next_step = ttk.Label(run_frame, text='Next Step:', width=25)
        widgetholder.AddButton(run_frame, 'run_next', 'Run Next Step', command=self.OnRunNext)
        widgetholder.AddButton(run_frame, 'run_all', 'Run All Steps', command=self.OnRunAll)
        widgetholder.AddVariableLabel(run_frame, 'next_step')
        label_choose_next = ttk.Label(run_frame, text='Possible Choices')
        widgetholder.AddListBox(run_frame, 'possible_steps', height=7, single_select=True,
                                callback=self.UpdateModelViewer)
        widgetholder.AddButton(run_frame, 'show_graph', 'Show Graph', command=self.OnShowGraph)
        widgetholder.Widgets['reload'].grid(row=0, column=0)
        label_next_step.grid(row=1, column=0, pady=(10,0))
        widgetholder.Widgets['next_step'].grid(row=2, column=0)
        widgetholder.Widgets['run_next'].grid(row=3, column=0)
        label_choose_next.grid(row=4, column=0)
        widgetholder.Widgets['possible_steps'].grid(row=5, column=0)
        widgetholder.Widgets['run_all'].grid(row=6, column=0, pady=20)

        widgetholder.Widgets['show_graph'].grid(row=7, column=0, pady=20)
        return frame

    def OnRunNext(self):
        steps = self.Model._GetSteps()
        if len(steps) == 0:
            return
        else:
            next_step = self.WidgetsModelViewer.GetListBox('possible_steps')
            if next_step is None:
                next_step = steps[0][0]
        try:
            self.Model._RunStep(next_step)
        except Exception as e:
            self.Model.LogInfo(ex=e)
            sfc_gui.utils.ErrorDialog(e)
            self.UpdateModelViewer()
            # messagebox.showinfo(message=str(e), icon='error', title='Error')
            raise e
        self.UpdateModelViewer()

    def OnRunAll(self):
        try:
            self.Model._RunAllSteps()
        except Exception as e:
            sfc_gui.utils.ErrorDialog(e) #messagebox.showinfo(message=str(e), icon='error', title='Error')
            self.Model.LogInfo(ex=e)
            self.UpdateModelViewer()
            raise e
        self.UpdateModelViewer()

    def OnShowGraph(self):
        self.Parameters.SetModel(self.Model)
        self.FramePlotter = sfc_gui.chart_plotter.ChartPlotterFrame(self, parameters=self.Parameters)
        self.FramePlotter.OnSettingsCallback = self.ShowSettings
        self.FramePlotter.tkraise()

    def ShowSettings(self):
        settings = sfc_gui.chart_plotter.SettingsWindow(self, parameters=self.Parameters)
        settings.OnCloseCallback = self.OnSettingsClose
        settings.tkraise()

    def OnSettingsClose(self):
        self.FramePlotter.Update()

    def OnGenerateFullCodes(self):
        self.Model._GenerateFullSectorCodes()
        self.UpdateModelViewer()

    def OnFixAliases(self):
        self.Model._FixAliases()
        self.UpdateModelViewer()

    def OnGenerateEquations(self):
        if len(self.Sectors) == 0:
            return
        sector = self.Sectors.pop(0)
        print(sector.Code)
        sector._GenerateEquations()
        self.UpdateModelViewer()

    def OnModelViewerBack(self):
        self.FrameChooser.tkraise()

    def GetModelName(self):
        return self.WidgetsChooser.GetListBox('models')

    def OnRunModel(self):
        name = self.GetModelName()
        if name is None:
            # Not sure how we get here, but, go back to chooser frame
            self.FrameChooser.tkraise()
            return
        self.CleanupOnModelChange()
        Logger.cleanup()
        if not self.Parameters.LogDir == '':
            base_name = os.path.join(self.Parameters.LogDir, name)
            Logger.register_standard_logs(base_file_name=base_name)
        python_mod = self.Importer(name)
        try:
            self.Model = python_mod.build_model()
        except Exception as e:
            messagebox.showinfo(message=str(e), icon='error', title='Error')
            raise e
        if type(self.Model) is not Model:
            raise ValueError('Expected a Model, got {0} instead'.format(type(Model)))
        self.Sectors = self.Model.GetSectors()
        self.UpdateModelViewer()
        self.FrameModelViewer.tkraise()

    def CleanupOnModelChange(self):
        kept_list = ('FINAL*EQUATIONS', 'CHANGED*EQUATIONS', 'SECTOR*EQUATIONS')
        treewidget = self.WidgetsModelViewer.Widgets['equations']
        children = treewidget.get_children()
        self.Sectors = []
        for child in children:
            if child not in kept_list:
                treewidget.delete(child)
            else:
                self.WidgetsModelViewer.DeleteTreeChildren('equations', child)


    def UpdateModelViewer(self, event=None):
        name = self.GetModelName()
        self.WidgetsModelViewer.Data['model_name'].set(name)
        self.WidgetsModelViewer.Data['model_state'].set(self.Model.State)
        steps = self.Model._GetSteps()
        if len(steps) == 0:
            self.WidgetsModelViewer.Data['possible_steps'].set('')
        else:
            self.WidgetsModelViewer.SetListBox('possible_steps', steps[0])
        if len(steps) == 0:
            next_step = ''
        else:
            next_step = self.WidgetsModelViewer.GetListBox('possible_steps')
            if next_step is None:
                next_step = steps[0][0]
        self.WidgetsModelViewer.Data['next_step'].set(next_step)
        treewidget = self.WidgetsModelViewer.Widgets['equations']
        country_list =   [x.Code for x in self.Model.CountryList]
        final_name = 'FINAL*EQUATIONS'
        root_list = [final_name, 'CHANGED*EQUATIONS', 'SECTOR*EQUATIONS'] + country_list
        # First: Eliminate countries (and children) that do not exist.
        on_tree = treewidget.get_children()
        # Cannot iterate on get_children(), as we modify the output with every delete!
        for name in on_tree:
            if name not in root_list:
                treewidget.delete(name)
        self.PreviousEquations = tuple(self.CurrentEquations)
        self.CurrentEquations = []
        # FINAL_EQUATIONS
        if final_name not in on_tree:
            treewidget.insert('', 'end',final_name,
                              text=self.WidgetsModelViewer.Data['parameter_final_equation'],
                              open=False)
        if 'SECTOR*EQUATIONS' not in on_tree:
            treewidget.insert('', 'end', 'SECTOR*EQUATIONS', text='Sector Equations', open=False)
        if 'CHANGED*EQUATIONS' not in on_tree:
            treewidget.insert('', 'end', 'CHANGED*EQUATIONS', text='Changed Equations', open=False)
        self.WidgetsModelViewer.DeleteTreeChildren('equations', final_name)
        num_final = 0
        for varname in self.Model.FinalEquationBlock.GetEquationList():
            num_final += 1
            eqn = self.Model.FinalEquationBlock[varname]
            eqn_str = '{0} = {1}'.format(varname, eqn.GetRightHandSide())
            treewidget.insert(final_name, 'end', varname,
                              text=eqn.LeftHandSide,
                              values=(eqn_str, eqn.Description))
        self.WidgetsModelViewer.Data['num_final_eqn'].set(str(num_final))
        num_sector_equations = 0
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
                    num_sector_equations += 1
                    eqn = variable_lookup[var_code]
                    rhs = eqn.GetRightHandSide()
                    eqn_str = "{0} = {1}".format(eqn.LeftHandSide, rhs)
                    if not sector_obj.FullCode == '':
                        fullname = sector_obj.GetVariableName(eqn.LeftHandSide)
                        self.CurrentEquations.append(
                            (fullname, '{0} = {1}'.format(fullname, rhs), eqn.Description))
                    if var_code not in variables_on_tree:
                        treewidget.insert(sector_code, 'end', var_code,
                                          text=eqn.LeftHandSide,
                                          values=(eqn_str, eqn.Description))
                    else:
                        treewidget.item(var_code, values=(eqn_str, eqn.Description))
        self.WidgetsModelViewer.Data['num_sector_eqn'].set(str(num_sector_equations))
        self.CurrentEquations.sort()
        changed_equations = []
        for x in self.CurrentEquations:
            if x not in self.PreviousEquations:
                changed_equations.append(x)
        self.WidgetsModelViewer.DeleteTreeChildren('equations', 'CHANGED*EQUATIONS')
        for varname, eqn_str, desc in changed_equations:
            treewidget.insert('CHANGED*EQUATIONS', 'end','C*'+varname, text=varname, values=(eqn_str, desc))
        on_tree = treewidget.get_children('SECTOR*EQUATIONS')
        for pos in range(0, len(self.CurrentEquations)):
            varname, eqn_str, desc = self.CurrentEquations[pos]
            ccode = 'S*' + varname
            if ccode in on_tree:
                treewidget.item(ccode, values=(eqn_str, desc))
            else:
                treewidget.insert('SECTOR*EQUATIONS', pos, text=varname,
                                  values=(eqn_str, desc))

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
        self.Parameters.LogDir = target

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
        self.WidgetsChooser.SetListBox('models', acceptable)

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
