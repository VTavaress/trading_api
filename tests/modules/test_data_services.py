from unittest.mock import patch
import pandas as pd
from datetime import datetime

from app.modules.data import services
from app.core.models.market_data import Symbol, Price

def test_fetch_and_store_ohlcv_new_symbol(db_session):
    """
    Testa a função de buscar dados para um novo símbolo.
    """
    fake_data = {
        'Open': [10.0], 'High': [10.5], 'Low': [9.5], 
        'Close': [10.2], 'Volume': [1000]
    }
    fake_dates = [datetime(2023, 1, 2)]
    fake_dataframe = pd.DataFrame(data=fake_data, index=pd.Index(fake_dates, name="Date"))

    with patch('app.modules.data.services.yf.download') as mock_download:
        mock_download.return_value = fake_dataframe

        count = services.fetch_and_store_ohlcv(
            ticker="NEWTICKER.SA",
            start_date="2023-01-01",
            end_date="2023-01-03",
            db=db_session
        )

        assert count == 1
        symbol_in_db = db_session.query(Symbol).filter(Symbol.ticker == "NEWTICKER.SA").first()
        assert symbol_in_db is not None
        assert symbol_in_db.name == "NEWTICKER.SA"