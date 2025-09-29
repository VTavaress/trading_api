from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch
import pandas as pd
from datetime import datetime

from app.core.models.market_data import Price, Symbol

def test_fetch_data_success(test_client: TestClient, db_session: Session):
    """
    Testa o sucesso do endpoint de busca de dados, verificando se os
    dados são guardados corretamente na base de dados de teste.
    """
    fake_data = {
        'Open': [10.0, 11.0], 'High': [10.5, 11.5],
        'Low': [9.5, 10.5], 'Close': [10.2, 11.2],
        'Volume': [1000, 1500]
    }
    fake_dates = [datetime(2023, 1, 2), datetime(2023, 1, 3)]
    fake_dataframe = pd.DataFrame(data=fake_data, index=pd.Index(fake_dates, name="Date"))

    with patch('app.modules.data.services.yf.download') as mock_download:
        mock_download.return_value = fake_dataframe

        request_payload = {
            "ticker": "TEST4.SA",
            "start_date": "2023-01-01",
            "end_date": "2023-01-03"
        }
        response = test_client.post("/api/v1/data/fetch", json=request_payload)

        assert response.status_code == 200
        
       
        assert "novos registros adicionados" in response.json()["message"]

        symbol_in_db = db_session.query(Symbol).filter(Symbol.ticker == "TEST4.SA").first()
        assert symbol_in_db is not None

        prices_in_db = db_session.query(Price).filter(Price.symbol_id == symbol_in_db.id).all()
        assert len(prices_in_db) == 2
        
        assert prices_in_db[0].open == 10.0
        assert prices_in_db[1].close == 11.2