from collections import defaultdict

import pandas as pd
from matplotlib import pyplot as plt
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from models import (
    CurrencyRateModel,
    RelatedCurrencyRateModel,
    ParametersModel,
    CountryModel
)
from schemas import (
    CountryUpdate,
    ParameterUpdate,
    CurrencyRelatedRateCreate,
    CurrencyRelatedRateUpdate
)
from parser import RateParser, CountryCurrencyParser
from create_update import create_object, update_object, get_object


class CurrencyController:
    def __init__(self):
        self.parser = RateParser()
        self.currency_codes = self.parser.currency_codes_urls.keys()

    @staticmethod
    def get_currency_rates(db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        return db.query(CurrencyRateModel).filter(
            CurrencyRateModel.date >= start_date,
            CurrencyRateModel.date <= end_date,
            CurrencyRateModel.currency_code.in_(currency_codes)
        ).all()

    @staticmethod
    def get_related_currency_rates(db: Session, start_date: date, end_date: date):
        return db.query(RelatedCurrencyRateModel).filter(
            RelatedCurrencyRateModel.date >= start_date,
            RelatedCurrencyRateModel.date <= end_date
        ).all()

    def sync_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        rates_to_sync = self.parser.parse(start_date, end_date, currency_codes)

        was_updated_counter = 0
        was_created_counter = 0

        for rate_to_sync in rates_to_sync:
            query = select(CurrencyRateModel).where(CurrencyRateModel.date == rate_to_sync.date).where(
                CurrencyRateModel.currency_code == rate_to_sync.currency_code)
            result = db.execute(query)
            rate: CurrencyRateModel = result.scalar_one_or_none()
            if rate:
                update_object(
                    db=db,
                    model=CurrencyRateModel,
                    obj_id=(rate.currency_code, rate.date),
                    schema=rate_to_sync
                )
                was_updated_counter += 1
            else:
                create_object(
                    db=db,
                    model=CurrencyRateModel,
                    schema=rate_to_sync
                )
                was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_related_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
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
                    update_object(
                        db=db,
                        model=RelatedCurrencyRateModel,
                        obj_id=(currency_code, related_rate.date),
                        schema=CurrencyRelatedRateUpdate(
                            related_rate=related_rate_value
                        )
                    )
                    was_updated_counter += 1
                else:
                    create_object(
                        db=db,
                        model=RelatedCurrencyRateModel,
                        schema=CurrencyRelatedRateCreate(
                            currency_code=currency_code,
                            date=related_rate.date,
                            related_rate=related_rate_value
                        )
                    )
                    was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_base_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        was_created_counter = 0
        was_updated_counter = 0

        base_date = date(2020, 1, 1)
        self.sync_currency_rates(db, start_date, end_date, currency_codes)

        for currency_code in currency_codes:
            query = select(CurrencyRateModel).where(CurrencyRateModel.date == base_date).where(
                CurrencyRateModel.currency_code == currency_code)
            result = db.execute(query)
            currency: CurrencyRateModel = result.scalar_one_or_none()

            param: ParametersModel = db.query(ParametersModel).get(currency_code)
            if param:
                new_parameter = ParameterUpdate(
                    base_rate=currency.rate,
                    date_of_base_rate=base_date,
                )
                update_object(
                    db=db,
                    model=ParametersModel,
                    obj_id=currency_code,
                    schema=new_parameter
                )
                was_updated_counter += 1
            else:
                new_parameter = ParametersModel(
                    currency_code=currency_code,
                    base_rate=currency.rate,
                    date_of_base_rate=base_date,
                )
                create_object(
                    db=db,
                    model=ParametersModel,
                    schema=new_parameter
                )
                was_created_counter += 1
        return was_updated_counter, was_created_counter

    def sync_and_get_currency_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        was_updated_counter, was_created_counter = self.sync_currency_rates(db, start_date, end_date, currency_codes)
        currency_rates = self.get_currency_rates(db, start_date, end_date, currency_codes)
        result = {
            'was_updated': was_updated_counter,
            'was_created': was_created_counter,
            'data': currency_rates
        }
        return result

    def sync_and_get_currency_related_rates(self, db: Session, start_date: date, end_date: date, currency_codes: List[str]):
        was_updated_counter_base, was_created_counter_base = self.sync_base_currency_rates(db, start_date, end_date, currency_codes)
        was_updated_counter_rel, was_created_counter_rel = self.sync_related_currency_rates(db, start_date, end_date, currency_codes)
        currency_rates = self.get_related_currency_rates(db, start_date, end_date)
        result = {
            'was_updated': was_updated_counter_base + was_updated_counter_rel,
            'was_created': was_created_counter_base + was_created_counter_rel,
            'data': currency_rates
        }
        return result


class CountryController:
    def __init__(self):
        self.parser = CountryCurrencyParser()

    @staticmethod
    def get_countries(db: Session):
        return db.query(CountryModel).all()

    @staticmethod
    def sync_counties(db: Session, countries_to_sync: List[CountryUpdate]):
        was_updated_counter = 0
        was_created_counter = 0

        for country_to_sync in countries_to_sync:
            country: CountryModel = db.query(CountryModel).get(country_to_sync.country)
            if country:
                update_object(
                    db=db,
                    model=CountryModel,
                    obj_id=country.country,
                    schema=country_to_sync
                )
                was_updated_counter += 1
            else:
                create_object(
                    db=db,
                    model=CountryModel,
                    schema=country_to_sync
                )
                was_created_counter += 1

        return was_updated_counter, was_created_counter

    def sync_and_get_countries(self, db: Session):
        countries = self.parser.parse()
        was_updated_counter, was_created_counter = self.sync_counties(db, countries_to_sync=countries)
        country_currencies = self.get_countries(db)
        result = {
            'was_updated': was_updated_counter,
            'was_created': was_created_counter,
            'data': country_currencies
        }
        return result


class PlotController:
    @staticmethod
    def draw_plot(related_rates, start_date: date, end_date: date, country_to_currency_code):
        currency_data = {}
        for related_rate in related_rates:
            if related_rate.currency_code not in currency_data:
                currency_data[related_rate.currency_code] = {'data': [], 'countries': []}
            currency_data[related_rate.currency_code]['data'].append([related_rate.date, related_rate.related_rate])
        for country, currency_code in country_to_currency_code.items():
            currency_data[currency_code]['countries'].append(country)

        plt.figure(figsize=(10, 6))
        plt.title('Относительное изменение курсов валют', fontsize=16)
        for currency_code, value in currency_data.items():
            data = value['data']
            countries = value['countries']
            df = pd.DataFrame(data, columns=['date', 'related_rate'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date')
            plt.plot(df['date'], df['related_rate'], label=f'{currency_code} в странах: {", ".join(countries)}')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Относительное изменение курсов валют', fontsize=12)
        plt.grid(alpha=0.4)
        plt.legend(title='Валюты', fontsize=12, title_fontsize=14)
        plt.tight_layout()
        plt.savefig(f'plots/{start_date}-{end_date}-{"-".join(currency_data.keys())}.png')
        plt.close()
