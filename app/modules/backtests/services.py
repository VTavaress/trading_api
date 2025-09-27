import backtrader as bt
from sqlalchemy.orm import Session, joinedload
import pandas as pd
from datetime import datetime

from core.database import SessionLocal
from core.models.market_data import Price, Symbol
from core.models.backtest_results import Backtest, Metric, Trade, DailyPosition
from modules.backtests.strategies import SmaCross, BreakoutStrategy
from modules.backtests.analyzers import TradeList

def run_backtest(ticker: str, start_date: str, end_date: str, strategy_type: str, 
                 strategy_params: dict, initial_cash: float, commission: float, db: Session):
    backtest_run = Backtest(
        ticker=ticker, start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
        strategy_type=strategy_type, strategy_params_json=strategy_params,
        initial_cash=initial_cash, commission=commission, status="running")
    db.add(backtest_run)
    db.commit()
    db.refresh(backtest_run)
    
    cerebro = bt.Cerebro()
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trade_analyzer')
    cerebro.addanalyzer(TradeList, _name='trade_list')

    query = db.query(Price.date, Price.open, Price.high, Price.low, Price.close, Price.volume)\
              .join(Price.symbol).filter(Symbol.ticker == ticker, Price.date.between(start_date, end_date))\
              .order_by(Price.date)
    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        raise ValueError("Não há dados para o ticker no período especificado.")
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)

    if strategy_type == "sma_cross":
        cerebro.addstrategy(SmaCross, **strategy_params)
    elif strategy_type == "breakout":
        cerebro.addstrategy(BreakoutStrategy, **strategy_params)
    else:
        raise ValueError(f"Estratégia '{strategy_type}' não suportada.")

    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    results = cerebro.run()
    strat = results[0]

    trade_analyzer = strat.analyzers.trade_analyzer.get_analysis()
    drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
    sharpe_analyzer = strat.analyzers.sharpe_ratio.get_analysis()
    trade_list = strat.analyzers.trade_list.get_analysis()

    metric = Metric(
        backtest_id=backtest_run.id,
        total_return=((cerebro.broker.getvalue() / initial_cash) - 1) * 100,
        sharpe=sharpe_analyzer.get('sharperatio', 0),
        max_drawdown=drawdown_analyzer.max.drawdown,
        win_rate=(trade_analyzer.won.total / trade_analyzer.total.total) * 100 if trade_analyzer.total.total > 0 else 0,
        avg_trade_return=trade_analyzer.pnl.net.average if trade_analyzer.total.total > 0 else 0,
        total_trades=trade_analyzer.total.total)
    db.add(metric)

    for t in trade_list:
        trade_record = Trade(
            backtest_id=backtest_run.id, date=datetime.fromisoformat(t['exit_date']).date(),
            side=t['direction'], price=t['entry_price'], size=t['size'], pnl=t['pnl_comm'])
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