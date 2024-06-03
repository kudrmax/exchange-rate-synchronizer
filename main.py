from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import date
# import models
# import crud
from database import engine, get_db
from parser import CountryCurrencyParser, RateParser
import uvicorn

from crud import sync_currency_rates, get_currency_rates, get_rate_by_id
from models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()


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
    parser = RateParser()
    rates = parser.parse(start_date, end_date)
    sync_currency_rates(db, new_rates=rates)
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
    @todo добавить значения по умолчанию для дат
    """
    rates = get_currency_rates(db, start_date, end_date)
    return rates


if __name__ == "__main__":  # запуск приложения
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
