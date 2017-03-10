import sfc_models.gl_book.chapter3 as chapter3
from sfc_gui.chart_plotter import ChartPlotterWindow2


builder = chapter3.SIM('CAN')

mod = builder.build_model()
mod.main()

window = ChartPlotterWindow2(None, mod, time_cut_off=40)
window.mainloop()


