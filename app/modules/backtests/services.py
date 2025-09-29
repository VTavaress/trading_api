import backtrader as bt
from sqlalchemy.orm import Session, joinedload
import pandas as pd
from datetime import datetime

from app.core.database import SessionLocal
from app.core.models.market_data import Price, Symbol
from app.core.models.backtest_results import Backtest, Metric, Trade
from app.modules.ml.services import train_prediction_model
from app.modules.backtests.strategies import SmaCross, BreakoutStrategy
from app.modules.backtests.analyzers import TradeList

class SmaCrossML(bt.Strategy):
    params = (
        ('fast', 10),
        ('slow', 30),
        ('ml_feature_cols', None),  
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma_fast = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.fast)
        self.sma_slow = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.slow)

        if hasattr(self.datas[0], '_ml_model'):
            self.ml_model = self.datas[0]._ml_model
        else:
            self.ml_model = None

    def next(self):
        if self.ml_model is None:
            return  

        X = [self.datas[0].close[0]] 
        pred = self.ml_model.predict([X])[0]

        if self.dataclose[0] > self.sma_fast[0] and self.dataclose[0] > self.sma_slow[0] and pred == 1:
            self.buy()
        elif self.dataclose[0] < self.sma_fast[0] and self.dataclose[0] < self.sma_slow[0] and pred == -1:
            self.sell()


def run_backtest(ticker: str, start_date: str, end_date: str, strategy_type: str, 
                 strategy_params: dict, initial_cash: float, commission: float, db: Session):
    
    backtest_run = Backtest(
        ticker=ticker,
        start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
        strategy_type=strategy_type,
        strategy_params_json=strategy_params,
        initial_cash=initial_cash,
        commission=commission,
        status="running"
    )
    db.add(backtest_run)
    db.flush()

    cerebro = bt.Cerebro()
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(TradeList, _name='trade_list')

    query = db.query(Price.date, Price.open, Price.high, Price.low, Price.close, Price.volume)\
              .join(Price.symbol)\
              .filter(Symbol.ticker == ticker, Price.date.between(start_date, end_date))\
              .order_by(Price.date)
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        raise ValueError("Não há dados para o ticker no período especificado.")
    
    ml_model, ml_features = None, None
    if strategy_type == "sma_cross_ml":
        ml_model, ml_features = train_prediction_model(df.copy())
        if ml_model is None:
            raise ValueError("Não foi possível treinar o modelo de ML com os dados disponíveis.")

    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df.columns = [col.lower() for col in df.columns]
    df.dropna(inplace=True)

    # Adiciona o modelo ML ao DataFrame para a estratégia
    if ml_model is not None:
        df._ml_model = ml_model

    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)

    # Seleciona a estratégia
    if strategy_type == "sma_cross":
        cerebro.addstrategy(SmaCross, **strategy_params)
    elif strategy_type == "breakout":
        cerebro.addstrategy(BreakoutStrategy, **strategy_params)
    elif strategy_type == "sma_cross_ml":
        cerebro.addstrategy(SmaCrossML, **strategy_params)
    else:
        raise ValueError(f"Estratégia '{strategy_type}' não suportada.")

    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    initial_portfolio_value = cerebro.broker.getvalue()
    results = cerebro.run()
    strat = results[0]
    final_portfolio_value = cerebro.broker.getvalue()

    trade_analyzer = strat.analyzers.trade_analyzer.get_analysis()
    drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
    sharpe_analyzer = strat.analyzers.sharpe_ratio.get_analysis()
    trade_list = strat.analyzers.trade_list.get_analysis()

    metric = Metric(
        backtest_id=backtest_run.id,
        total_return=((final_portfolio_value / initial_portfolio_value) - 1) * 100,
        sharpe=sharpe_analyzer.get('sharperatio', 0),
        max_drawdown=drawdown_analyzer.get('max', {}).get('drawdown', 0),
        win_rate=(trade_analyzer['won']['total'] / trade_analyzer['total']['total'] * 100)
                 if trade_analyzer['total']['total'] > 0 else 0,
        avg_trade_return=(trade_analyzer['pnl']['net']['average']
                          if trade_analyzer['total']['total'] > 0 else 0),
        total_trades=trade_analyzer['total']['total']
    )
    db.add(metric)

    for t in trade_list:
        trade_record = Trade(
            backtest_id=backtest_run.id,
            date=datetime.fromisoformat(t['exit_date']).date(),
            side=t['direction'],
            price=t['entry_price'],
            size=t['size'],
            pnl=t['pnl_comm']
        )
        db.add(trade_record)
    
    backtest_run.status = "completed"
    db.commit()
    db.refresh(backtest_run)
    return backtest_run


def get_backtest_results(db: Session, backtest_id: int):
    return db.query(Backtest).options(
        joinedload(Backtest.metrics),
        joinedload(Backtest.trades)
    ).filter(Backtest.id == backtest_id).first()


def list_backtests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Backtest).order_by(Backtest.id.desc()).offset(skip).limit(limit).all()
