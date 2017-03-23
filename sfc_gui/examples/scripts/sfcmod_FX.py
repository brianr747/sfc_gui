
from sfc_models import register_standard_logs
from sfc_models.objects import *
from sfc_models.sector import Sector
from sfc_gui.chart_plotter import ChartPlotterWindow2


def get_description():
    return "ModelFX"

def build_model():
    mod = Model()
    ext = ExternalSector(mod)
    ca = Country(mod, 'Canada', 'CA', currency='CAD')
    us = Country(mod, 'United States', 'US', currency='USD')

    xrate = ext.GetCrossRate('CAD', 'USD')
    xrate = ext.GetCrossRate('USD', 'CAD')
    hh_ca = Sector(ca, 'Canada HH', 'HH')
    hh_us = Sector(us, 'US HH', 'HH')
    hh_ca.AddVariable('GIFT', 'Gifts!', '5.')
    fx = ext['FX']
    xr = ext['XR']
    # hh_ca.AddVariable('GOLDPURCHASES', 'Yeah', '-GIFT')
    # ext['GOLD'].SetGoldPurchases(hh_ca, 'GOLDPURCHASES', 100.)
    tre = Treasury(ca, 'Ministry O Finance', 'TRE')
    cb_ca = GoldStandardCentralBank(ca, 'Bank O Canada', 'CB', tre, 1000)
    mm = MoneyMarket(ca, issuer_short_code='CB')
    dep = DepositMarket(ca, issuer_short_code='TRE')
    tax = TaxFlow(ca, 'TaxFlow', 'TF', .2, taxes_paid_to='TRE')
    xr.SetExogenous('CAD', '[1.5,]*100')
    mod.EquationSolver.MaxTime= 10
    mod.RegisterCashFlow(hh_ca, hh_us, 'GIFT', False, True)
    mod.EquationSolver.TraceStep = 4
    # fx._SendMoney(hh_ca, 'GIFT')
    # fx._ReceiveMoney(hh_us, hh_ca, 'GIFT')

    return mod



if __name__ == '__main__':
    register_standard_logs('output', __file__)
    mod2 = build_model()
    mod2.main()
    window = ChartPlotterWindow2(None, mod2)
    window.mainloop()