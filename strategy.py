import backtrader as bt

from colorama import Fore, Style

class Strategy(bt.Strategy):
    data_ready = False
    order = None   

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime()
        print('%s, %s' % (dt.isoformat(), txt))

    def log_data(self):
        ohlc = []
        ohlc.append(str(self.data.datetime.datetime()))
        ohlc.append(str(self.data.open[0]))
        ohlc.append(str(self.data.high[0]))
        ohlc.append(str(self.data.low[0]))
        ohlc.append(str(self.data.close[0]))
        print(', '.join(ohlc))
    
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
        
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        if trade.pnl > 0:
            print(Fore.GREEN, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)
        else:
            print(Fore.RED, 'OPERATION PROFIT, GROSS %.2f' % trade.pnl, Style.RESET_ALL)