from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text('SELECT 1'))
    return {"status": "ok", "postgres_connection": "ok"}
