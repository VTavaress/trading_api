"""Cria a estrutura inicial de tabelas

Revision ID: 2943187ce80f
Revises: 
Create Date: 2025-09-27 05:59:36.247936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2943187ce80f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    

    op.create_table('backtests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('strategy_type', sa.String(), nullable=False),
    sa.Column('strategy_params_json', sa.JSON(), nullable=True),
    sa.Column('initial_cash', sa.Float(), nullable=False),
    sa.Column('commission', sa.Float(), nullable=False),
    sa.Column('status', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backtests_id'), 'backtests', ['id'], unique=False)
    op.create_table('symbols',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticker', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('exchange', sa.String(), nullable=True),
    sa.Column('currency', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_symbols_id'), 'symbols', ['id'], unique=False)
    op.create_index(op.f('ix_symbols_ticker'), 'symbols', ['ticker'], unique=True)
    op.create_table('daily_positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('backtest_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('position_size', sa.Float(), nullable=True),
    sa.Column('cash', sa.Float(), nullable=True),
    sa.Column('equity', sa.Float(), nullable=True),
    sa.Column('drawdown', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['backtest_id'], ['backtests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_positions_id'), 'daily_positions', ['id'], unique=False)
    op.create_table('metrics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('backtest_id', sa.Integer(), nullable=False),
    sa.Column('total_return', sa.Float(), nullable=True),
    sa.Column('sharpe', sa.Float(), nullable=True),
    sa.Column('max_drawdown', sa.Float(), nullable=True),
    sa.Column('win_rate', sa.Float(), nullable=True),
    sa.Column('avg_trade_return', sa.Float(), nullable=True),
    sa.Column('total_trades', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['backtest_id'], ['backtests.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('backtest_id')
    )
    op.create_index(op.f('ix_metrics_id'), 'metrics', ['id'], unique=False)
    op.create_table('prices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('symbol_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('open', sa.Float(), nullable=False),
    sa.Column('high', sa.Float(), nullable=False),
    sa.Column('low', sa.Float(), nullable=False),
    sa.Column('close', sa.Float(), nullable=False),
    sa.Column('volume', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['symbol_id'], ['symbols.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('symbol_id', 'date', name='_symbol_date_uc')
    )
    op.create_index(op.f('ix_prices_id'), 'prices', ['id'], unique=False)
    op.create_table('trades',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('backtest_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=True),
    sa.Column('side', sa.String(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('size', sa.Float(), nullable=True),
    sa.Column('commission', sa.Float(), nullable=True),
    sa.Column('pnl', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['backtest_id'], ['backtests.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trades_id'), 'trades', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f('ix_trades_id'), table_name='trades')
    op.drop_table('trades')
    op.drop_index(op.f('ix_prices_id'), table_name='prices')
    op.drop_table('prices')
    op.drop_index(op.f('ix_metrics_id'), table_name='metrics')
    op.drop_table('metrics')
    op.drop_index(op.f('ix_daily_positions_id'), table_name='daily_positions')
    op.drop_table('daily_positions')
    op.drop_index(op.f('ix_symbols_ticker'), table_name='symbols')
    op.drop_index(op.f('ix_symbols_id'), table_name='symbols')
    op.drop_table('symbols')
    op.drop_index(op.f('ix_backtests_id'), table_name='backtests')
    op.drop_table('backtests')
