from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from models import CurrencyRateModel, RelatedCurrencyRateModel, Parameters
# import crud
from database import engine, get_db
from parser import CountryCurrencyParser, RateParser
import uvicorn

from crud import sync_currency_rates, get_currency_rates, sync_counties, get_countries, \
    sync_and_get_currency_related_rates
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


@app.post("/sync-and-get-currency-related-rates/")
def sync_and_get_currency_related_rates_endpoint(
        start_date: date,
        end_date: date,
        db: Session = Depends(get_db)
):
    base_date = date(2020, 1, 1)

    sync_and_get_currency_rates_endpoint(start_date, end_date, db)
    sync_and_get_currency_rates_endpoint(base_date, base_date, db)

    currency_codes = {
        'USD': 52148,  # доллар
        'EUR': 52170,  # евро
        'GBP': 52146,  # фунт стерлигов
        'JPY': 52246,  # японская йена
        'TRY': 52158,  # турецкая лира
        'INR': 52238,  # индийская рупия
        'CNY': 52207,  # китайский юань
    }


    for currency_code, _ in currency_codes.items():
        query = select(CurrencyRateModel).where(CurrencyRateModel.date == base_date).where(
            CurrencyRateModel.currency_code == currency_code)
        result = db.execute(query)
        currency: CurrencyRateModel = result.scalar_one_or_none()
        if currency:
            param = Parameters(
                currency_code=currency_code,
                base_rate=currency.rate,
                date_of_base_rate=base_date,
            )
            print(param)
            db.add(param)
            db.commit()

    query = select(Parameters).where(True)
    result = db.execute(query)
    temp = list(result.scalars())
    print(*temp)


    # rates_to_sync = get_currency_rates(db, start_date, end_date)
    # base_rates = get_base_rates(db)
    # was_updated_counter_related_rates, was_created_counter_related_rates = sync_and_get_currency_related_rates(db, rates_to_sync=rates_to_sync, base_rates=base_rates)

    # rates_from_db = get_currency_rates(db, start_date, end_date)
    # result = {
    #     'was_updated': was_updated_counter_rates + was_updated_counter_related_rates,
    #     'was_created': was_created_counter_rates + was_created_counter_related_rates,
    #     'data': rates_from_db
    # }
    # return result
    return {}


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
