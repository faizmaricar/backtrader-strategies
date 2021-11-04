import backtrader as bt

class EurUsd0730(bt.strategy):

    # Check if its 0730 GMT
    # Look at three trends: SuperTrend, MACD, DMI
    # Buy if all three trends are positive 
    # Sell if all three trends are negative
    # Profit target: 12 pips, Stop loss: 48 period High-Low stop
    # Exit trader if its 1200 GMT
    def __init__(self):

        self.macd = bt.indicators.macd(self.datas[0])
        pass