from sqlalchemy import (Column, Integer, String, Float, Date, ForeignKey, 
                        UniqueConstraint, DateTime)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Symbol(Base):
    __tablename__ = 'symbols'
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    exchange = Column(String)
    currency = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    prices = relationship("Price", back_populates="symbol")

class Price(Base):
    __tablename__ = 'prices'
    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey('symbols.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    symbol = relationship("Symbol", back_populates="prices")
    __table_args__ = (UniqueConstraint('symbol_id', 'date', name='_symbol_date_uc'),)