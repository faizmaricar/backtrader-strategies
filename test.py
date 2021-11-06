from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta

import backtrader as bt

from teststrategy import TestStrategy
from macddmi import MacdDmi

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MacdDmi)

    ibstore = bt.stores.IBStore(port=7497)
    
    dataargs = dict(
        timeframe = bt.TimeFrame.Minutes,
        rtbar = False,
        historical = True,
        what = 'MIDPOINT',
        useRTH = False,
        qcheck = 0.5,
        backfill_start = True,
        backfill = True,
        fromdate = datetime.today() - timedelta(days=365),
        latethrough = False,  
        tradename = None
    )
    
    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', **dataargs)
        
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=1)
    
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)
    
    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.run()
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    #cerebro.plot()