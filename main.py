from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import date
# import models
# import crud
from database import engine, get_db
from parser import CountryCurrencyParser, RateParser
import uvicorn

from crud import sync_currency_rates, get_currency_rates, sync_counties, get_countries
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
    sync_currency_rates(db, rates_to_sync=rates)
    rates_from_db = get_currency_rates(db, start_date, end_date)
    return rates_from_db


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


@app.post("/sync-countries/")
def get_country_currency_rates_endpoint(
        db: Session = Depends(get_db)
):
    parser = CountryCurrencyParser()
    countries = parser.parse()
    sync_counties(db, countries_to_sync=countries)
    country_currencies = get_countries(db)
    return country_currencies


@app.get("/get-countries/")
def get_countries_endpoint(
        db: Session = Depends(get_db)
):
    countries = get_countries(db)
    return countries


if __name__ == "__main__":  # запуск приложения
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
