from datetime import date
from typing import List

from sqlalchemy.orm import Session

import models, schemas


def sync_currency_rates(db: Session, rates: List[schemas.CurrencyRateCreate]):
    """
    Сохранить курсы валют в базу данных.
    """
    for rate in rates:
        db_rate = models.CurrencyRate(**rate.dict())
        db.add(db_rate)
    db.commit()


def get_currency_rates(db: Session, start_date: date, end_date: date):
    """
    Получить курсы валют из базы данных за указанный диапазон дат.
    """
    return db.query(models.CurrencyRate).filter(
        models.CurrencyRate.date >= start_date,
        models.CurrencyRate.date <= end_date
    ).all()
