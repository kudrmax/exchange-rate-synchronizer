from datetime import date
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from .base_controller import BaseController
from models import CurrencyRateModel, RelatedCurrencyRateModel, ParametersModel
from parsers import RateParser
from schemas import CurrencyRelatedRateSchema, ParameterUpdateSchema, ParameterSchema, CurrencyRelatedRateUpdateSchema


class CurrencyController(BaseController):
    def __init__(self):
        self.parser = RateParser()
        self.currency_codes = self.parser.currency_codes_urls.keys()
        self.base_date = date(2020, 1, 1)

    @staticmethod
    def get_currency_rates(db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Получение курсов валют за указанный период времени.
        """
        return db.query(CurrencyRateModel).filter(
            CurrencyRateModel.date >= start_date,
            CurrencyRateModel.date <= end_date,
            CurrencyRateModel.currency_code.in_(currency_codes)
        ).all()

    @staticmethod
    def get_related_currency_rates(db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Получение относительных изменений курсов валют за указанный период времени.
        """
        return db.query(RelatedCurrencyRateModel).filter(
            RelatedCurrencyRateModel.date >= start_date,
            RelatedCurrencyRateModel.date <= end_date,
            RelatedCurrencyRateModel.currency_code.in_(currency_codes)
        ).all()

    def sync_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Метод для синхронизации курсов валют.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        start_date : date
            Начальная дата периода.
        end_date : date
            Конечная дата периода.
        currency_codes : List[str]
            Список кодов валют.
        """
        rates_to_sync = self.parser.parse(start_date, end_date, currency_codes)

        was_updated_counter = 0
        was_created_counter = 0

        for rate_to_sync in rates_to_sync:
            query = select(CurrencyRateModel).where(CurrencyRateModel.date == rate_to_sync.date).where(
                CurrencyRateModel.currency_code == rate_to_sync.currency_code)
            result = db.execute(query)
            rate: CurrencyRateModel = result.scalar_one_or_none()
            if rate:
                if rate.rate != rate_to_sync.rate:
                    self.update_object(
                        db=db,
                        model=CurrencyRateModel,
                        obj_id=(rate.currency_code, rate.date),
                        schema=rate_to_sync
                    )
                    was_updated_counter += 1
            else:
                self.create_object(
                    db=db,
                    model=CurrencyRateModel,
                    schema=rate_to_sync
                )
                was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_related_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Метод для синхронизации относительных изменений курсов валют.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        start_date : date
            Начальная дата периода.
        end_date : date
            Конечная дата периода.
        currency_codes : List[str]
            Список кодов валют.
        """
        was_updated_counter, was_created_counter = 0, 0

        self.sync_currency_rates(db, start_date, end_date, currency_codes)
        related_rates_to_sync = self.get_currency_rates(db, start_date, end_date, currency_codes)

        for related_rate in related_rates_to_sync:
            currency_code = related_rate.currency_code
            param: ParametersModel = db.query(ParametersModel).get(currency_code)
            if param:
                related_rate_value = related_rate.rate / param.base_rate
                query = select(RelatedCurrencyRateModel).where(
                    RelatedCurrencyRateModel.date == related_rate.date).where(
                    RelatedCurrencyRateModel.currency_code == currency_code)
                result = db.execute(query)
                existing_related_rate: RelatedCurrencyRateModel = result.scalar_one_or_none()

                if existing_related_rate:
                    if existing_related_rate.related_rate != related_rate_value:
                        self.update_object(
                            db=db,
                            model=RelatedCurrencyRateModel,
                            obj_id=(currency_code, related_rate.date),
                            schema=CurrencyRelatedRateUpdateSchema(
                                related_rate=related_rate_value
                            )
                        )
                        was_updated_counter += 1
                else:
                    self.create_object(
                        db=db,
                        model=RelatedCurrencyRateModel,
                        schema=CurrencyRelatedRateSchema(
                            currency_code=currency_code,
                            date=related_rate.date,
                            related_rate=related_rate_value
                        )
                    )
                    was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_base_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Метод для синхронизации "базовых" значений курсов валют.
        За "базовое" значение принимается значение курса валюты на момент 2020-01-01 (self.base_date).
        """
        was_created_counter = 0
        was_updated_counter = 0

        self.sync_currency_rates(db, self.base_date, self.base_date, currency_codes)

        for currency_code in currency_codes:
            query = select(CurrencyRateModel).where(CurrencyRateModel.date == self.base_date).where(
                CurrencyRateModel.currency_code == currency_code)
            result = db.execute(query)
            currency: CurrencyRateModel = result.scalar_one_or_none()

            param: ParametersModel = db.query(ParametersModel).get(currency_code)
            if param:
                if param.base_rate != currency.rate:
                    new_parameter = ParameterUpdateSchema(
                        base_rate=currency.rate,
                        date_of_base_rate=self.base_date,
                    )
                    self.update_object(
                        db=db,
                        model=ParametersModel,
                        obj_id=currency_code,
                        schema=new_parameter
                    )
                    was_updated_counter += 1
            else:
                new_parameter = ParameterSchema(
                    currency_code=currency_code,
                    base_rate=currency.rate,
                    date_of_base_rate=self.base_date,
                )
                self.create_object(
                    db=db,
                    model=ParametersModel,
                    schema=new_parameter
                )
                was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_and_get_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        """
        Метод для синхронизации и получения курсов валют.
        """
        was_updated_counter, was_created_counter = self.sync_currency_rates(db, start_date, end_date, currency_codes)
        currency_rates = self.get_currency_rates(db, start_date, end_date, currency_codes)
        result = {
            'was_updated': was_updated_counter,
            'was_created': was_created_counter,
            'data': currency_rates
        }
        return result

    def sync_and_get_currency_related_rates(
            self,
            db: Session,
            start_date: date,
            end_date: date,
            currency_codes: List[str]
    ):
        """
        Метод для синхронизации и получения относительных изменений курсов валют.
        """
        was_updated_counter_base, was_created_counter_base = self.sync_base_currency_rates(
            db,
            start_date,
            end_date,
            currency_codes
        )
        was_updated_counter_rel, was_created_counter_rel = self.sync_related_currency_rates(
            db,
            start_date,
            end_date,
            currency_codes
        )
        currency_rates = self.get_related_currency_rates(
            db,
            start_date,
            end_date,
            currency_codes
        )
        result = {
            'was_updated': was_updated_counter_base + was_updated_counter_rel,
            'was_created': was_created_counter_base + was_created_counter_rel,
            'data': currency_rates
        }
        return result
