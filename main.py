from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from models import CurrencyRateModel, RelatedCurrencyRateModel, Parameters
# import crud
from database import engine, get_db
from parser import CountryCurrencyParser, RateParser
import uvicorn

from crud import *
from models import Base

from create_update import create_object, update_object, get_object

from schemas import *

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/sync-and-get-currency-rates/")
def sync_and_get_currency_rates_endpoint(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    # @todo добавить проверку на то, что нельзя выбрать период более двух лет
    # @todo добавить значения по умолчанию для дат
    was_updated_counter, was_created_counter = sync_currency_rates(db, start_date, end_date)
    currency_rates = get_currency_rates(db, start_date, end_date)
    result = {
        'was_updated': was_updated_counter,
        'was_created': was_created_counter,
        'data': currency_rates
    }
    return result


@app.post("/sync-and-get-currency-related-rates/")
def sync_and_get_currency_related_rates_endpoint(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    was_updated_counter_base, was_created_counter_base = sync_base_currency_rates(db, start_date, end_date)
    was_updated_counter_rel, was_created_counter_rel = sync_related_currency_rates(db, start_date, end_date)
    currency_rates = get_related_currency_rates(db, start_date, end_date)
    result = {
        'was_updated': was_updated_counter_base + was_updated_counter_rel,
        'was_created': was_created_counter_base + was_created_counter_rel,
        'data': currency_rates
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
