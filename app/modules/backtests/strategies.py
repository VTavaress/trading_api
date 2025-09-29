import backtrader as bt
import math
import pandas as pd

class SmaCross(bt.Strategy):
    """
    Estratégia de Cruzamento de Médias Móveis com Gestão de Risco (ATR Stop Loss e Position Sizing).
    """
    params = (
        ('fast', 50), 
        ('slow', 200),
        ('atr_period', 14),
        ('atr_multiplier', 2.0),
        ('risk_pct', 0.01),
    )

    def __init__(self):
        sma_fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast)
        sma_slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(sma_fast, sma_slow)
        self.atr = bt.indicators.AverageTrueRange(period=self.p.atr_period)
        self.stop_order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status == order.Completed and order.isbuy():
            stop_price = order.executed.price - (self.atr[0] * self.p.atr_multiplier)
            self.stop_order = self.sell(exectype=bt.Order.Stop, price=stop_price, size=order.executed.size)
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            if self.stop_order and self.stop_order.ref == order.ref:
                self.stop_order = None

    def next(self):
        if self.stop_order:
            return
        if not self.position:
            if self.crossover > 0:
                stop_distance_points = self.atr[0] * self.p.atr_multiplier
                if stop_distance_points == 0: return
                capital_total = self.broker.getvalue()
                risk_amount_per_trade = capital_total * self.p.risk_pct
                size = math.floor(risk_amount_per_trade / stop_distance_points)
                if size > 0:
                    self.buy(size=size)
        else:
            if self.crossover < 0:
                self.close()

class BreakoutStrategy(bt.Strategy):
    """
    Estratégia de Breakout (Rompimento de Máximas/Mínimas).
    """
    params = (
        ('breakout_period', 20),
        ('exit_period', 10),
    )

    def __init__(self):
        self.highest_high = bt.indicators.Highest(self.data.high, period=self.p.breakout_period)
        self.lowest_low_exit = bt.indicators.Lowest(self.data.low, period=self.p.exit_period)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.highest_high[-1]:
                self.buy(size=100)
        else:
            if self.data.close[0] < self.lowest_low_exit[-1]:
                self.close()

class SmaCrossML(SmaCross):
    """
    Estratégia SmaCross que só compra se o modelo de ML prever um dia de alta.
    Herda toda a lógica de gestão de risco da SmaCross.
    """
    def __init__(self):
        super().__init__()
        self.ml_model = self.p.ml_model
        self.ml_features = self.p.ml_features
    
    def next(self):
        if self.stop_order:
            return

        if not self.position:
            if self.crossover > 0:
                try:
                    current_data = {f: [self.data.close.pct_change(int(f.split('_')[1][:-1]))[0]] for f in self.ml_features}
                    current_df = pd.DataFrame(current_data)
                    
                    if current_df.isnull().values.any():
                        return 
                    
                    prediction = self.ml_model.predict(current_df)[0]
                    
                    if prediction == 1:
                        stop_distance_points = self.atr[0] * self.p.atr_multiplier
                        if stop_distance_points == 0: return
                        capital_total = self.broker.getvalue()
                        risk_amount_per_trade = capital_total * self.p.risk_pct
                        size = math.floor(risk_amount_per_trade / stop_distance_points)
                        if size > 0:
                            self.buy(size=size)
                except IndexError:

                    pass
        else:
            if self.crossover < 0:
                self.close()