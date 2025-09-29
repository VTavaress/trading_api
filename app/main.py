from fastapi import FastAPI 
from app.api.v1.endpoints import health, data, backtests


app = FastAPI(
    title="Trading Algorithm API",
    description="API para backtesting de estratégias de trading.",
    version="0.1.0"
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(data.router, prefix="/api/v1")
app.include_router(backtests.router, prefix="/api/v1") 

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API de Trading Algorítmico!"}