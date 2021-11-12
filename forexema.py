import backtrader as bt

from datetime import datetime, timedelta

from strategy import Strategy

class ForexEmaStrategy(Strategy):
    params = (
        ('trading', False),
        ('shortema', 5),
        ('mediumema', 20),
        ('longema', 50),
    )
    
    def __init__(self):
        self.shortema = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.shortema)
        self.mediumema = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.mediumema)
        self.longema = bt.indicators.ExponentialMovingAverage(self.data, period=self.params.longema)

        self.shortemacrossover = bt.indicators.CrossOver(self.shortema, self.mediumema)

    def next(self):
        if self.params.trading and not self.data_ready:
            return
        
        if self.params.trading:
            self.log_data()

        if self.order:
            return
        
        if not self.position:
            if self.shortemacrossover > 0 and self.data.low[0] > self.longema and self.mediumema > self.longema and self.shortema > self.longema:
                self.order = self.buy_bracket(
                    price=self.data.close[0],
                    limitprice=self.data.close[0] + 0.002,
                    stopprice=self.data.close[0] - 0.001,
                    stopexec=bt.Order.StopTrail,
                    trailamount=0.001
                )
            if self.shortemacrossover < 0 and self.data.high[0] < self.longema and self.mediumema < self.longema and self.shortema < self.longema:
                self.order = self.sell_bracket(
                    price=self.data.close[0],
                    limitprice=self.data.close[0] - 0.002,
                    stopprice=self.data.close[0] + 0.001,
                )
        else:
            if self.position.size > 0 and self.shortemacrossover < 0:
                self.close()
            elif self.position.size < 0 and self.shortemacrossover > 0:
                self.close()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(ForexEmaStrategy, trading=False)
    
    ibstore = bt.stores.IBStore(port=7497)
    
    dataargs = dict(
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
    #data = ibstore.getdata(dataname='EUR.USD', sectype='CASH', exchange='IDEALPRO')

    cerebro.resampledata(data, timeframe= bt.TimeFrame.Minutes, compression=5)     
    cerebro.broker.setcash(100000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=70000)

    print('Starting portfolio value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    
    cerebro.plot()