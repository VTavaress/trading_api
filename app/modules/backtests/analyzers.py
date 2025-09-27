import backtrader as bt

class TradeList(bt.Analyzer):
    def __init__(self):
        self.trades = []
        self.cum_pnl = 0.0
        self.open_trade_sizes = {}
    def notify_trade(self, trade):
        if trade.justopened:
            self.open_trade_sizes[trade.ref] = trade.size
        if trade.isclosed:
            self.cum_pnl += trade.pnlcomm
            original_size = self.open_trade_sizes.pop(trade.ref, 0)
            exit_price = 0.0
            if original_size != 0:
                exit_price = round(trade.pnl / original_size + trade.price, 2)
            self.trades.append({
                'ref': trade.ref, 'status': trade.status,
                'direction': 'long' if original_size > 0 else 'short',
                'entry_date': bt.num2date(trade.dtopen).isoformat(),
                'entry_price': round(trade.price, 2),
                'exit_date': bt.num2date(trade.dtclose).isoformat(),
                'exit_price': exit_price, 'size': original_size,
                'pnl': round(trade.pnl, 2), 'pnl_comm': round(trade.pnlcomm, 2),
                'value': round(self.strategy.broker.getvalue(), 2),
                'cumulative_pnl': round(self.cum_pnl, 2),
            })
    def get_analysis(self):
        return self.trades