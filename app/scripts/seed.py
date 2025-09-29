from app.core.database import SessionLocal
from app.core.models.market_data import Symbol

def seed_tickers():
    db = SessionLocal()
    try:
        tickers_to_seed = [
            {"ticker": "PETR4.SA", "name": "Petrobras PN"},
            {"ticker": "VALE3.SA", "name": "Vale ON"},
            {"ticker": "ITUB4.SA", "name": "Itau Unibanco PN"},
            {"ticker": "BBDC4.SA", "name": "Bradesco PN"},
        ]

        print("Cadastrando tickers iniciais...")
        for ticker_data in tickers_to_seed:
            exists = db.query(Symbol).filter(Symbol.ticker == ticker_data["ticker"]).first()
            if not exists:
                db.add(Symbol(**ticker_data))
        
        db.commit()
        print("Tickers cadastrados com sucesso!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_tickers()