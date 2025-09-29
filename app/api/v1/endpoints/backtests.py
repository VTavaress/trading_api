from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.modules.backtests import services
from app.core.database import get_db

router = APIRouter()

class BacktestRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    strategy_type: str
    strategy_params: Dict[str, Any] = Field(default_factory=dict)
    initial_cash: float = 100000.0
    commission: float = 0.001

@router.post("/backtests/run", tags=["Backtests"])
def run_backtest_endpoint(request: BacktestRequest, db: Session = Depends(get_db)):
    try:
        backtest_run = services.run_backtest(
            db=db,
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            strategy_type=request.strategy_type,
            strategy_params=request.strategy_params,
            initial_cash=request.initial_cash,
            commission=request.commission
        )
        return {
            "id": backtest_run.id,
            "status": backtest_run.status,
            "ticker": backtest_run.ticker,
            "strategy_type": backtest_run.strategy_type,
            "created_at": backtest_run.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtests", tags=["Backtests"])
def list_backtests_endpoint(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    backtests = services.list_backtests(db=db, skip=skip, limit=limit)
    return backtests

@router.get("/backtests/{backtest_id}/results", tags=["Backtests"])
def get_backtest_results_endpoint(backtest_id: int, db: Session = Depends(get_db)):
    results = services.get_backtest_results(db=db, backtest_id=backtest_id)
    if results is None:
        raise HTTPException(status_code=404, detail="Backtest não encontrado")
    return results
