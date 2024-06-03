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


@app.post("/sync-and-get-currency-rates/")
def sync_and_get_currency_rates_endpoint(
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
    # @todo добавить проверку на то, что нельзя выбрать период более двух лет
    # @todo добавить значения по умолчанию для дат
    parser = RateParser()
    rates_to_sync = parser.parse(start_date, end_date)
    was_updated_counter, was_created_counter = sync_currency_rates(db, rates_to_sync=rates_to_sync)
    rates_from_db = get_currency_rates(db, start_date, end_date)
    result = {
        'was_updated': was_updated_counter,
        'was_created': was_created_counter,
        'data': rates_from_db
    }
    return result


@app.post("/sync-and-get-countries/")
def sync_and_get_country_currency_rates_endpoint(
        db: Session = Depends(get_db)
):
    parser = CountryCurrencyParser()
    countries = parser.parse()
    was_updated_counter, was_created_counter = sync_counties(db, countries_to_sync=countries)
    country_currencies = get_countries(db)
    result = {
        'was_updated': was_updated_counter,
        'was_created': was_created_counter,
        'data': country_currencies
    }
    return result


if __name__ == "__main__":  # запуск приложения
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
