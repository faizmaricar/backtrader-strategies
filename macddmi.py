import backtrader as bt

class MacdDmi(bt.Strategy):

    params = (
        ('period_me1', 12),
        ('period_me2', 26),
        ('period_signal', 9)
    )

    def __init__(self):
        self.orders = None
        
        self.highest = bt.indicators.Highest(self.data.high, period=48, subplot=False)
        self.lowest = bt.indicators.Lowest(self.data.low, period=48, subplot=False)

        self.macd = bt.indicators.MACD(
            self.datas[0], 
            period_me1=self.params.period_me1, 
            period_me2=self.params.period_me2,
            period_signal=self.params.period_signal, 
            subplot=False
        )

        self.dmi = bt.indicators.DirectionalMovementIndex(self.datas[0], subplot=False)

        self.macdcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.dmicross = bt.indicators.CrossOver(self.dmi.plusDI, self.dmi.minusDI)
        
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
        ohlcv.append(str(self.dmicross[0]))
        print(', '.join(ohlcv))

    def next(self):        
        if not self.position:
            take_profit = 0.0004
            if self.macdcross[0] > 0 and self.dmicross[0] > 0:
                orderags = dict(
                    limitprice=self.data.close[0] + take_profit,
                    price=self.data.close[0],
                )
                self.orders = self.buy_bracket(**orderags, stopexec=bt.Order.StopTrailLimit)
                self.log('BUY CREATE')
            elif self.macdcross[0] < 0 and self.dmicross[0] < 0:
                orderags = dict(
                    limitprice=self.data.close[0] - take_profit,
                    price=self.data.close[0],
                )
                self.orders = self.sell_bracket(**orderags, stopexec=bt.Order.StopTrailLimit, trailamount=0.0001)
                self.log('SELL CREATE')