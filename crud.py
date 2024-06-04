import datetime
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import models, schemas
from models import *  # @todo
from schemas import CurrencyRateCreate, CountryCreate

from parser import RateParser


def get_rate_by_code(
        db: Session,
        currency_code: str,
        curr_date: date
) -> Optional[CurrencyRateModel]:
    query = select(CurrencyRateModel).where(CurrencyRateModel.currency_code == currency_code).where(
        CurrencyRateModel.date == curr_date)
    result = db.execute(query)
    rate: CurrencyRateModel = result.scalar_one_or_none()
    return rate


def get_currency_rates(db: Session, start_date: date, end_date: date):
    """
    Функция для получения курсов валют из базы данных за указанный диапазон дат.
    """
    # @todo добавить значения по умолчанию для полчения всех возможных баз данных
    return db.query(models.CurrencyRateModel).filter(
        models.CurrencyRateModel.date >= start_date,
        models.CurrencyRateModel.date <= end_date
    ).all()


def sync_currency_rates(
        db: Session,
        rates_to_sync: List[schemas.CurrencyRateUpdate]
):
    """
    Функция для сохранения курсов валют в базу.
    """
    was_updated_counter = 0
    was_created_counter = 0

    for rate_to_sync in rates_to_sync:
        query = select(CurrencyRateModel).where(CurrencyRateModel.date == rate_to_sync.date).where(
            CurrencyRateModel.currency_code == rate_to_sync.currency_code)
        result = db.execute(query)
        rate: CurrencyRateModel = result.scalar_one_or_none()
        if rate:
            update_currency_rate(db, currency_code=rate.currency_code, curr_date=rate.date, new_rate=rate_to_sync)
            was_updated_counter += 1
        else:
            new_rate = CurrencyRateCreate(**rate_to_sync.model_dump())
            create_currency_rate(db, new_rate=new_rate)
            was_created_counter += 1
    return was_updated_counter, was_created_counter


def update_currency_rate(
        db: Session,
        currency_code: str,
        curr_date: date,
        new_rate: schemas.CurrencyRateUpdate
):
    rate = get_rate_by_code(db=db, currency_code=currency_code, curr_date=curr_date)
    if rate:
        new_rate_dict = new_rate.model_dump(exclude_unset=True)
        for key, val in new_rate_dict.items():
            setattr(rate, key, val)
        db.commit()
        db.refresh(rate)
        return rate


def create_currency_rate(
        db: Session,
        new_rate: CurrencyRateCreate
):
    rate = CurrencyRateModel(**new_rate.model_dump())
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


##################################


def sync_and_get_currency_related_rates(
        db: Session,
        rates_to_sync: List[schemas.CurrencyRateUpdate]
):
    was_updated_counter = 0
    was_created_counter = 0

    for rate_to_sync in rates_to_sync:
        # query = select(RelatedCurrencyRateModel).where(RelatedCurrencyRateModel.date == rate_to_sync.date).where(
        #     RelatedCurrencyRateModel.currency_code == rate_to_sync.currency_code)
        # result = db.execute(query)
        # rate: RelatedCurrencyRateModel = result.scalar_one_or_none()

        # получить базовое значение rate
        # если оно пустое, то синхронизировать

        sync_base_rates(db)

        # получить базовое значение rate
        # получить из пришедшего rate и базового значения related_rate
        # обновить или добавить

        # if rate:
        #     update_currency_rate(db, currency_code=rate.currency_code, curr_date=rate.date, new_rate=rate_to_sync)
        #     was_updated_counter += 1
        # else:
        #     new_rate = CurrencyRateCreate(**rate_to_sync.model_dump())
        #     create_currency_rate(db, new_rate=new_rate)
        #     was_created_counter += 1
        pass
    return was_updated_counter, was_created_counter


def sync_base_rates(db: Session, base_date):


    parser = RateParser()
    rates_to_sync = parser.parse(base_date, base_date)
    sync_currency_rates(db, rates_to_sync=rates_to_sync)
    rates_from_db = get_currency_rates(db, base_date,
                                       base_date)  # @todo сделать так, чтобы get обязательно перед этим делал sync
    print(rates_from_db)


##################################


# def get_country_by_id(
#         db: Session,
#         country_id: int
# ) -> Optional[CountryModel]:
#     query = select(CountryModel).where(CountryModel.id == country_id)
#     result = db.execute(query)
#     rate: CountryModel = result.scalar_one_or_none()
#     return rate


def get_countries(db: Session):
    return db.query(models.CountryModel).all()


def sync_counties(
        db: Session,
        countries_to_sync: List[schemas.CountryUpdate]
):
    """
    Функция для сохранения курсов валют в базу.
    """
    was_updated_counter = 0
    was_created_counter = 0

    for country_to_sync in countries_to_sync:
        country: CountryModel = db.query(models.CountryModel).get(country_to_sync.country)
        if country:  # если такая страна нашлась, то обновляем ее актуальными данными
            country_to_sync_dict = country_to_sync.model_dump(exclude_unset=True)
            for key, val in country_to_sync_dict.items():
                setattr(country, key, val)
            db.commit()
            db.refresh(country)
            was_updated_counter += 1
        else:
            country = CountryModel(**country_to_sync.model_dump())
            db.add(country)
            db.commit()
            db.refresh(country)
            was_created_counter += 1

    return was_updated_counter, was_created_counter

# def update_country(
#         db: Session,
#         country: str,
#         update_country: schemas.CountryUpdate
# ):
#     country = get_country_by_id(db=db, country_id=country_id)
#     if country:
#         new_country_dict = update_country.model_dump(exclude_unset=True)
#         for key, val in new_country_dict.items():
#             setattr(country, key, val)
#         db.commit()
#         db.refresh(country)
#         return country
#
#
# def create_country(
#         db: Session,
#         new_country: CountryCreate
# ):
#     country = CountryModel(**new_country.model_dump())
#     db.add(country)
#     db.commit()
#     db.refresh(country)
#     return country
