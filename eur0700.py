from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

from colorama import Fore, Style

class Eur0700(bt.Strategy):
    params = (
        ('trading', False),
        ('profit_take', 0.001),
        ('stop_loss', 0.0005),
        ('trail_amount', 0.0004),
    )

    def __init__(self):
        self.data_ready = False
        self.longorder = None
        self.shortorder = None


    def notify_data(self, data, status, *args, **kwargs):
        if status == data.LIVE:
            self.data_ready = True
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED Price: %.5f' % order.executed.price)
                if self.longorder:
                    self.profittaker = self.sell(
                        exectype=bt.Order.Limit,
                        price=self.high + self.params.profit_take
                    )
                    self.stoploss = self.sell(
                        exectype=bt.Order.StopTrail,
                        price=self.high - self.params.stop_loss,
                        trailamount=self.params.trail_amount,
                        oco=self.profittaker
                    )
            else:
                self.log('SELL EXECUTED Price: %.5f' % order.executed.price)
                if self.shortorder:
                    self.profittaker = self.buy(
                        exectype=bt.Order.Limit,
                        price=self.low - self.params.profit_take
                    )
                    self.stoploss = self.buy(
                        exectype=bt.Order.StopTrail,
                        price=self.low + self.params.stop_loss,
                        trailamount=self.params.trail_amount,
                        oco=self.profittaker
                    )
            self.bar_executed = len(self)
            

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        self.shortorder = None
        self.longorder = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        if trade.pnl > 0:
            print(Fore.GREEN, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)
        else:
            print(Fore.RED, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    

    def log_data(self):
        ohlc = []
        ohlc.append(str(self.data.datetime.datetime()))
        ohlc.append(str(self.data.open[0]))
        ohlc.append(str(self.data.high[0]))
        ohlc.append(str(self.data.low[0]))
        ohlc.append(str(self.data.close[0]))
        print(', '.join(ohlc))
       
    def next(self):
        if self.params.trading and not self.data_ready:
            return
        
        if self.longorder or self.shortorder:
            return

        getlevels = self.data.datetime.time().hour == 7
        tradestart = self.data.datetime.time().hour == 8
        tradestop = self.data.datetime.time().hour == 12
        
        if getlevels:
            self.high = self.data.high[0]
            self.low = self.data.low[0]
        
        if tradestart and not self.position:
            self.longorder = self.buy(
                exectype=bt.Order.StopLimit,
                price=self.high,
                plimit=self.high + 0.00001
            )
            self.shortorder = self.sell(
                exectype=bt.Order.StopLimit,
                price=self.low,
                plimit=self.low - 0.00001,
                oco=self.longorder
            )
        elif tradestop and self.position:
            self.close()
            self.cancel(order=self.profittaker)
            self.cancel(order=self.stoploss)
            self.profittaker = None
            self.stoploss = None 
            
if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(Eur0700, trading=True)
    
    ibstore = bt.stores.IBStore(port=7497)
    
    cerebro.broker = ibstore.getbroker()
    
    dataargs = dict(
        dataname='EUR.USD',
        sectype='CASH',
        exchange='IDEALPRO',
        timeframe=bt.TimeFrame.Minutes,
        compression=60
    )

    data = ibstore.getdata(**dataargs)

    cerebro.adddata(data)    
    cerebro.addsizer(bt.sizers.FixedSize, stake=65000)
        
    cerebro.run()