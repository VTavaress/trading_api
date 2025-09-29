from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.core.models.backtest_results import Backtest

def test_run_backtest_success(test_client: TestClient, db_session: Session):
    """
    Testa o sucesso do endpoint de execução de backtest, verificando se
    um novo registro de backtest é criado no banco de dados.
    """
    
    with patch('app.api.v1.endpoints.backtests.services.run_backtest') as mock_run_backtest:
        
        mock_backtest_run = MagicMock()
        mock_backtest_run.id = 1
        mock_backtest_run.status = "completed"
        mock_backtest_run.ticker = "TEST4.SA"
        mock_backtest_run.strategy_type = "sma_cross"
        mock_backtest_run.created_at = "2025-09-29T12:00:00" # Data de exemplo
        mock_run_backtest.return_value = mock_backtest_run

        request_payload = {
            "ticker": "TEST4.SA",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "strategy_type": "sma_cross",
            "strategy_params": {"fast": 10, "slow": 30},
            "initial_cash": 100000,
            "commission": 0.001
        }
        response = test_client.post("/api/v1/backtests/run", json=request_payload)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["ticker"] == "TEST4.SA"
        assert response_data["status"] == "completed"

        mock_run_backtest.assert_called_once()