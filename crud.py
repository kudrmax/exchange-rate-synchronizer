from datetime import date
from typing import List

from sqlalchemy.orm import Session

import models, schemas


def sync_currency_rates(db: Session, rates: List[schemas.CurrencyRateCreate]):
    """
    Функция для сохранения курсов валют в базу.
    """
    for rate in rates:
        db_rate = models.CurrencyRate(**rate.dict())
        db.add(db_rate)
    db.commit()


def get_currency_rates(db: Session, start_date: date, end_date: date):
    """
    Функция для получения курсов валют из базы данных за указанный диапазон дат.
    """
    # @todo добавить значения по умолчанию для полчения всех возможных баз данных
    return db.query(models.CurrencyRate).filter(
        models.CurrencyRate.date >= start_date,
        models.CurrencyRate.date <= end_date
    ).all()
