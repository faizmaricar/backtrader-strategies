from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta
from itertools import compress

import backtrader as bt

from macddmi import MacdDmi
from macdema import MacdEma
from macdpivot import MacdPivot

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MacdPivot)

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
        fromdate = datetime.today() - timedelta(days=30),
        latethrough = False,  
        tradename = None,
        compression=15
    )
    
    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', **dataargs)

    cerebro.adddata(data) 
    resampledData = cerebro.resampledata(data, timeframe=bt.TimeFrame.Days, compression=3)
    resampledData.plotinfo.plot = False
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)
    
    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.run()
    
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.plot()