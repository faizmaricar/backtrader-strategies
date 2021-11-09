from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

class MacdPivot(bt.Strategy):
    def __init__(self):
        macd = bt.indicators.MACD(self.data0)
        self.macdcrossover = bt.indicators.CrossOver(macd.macd, macd.signal)
        self.pivotindicator = bt.indicators.PivotPoint(self.data1)

    def notify_data(self, data, status):
        if status == data.LIVE:
            self.data_ready = True

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.5f, Cost: %.5f, Comm %.5f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.5f' % trade.pnl)
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime()
        print('%s, %s' % (dt.isoformat(), txt))

    def log_data(self):
        ohlc = []
        ohlc.append(str(self.data0.datetime.datetime()))
        ohlc.append(str(self.data0.open[0]))
        ohlc.append(str(self.data0.close[0]))
        ohlc.append(str(self.data0.high[0]))
        ohlc.append(str(self.data0.low[0]))
        print(', '.join(ohlc))
    
    def next(self):
        # if not self.data_ready:
        #     return;
        self.log_data()
                    
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MacdPivot)

    ibstore = bt.stores.IBStore(port=7497)
    
    cerebro.broker = ibstore.getbroker()
    
    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', timeframe=bt.TimeFrame.Minutes, compression=5)
    
    cerebro.adddata(data)
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days, compression=1)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)

    cerebro.run()