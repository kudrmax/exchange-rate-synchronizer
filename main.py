from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import models
import schemas
import crud
from database import SessionLocal, engine, get_db
from services import fetch_currency_rates
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/currency-rates/", response_model=List[schemas.CurrencyRateRead])
def get_currency_rates(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    """
    Получить курсы валют за указанный диапазон дат.
    """
    rates = fetch_currency_rates(start_date, end_date)
    # crud.save_currency_rates(db, rates)
    return rates


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
