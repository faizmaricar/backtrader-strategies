import backtrader as bt

from datetime import datetime, timedelta
from colorama import Fore, Style

class SmaCrossoverStrategy(bt.Strategy):

    params = (
        ('short_ma', 20),
        ('long_ma', 50),
    )

    def __init__(self):
        shortsma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.short_ma, subplot=False)
        longsma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.long_ma, subplot=False)
        self.smacrossover = bt.indicators.CrossOver(shortsma, longsma)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        
        if trade.pnl > 0:
            print(Fore.GREEN, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)
        else:
            print(Fore.RED, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)

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
        
        self.order = None

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.smacrossover > 0:
                self.order = self.buy()
        else:
            if self.smacrossover < 0:
                self.order = self.sell()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCrossoverStrategy, short_ma=50, long_ma=200)
    
    ibstore = bt.stores.IBStore(port=7497)
    
    dataargs = dict(
        timeframe = bt.TimeFrame.Days,
        compression=1,
        rtbar = False,
        historical = True,
        what = 'MIDPOINT',
        useRTH = False,
        qcheck = 0.5,
        backfill_start = True,
        backfill = True,
        fromdate = datetime.today() - timedelta(days=365),
        latethrough = False,  
        tradename = None,
    )

    data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO', **dataargs)

    cerebro.adddata(data)    
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.plot(style='candlestick')