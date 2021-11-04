import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        print('init strategy')
        self.data_ready = False

    def notify_data(self, data, status):
        if status == data.LIVE:
            self.data_ready = True
    
    def log_data(self):
        ohlcv = []
        ohlcv.append(str(self.data.datetime.datetime()))
        ohlcv.append(str(self.data.open[0]))
        ohlcv.append(str(self.data.high[0]))
        ohlcv.append(str(self.data.low[0]))
        ohlcv.append(str(self.data.close[0]))
        ohlcv.append(str(self.data.volume[0]))
        print(', '.join(ohlcv))

    def next(self):
        self.log_data()

        if not self.data_ready:
            return

        # if not self.position:
        #     self.buy()
        # elif self.position: 
        #     self.sell()