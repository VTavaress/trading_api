import pandas as pd
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.modules.backtests import services
from app.core.models.backtest_results import Backtest

def test_run_backtest_service_logic(db_session):
    
    
    fake_data = {
        'date': [datetime(2023, 1, 2).date()],
        'open': [10.0], 'high': [10.5], 'low': [9.5], 
        'close': [10.2], 'volume': [1000]
    }
    fake_dataframe = pd.DataFrame(fake_data)

    with patch('app.modules.backtests.services.pd.read_sql') as mock_read_sql, \
         patch('app.modules.backtests.services.bt.Cerebro') as mock_cerebro_class:
        
        # Configuramos os mocks para retornar valores padrão
        mock_read_sql.return_value = fake_dataframe
        mock_cerebro_instance = MagicMock()
        
        # Simulamos os resultados dos analisadores
        mock_analyzers = {
            'sharpe_ratio': MagicMock(),
            'drawdown': MagicMock(),
            'trade_analyzer': MagicMock(),
            'trade_list': MagicMock()
        }
        mock_analyzers['trade_analyzer'].get_analysis.return_value = {'total': {'total': 0}, 'won': {'total': 0}, 'lost': {'total': 0}, 'pnl': {'net': {'average': 0}}}
        mock_analyzers['drawdown'].get_analysis.return_value = {'max': {'drawdown': 0}}
        mock_analyzers['sharpe_ratio'].get_analysis.return_value = {'sharperatio': 0}
        mock_analyzers['trade_list'].get_analysis.return_value = []

        mock_strategy = MagicMock()
        mock_strategy.analyzers.trade_analyzer = mock_analyzers['trade_analyzer']
        mock_strategy.analyzers.drawdown = mock_analyzers['drawdown']
        mock_strategy.analyzers.sharpe_ratio = mock_analyzers['sharpe_ratio']
        mock_strategy.analyzers.trade_list = mock_analyzers['trade_list']

        mock_cerebro_instance.run.return_value = [mock_strategy]
        mock_cerebro_class.return_value = mock_cerebro_instance

        # 3. Executamos o serviço diretamente
        backtest_run = services.run_backtest(
            ticker="TEST.SA",
            start_date="2023-01-01",
            end_date="2023-01-03",
            strategy_type="sma_cross",
            strategy_params={},
            initial_cash=100000,
            commission=0.001,
            db=db_session
        )

        # 4. Verificamos se um registo de backtest foi criado e finalizado
        assert isinstance(backtest_run, Backtest)
        assert backtest_run.status == "completed"
        assert backtest_run.ticker == "TEST.SA"

        # 5. Verificamos se as funções principais foram chamadas
        mock_read_sql.assert_called_once()
        mock_cerebro_instance.adddata.assert_called_once()
        mock_cerebro_instance.addstrategy.assert_called_once()
        mock_cerebro_instance.run.assert_called_once()