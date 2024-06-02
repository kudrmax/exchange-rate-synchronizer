from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

import models, schemas
from models import CurrencyRate


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
        new_rates: List[schemas.CurrencyRateUpdate]
):
    """
    Функция для сохранения курсов валют в базу.
    """
    for new_rate in new_rates:
        rate = get_rate_by_id(db=db, rate_id=new_rate.id)
        if rate:
            new_rate_dict = new_rate.model_dump(exclude_unset=True)
            for key, val in new_rate_dict.items():
                setattr(rate, key, val)
            db.commit()
            db.refresh(rate)


def get_currency_rates(db: Session, start_date: date, end_date: date):
    """
    Функция для получения курсов валют из базы данных за указанный диапазон дат.
    """
    # @todo добавить значения по умолчанию для полчения всех возможных баз данных
    return db.query(models.CurrencyRate).filter(
        models.CurrencyRate.date >= start_date,
        models.CurrencyRate.date <= end_date
    ).all()
