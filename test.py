from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from datetime import datetime, timedelta
from itertools import compress

import backtrader as bt
import backtrader.analyzers as btanalyzers

from macddmi import MacdDmi
from macdema import MacdEma
from macdpivot import MacdPivot
from eur0700 import Eur0700

if __name__ == '__main__':
    cerebro = bt.Cerebro(stdstats=False)

    cerebro.addstrategy(Eur0700)
    
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.Trades)
    cerebro.addobserver(bt.observers.BuySell)

    ibstore = bt.stores.IBStore(port=7497)
    
    dataargs = dict(
        timeframe = bt.TimeFrame.Minutes,
        compression=1,
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
    )
    
    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', **dataargs)

    cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)     
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.plot()