from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.data import services
from pydantic import BaseModel

router = APIRouter()

class FetchRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

@router.post("/data/fetch", tags=["Data Management"])
def fetch_data(request: FetchRequest, db: Session = Depends(get_db)):
    try:
        count = services.fetch_and_store_ohlcv(
            ticker=request.ticker,
            start_date=request.start_date,
            end_date=request.end_date,
            db=db
        )
        return {"message": f"Dados para {request.ticker} processados. {count} novos registros adicionados."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
