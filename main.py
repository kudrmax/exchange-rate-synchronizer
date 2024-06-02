from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import date
import models
import crud
from database import engine, get_db
from services import parse_rates
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# @app.post("/update-currency-rates/", response_model=List[schemas.CurrencyRateRead])
@app.post("/sync-currency-rates/")
def sync_currency_rates_endpoint(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    """
    API для синхронизации курсов валют за указанный период дат между сайтом и базой данных.

    Parameters
    ----------
    start_date: дата начала периода
    end_date: дата конца периода
    db: сессия

    Returns
    -------
    Лист из объектов типа CurrencyRate (@todo изменить, чтобы был не Create)
    """
    rates = parse_rates(start_date, end_date)
    print(rates)
    crud.sync_currency_rates(db, rates)
    return rates


@app.get("/get-currency-rates/")
def get_currency_rates_endpoint(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    """
    API для получения курсов валют за указанный период дат из базы данных.

    Parameters
    ----------
    start_date: дата начала периода
    end_date: дата конца периода
    db: сессия

    Returns
    -------
    Лист из объектов типа CurrencyRate (@todo изменить, чтобы был не Create)
    """
    rates = crud.get_currency_rates(db, start_date, end_date)
    return rates


if __name__ == "__main__":  # запуск приложения
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
