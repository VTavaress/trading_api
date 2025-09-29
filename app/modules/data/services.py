import yfinance as yf
from sqlalchemy.orm import Session
from app.core.models.market_data import Symbol, Price


def fetch_and_store_ohlcv(ticker: str, start_date: str, end_date: str, db: Session):
    symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
    if not symbol:
        symbol = Symbol(ticker=ticker, name=ticker)
        db.add(symbol)
        db.commit()
        db.refresh(symbol)
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        return 0
    prices_to_add = []
    for date, row in data.iterrows():
        exists = db.query(Price).filter(Price.symbol_id == symbol.id, Price.date == date.date()).first()
        if not exists:
            price = Price(
                symbol_id=symbol.id, date=date.date(), open=float(row['Open']),
                high=float(row['High']), low=float(row['Low']), close=float(row['Close']),
                volume=int(row['Volume'])
            )
            prices_to_add.append(price)
    if prices_to_add:
        db.bulk_save_objects(prices_to_add)
        db.commit()
        return len(prices_to_add)
    return 0