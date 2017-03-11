# coding=utf-8
# import sfc_models.gl_book.chapter3 as chapter3
from sfc_models.objects import *
from sfc_gui.chart_plotter import ChartPlotterWindow2

mod = Model()
# Create first country - Canada. (This model only has one country.)
can = Country(mod, 'Canada', 'CA')
# Create sectors
gov = DoNothingGovernment(can, 'Government', 'GOV')
hh = Household(can, 'Household', 'HH', alpha_income=.6, alpha_fin=.4)
bus = FixedMarginBusiness(can, 'Business Sector', 'BUS', profit_margin=0.0)
# Create the linkages between sectors - tax flow, markets - labour ('LAB'), goods ('GOOD')
tax = TaxFlow(can, 'TaxFlow', 'TF', .2)
labour = Market(can, 'Labour market', 'LAB')
goods = Market(can, 'Goods market', 'GOOD')
# Need to set the exogenous variable - Government demand for Goods ("G" in economist symbology)
mod.AddExogenous('GOV', 'DEM_GOOD', '[0.,]*5 + [20.,] * 105')
mod.AddGlobalEquation('t', 'Decorated Time Axis', '1950.0 + 0.25*k')

#builder = chapter3.SIM('CAN')
#mod = builder.build_model()

mod.main()

window = ChartPlotterWindow2(None, mod)
window.mainloop()


