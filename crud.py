from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import models, schemas
from models import CurrencyRate
from schemas import CurrencyRateCreate


def get_rate_by_id(
        db: Session,
        rate_id: int
) -> Optional[CurrencyRate]:
    query = select(CurrencyRate).where(CurrencyRate.id == rate_id)
    result = db.execute(query)
    rate: CurrencyRate = result.scalar_one_or_none()
    return rate


def sync_currency_rates(
        db: Session,
        rates_to_sync: List[schemas.CurrencyRateUpdate]
):
    """
    Функция для сохранения курсов валют в базу.
    """
    for rate_to_sync in rates_to_sync:
        query = select(CurrencyRate).where(CurrencyRate.date == rate_to_sync.date).where(
            CurrencyRate.currency == rate_to_sync.currency)
        result = db.execute(query)
        rate: CurrencyRate = result.scalar_one_or_none()
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
    rate = CurrencyRate(**new_rate.model_dump())
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate


def get_currency_rates(db: Session, start_date: date, end_date: date):
    """
    Функция для получения курсов валют из базы данных за указанный диапазон дат.
    """
    # @todo добавить значения по умолчанию для полчения всех возможных баз данных
    return db.query(models.CurrencyRate).filter(
        models.CurrencyRate.date >= start_date,
        models.CurrencyRate.date <= end_date
    ).all()
