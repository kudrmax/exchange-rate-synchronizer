from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import models, schemas
from models import *  # @todo
from schemas import CurrencyRateCreate, CountryCreate


def get_rate_by_id(
        db: Session,
        rate_id: int
) -> Optional[CurrencyRateModel]:
    query = select(CurrencyRateModel).where(CurrencyRateModel.id == rate_id)
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
    for rate_to_sync in rates_to_sync:
        query = select(CurrencyRateModel).where(CurrencyRateModel.date == rate_to_sync.date).where(
            CurrencyRateModel.currency == rate_to_sync.currency)
        result = db.execute(query)
        rate: CurrencyRateModel = result.scalar_one_or_none()
        if rate:
            update_currency_rate(db, rate_id=rate.id, new_rate=rate_to_sync)
        else:
            new_rate = CurrencyRateCreate(**rate_to_sync.model_dump())
            create_currency_rate(db, new_rate=new_rate)


def update_currency_rate(
        db: Session,
        rate_id: int,
        new_rate: schemas.CurrencyRateUpdate
):
    rate = get_rate_by_id(db=db, rate_id=rate_id)
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


def get_country_by_id(
        db: Session,
        country_id: int
) -> Optional[CountryModel]:
    query = select(CountryModel).where(CountryModel.id == country_id)
    result = db.execute(query)
    rate: CountryModel = result.scalar_one_or_none()
    return rate


def get_countries(db: Session):
    return db.query(models.CountryModel).all()


from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from models import CountryModel, CurrencyDataModel
from schemas import CountryUpdate
from typing import List


def sync_counties(db: Session, countries_to_sync: List[CountryUpdate]):
    """
    Синхронизировать данные о странах и валютах в базе данных.

    Parameters
    ----------
    db : Session
        Сессия базы данных.
    countries_to_sync : List[CountryUpdate]
        Список данных для обновления о странах и валютах.
    """
    currency_data_updates = []
    country_data_updates = []

    for update in countries_to_sync:
        currency_data_updates.append({
            "currency_name": update.currency_name,
            "currency_code": update.currency_code
        })

    # обновляем БД currencies_data используя данные, которые мы получили в country_updates
    # если такая запись уже была, актуализируем ее новыми данными
    # если такой записи еще нет, то добавляем новую
    insert_stmt = insert(CurrencyDataModel).values(currency_data_updates)
    update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['currency_name'],  # Обрабатываем конфликт по currency_name
        set_={
            "currency_code": insert_stmt.excluded.currency_code
        }
    )
    db.execute(update_stmt)
    db.commit()

    insert_stmt = insert(CurrencyDataModel).values(currency_data_updates)
    update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['currency_code'],  # Обрабатываем конфликт по currency_code
        set_={
            "currency_name": insert_stmt.excluded.currency_name
        }
    )
    db.execute(update_stmt)
    db.commit()

    # получим id в таблице CurrencyDataModel для всех country в country_updates
    currency_name_to_id = {
        obj.currency_name: obj.id for obj in db.query(CurrencyDataModel).all()
    }

    for update in countries_to_sync:
        country_data_updates.append({
            "country": update.country,
            "currency_id": currency_name_to_id[update.currency_name]
        })

    # массовая вставка в БД CountryModel аналогично массовой вставке выше
    insert_stmt = insert(CountryModel).values(country_data_updates)
    update_stmt = insert_stmt.on_conflict_do_update(
        index_elements=['country'],
        set_={
            "currency_id": insert_stmt.excluded.currency_id
        }
    )
    db.execute(update_stmt)
    db.commit()


def update_country(
        db: Session,
        country_id: int,
        update_country: schemas.CountryUpdate
):
    country = get_country_by_id(db=db, country_id=country_id)
    if country:
        new_country_dict = update_country.model_dump(exclude_unset=True)
        for key, val in new_country_dict.items():
            setattr(country, key, val)
        db.commit()
        db.refresh(country)
        return country


def create_country(
        db: Session,
        new_country: CountryCreate
):
    country = CountryModel(**new_country.model_dump())
    db.add(country)
    db.commit()
    db.refresh(country)
    return country
