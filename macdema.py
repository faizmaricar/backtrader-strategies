from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt

class MacdEma(bt.Strategy):

    params = (
        ('period_me1', 12),
        ('period_me2', 26),
        ('period_signal', 9)
    )

    def __init__(self):
        self.orders = None
        self.macd = bt.indicators.MACD(
            self.datas[0], 
            period_me1=self.params.period_me1, 
            period_me2=self.params.period_me2,
            period_signal=self.params.period_signal, 
            subplot=False
        )
        
        self.macdcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.ema100 = bt.indicators.EMA(self.datas[0], period=100)
        
    def notify_data(self, data, status):
        if status == data.LIVE:
            self.data_ready = True

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED Price: %.5f' % order.executed.price)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED Price: %.5f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.5f' % trade.pnl)
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))
    
    def log_data(self):
        ohlcv = []
        ohlcv.append(str(self.data.datetime.datetime()))
        ohlcv.append(str(self.data.open[0]))
        ohlcv.append(str(self.data.high[0]))
        ohlcv.append(str(self.data.low[0]))
        ohlcv.append(str(self.data.close[0]))
        ohlcv.append(str(self.macdcross[0]))
        self.log(', '.join(ohlcv))

    def next(self):  
        # Use when trading
        # if not self.data_ready:
        #    return
        # self.log_data()
        if not self.position:
            take_profit = 0.001
            if self.macdcross[0] > 0 and self.data.low[0] > self.ema100[0]:
                orderags = dict(
                    limitprice=self.data.close[0] + take_profit,
                    price=self.data.close[0],
                    stopexec=bt.Order.StopTrailLimit
                )
                self.orders = self.buy_bracket(**orderags)
                self.log('BUY CREATE')
            elif self.macdcross[0] < 0 and self.data.low[0] > self.ema100[0]:
                orderags = dict(
                    limitprice=self.data.close[0] - take_profit,
                    price=self.data.close[0],
                    stopexec=bt.Order.StopTrailLimit
                )
                self.orders = self.sell_bracket(**orderags)
                self.log('SELL CREATE')

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MacdEma)

    ibstore = bt.stores.IBStore(port=7497)
    
    cerebro.broker = ibstore.getbroker()
    
    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', timeframe=bt.TimeFrame.Minutes)
        
    cerebro.resampledata(data, timeframe=bt.TimeFrame.Days)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)
    
    cerebro.run()