from sqlalchemy import (Column, Integer, String, Float, Date, ForeignKey, 
                        DateTime, JSON)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Backtest(Base):
    __tablename__ = 'backtests'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ticker = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    strategy_type = Column(String, nullable=False)
    strategy_params_json = Column(JSON)
    initial_cash = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    status = Column(String, default="running")
    metrics = relationship("Metric", back_populates="backtest", uselist=False)
    trades = relationship("Trade", back_populates="backtest")
    daily_positions = relationship("DailyPosition", back_populates="backtest")

class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False, unique=True)
    total_return = Column(Float)
    sharpe = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    avg_trade_return = Column(Float)
    total_trades = Column(Integer)
    backtest = relationship("Backtest", back_populates="metrics")

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    date = Column(Date)
    side = Column(String)
    price = Column(Float)
    size = Column(Float)
    commission = Column(Float)
    pnl = Column(Float)
    backtest = relationship("Backtest", back_populates="trades")

class DailyPosition(Base):
    __tablename__ = 'daily_positions'
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey('backtests.id'), nullable=False)
    date = Column(Date, nullable=False)
    position_size = Column(Float)
    cash = Column(Float)
    equity = Column(Float)
    drawdown = Column(Float)
    backtest = relationship("Backtest", back_populates="daily_positions")