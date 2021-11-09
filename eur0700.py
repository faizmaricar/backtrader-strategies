from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

class Eur0700(bt.Strategy):
    params = (
        ('take_profit', 0.005),
        ('stop_loss', 0.001),
        ('trail_amount', 0.001)
    )
    def __init__(self) -> None:
        self.data_ready = None
        self.o1 = None
        self.o2 = None
        self.high = None
        self.low = None
    
    def notify_data(self, data, status):
        if status == data.LIVE:
            self.data_ready = True

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.5f' % order.executed.price )
                if self.o1:
                    pt = self.sell(
                        price=self.high + self.params.take_profit, 
                        exectype=bt.Order.Limit
                    )
                    self.sell(
                        price=self.high - self.params.stop_loss,
                        exectype=bt.Order.StopTrail,
                        trailamount=self.params.trail_amount,
                        oco=pt
                    )
            else:
                self.log('SELL EXECUTED, Price: %.5f' % order.executed.price)
                if self.o2:
                    pt = self.buy(
                        price=self.low - self.params.take_profit,
                        exectype=bt.Order.Limit
                    )
                    self.buy(
                        price=self.low + self.params.stop_loss,
                        exectype=bt.Order.StopTrail,
                        trailamount=self.params.trail_amount, 
                        oco=pt
                    )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.o1 = None
        self.o2 = None
    
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f' % trade.pnl)

    def log(self, txt, dt=None):
        dt = dt or self.data0.datetime.datetime()
        print('%s, %s' % (str(dt), txt))

    def log_data(self):
        ohlc = []
        ohlc.append(str(self.data0.datetime.datetime()))
        ohlc.append(str(self.data0.open[0]))
        ohlc.append(str(self.data0.high[0]))
        ohlc.append(str(self.data0.low[0]))
        ohlc.append(str(self.data0.close[0]))
        print(', '.join(ohlc))

    def next(self):
        #if not self.data_ready:
        #  return
        #         
        if self.o2 or self.o1:
            return
        
        tradestart = self.datas[1].datetime.time().hour == 8
        if tradestart and not self.position:
            self.high = self.datas[1].high[-1]
            self.low = self.datas[1].low[-1]
            
            self.o1 = self.buy(
                exectype=bt.Order.StopLimit,
                price=self.high,
                plimit=self.high + 0.00001
            )
            
            self.o2 = self.sell(
                exectype=bt.Order.StopLimit,
                price=self.low,
                plimit=self.low - 0.00001,
                oco=self.o1
            )
                
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(Eur0700)
    
    ibstore = bt.stores.IBStore(port=7497)
    
    cerebro.broker = ibstore.getbroker()

    dataargs = dict(
        dataname='EUR.USD',
        sectype='CASH',
        exchange='IDEALPRO',
        timeframe=bt.TimeFrame.Minutes
    )

    data = ibstore.getdata(**dataargs)

    cerebro.adddata(data)
    
    resampledData = cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, compression=60)
    
    cerebro.addsizer(bt.sizers.FixedSize, stake=65000)
        
    cerebro.run()