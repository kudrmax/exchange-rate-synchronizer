# import datetime
# from datetime import date
# from typing import List, Optional
#
# from sqlalchemy import select
# from sqlalchemy.orm import Session
#
# from schemas import *  # @todo
# from models import *  # @todo
# from schemas import CurrencyRateCreate, CountryCreate
#
# from parser import RateParser
#
# from create_update import create_object, update_object, get_object
#
#
# def get_currency_rates(db: Session, start_date: date, end_date: date):
#     """
#     Функция для получения курсов валют из базы данных за указанный диапазон дат.
#     """
#     # @todo добавить значения по умолчанию для полчения всех возможных баз данных
#     return db.query(CurrencyRateModel).filter(
#         CurrencyRateModel.date >= start_date,
#         CurrencyRateModel.date <= end_date
#     ).all()
#
#
# def get_related_currency_rates(db: Session, start_date: date, end_date: date):
#     """
#     Функция для получения курсов валют из базы данных за указанный диапазон дат.
#     """
#     # @todo добавить значения по умолчанию для полчения всех возможных баз данных
#     return db.query(RelatedCurrencyRateModel).filter(
#         RelatedCurrencyRateModel.date >= start_date,
#         RelatedCurrencyRateModel.date <= end_date
#     ).all()
#
#
# def sync_currency_rates(
#         db: Session,
#         start_date: date,
#         end_date: date,
# ):
#     """
#     Функция для сохранения курсов валют в базу.
#     """
#
#     parser = RateParser()
#     rates_to_sync = parser.parse(start_date, end_date)
#
#     was_updated_counter = 0
#     was_created_counter = 0
#
#     for rate_to_sync in rates_to_sync:
#         query = select(CurrencyRateModel).where(CurrencyRateModel.date == rate_to_sync.date).where(
#             CurrencyRateModel.currency_code == rate_to_sync.currency_code)
#         result = db.execute(query)
#         rate: CurrencyRateModel = result.scalar_one_or_none()
#         if rate:
#             update_object(
#                 db=db,
#                 model=CurrencyRateModel,
#                 obj_id=(rate.currency_code, rate.date),
#                 schema=rate_to_sync
#             )
#             was_updated_counter += 1
#         else:
#             create_object(
#                 db=db,
#                 model=CurrencyRateModel,
#                 schema=rate_to_sync
#             )
#             was_created_counter += 1
#     return was_updated_counter, was_created_counter
#
#
# def sync_related_currency_rates(
#         db: Session,
#         start_date: date,
#         end_date: date,
# ):
#     was_updated_counter, was_created_counter = 0, 0
#
#     # обновление курсов валют
#     sync_currency_rates(db, start_date, end_date)
#     related_rates_to_sync = get_currency_rates(db, start_date, end_date)
#
#     # обновление БД относительных курсов валют
#     for related_rate in related_rates_to_sync:
#         currency_code = related_rate.currency_code
#         param: Parameters = db.query(Parameters).get(currency_code)
#         if param:
#             related_rate_value = related_rate.rate / param.base_rate
#             query = select(RelatedCurrencyRateModel).where(
#                 RelatedCurrencyRateModel.date == related_rate.date).where(
#                 RelatedCurrencyRateModel.currency_code == currency_code)
#             result = db.execute(query)
#             existing_related_rate: RelatedCurrencyRateModel = result.scalar_one_or_none()
#
#             if existing_related_rate:
#                 update_object(
#                     db=db,
#                     model=RelatedCurrencyRateModel,
#                     obj_id=(currency_code, related_rate.date),
#                     schema=CurrencyRelatedRateUpdate(
#                         related_rate=related_rate_value
#                     )
#                 )
#                 was_updated_counter += 1
#             else:
#                 create_object(
#                     db=db,
#                     model=RelatedCurrencyRateModel,
#                     schema=CurrencyRelatedRateCreate(
#                         currency_code=currency_code,
#                         date=related_rate.date,
#                         related_rate=related_rate_value
#                     )
#                 )
#                 was_created_counter += 1
#     return was_updated_counter, was_created_counter
#
#
# def sync_base_currency_rates(
#         db: Session,
#         start_date: date,
#         end_date: date,
# ):
#     was_created_counter = 0
#     was_updated_counter = 0
#
#     base_date = date(2020, 1, 1)  # @todo вынести в config
#     sync_currency_rates(db, start_date, end_date)
#
#     currency_codes = {
#         'USD': 52148,  # доллар
#         'EUR': 52170,  # евро
#         'GBP': 52146,  # фунт стерлигов
#         'JPY': 52246,  # японская йена
#         'TRY': 52158,  # турецкая лира
#         'INR': 52238,  # индийская рупия
#         'CNY': 52207,  # китайский юань
#     }
#
#     for currency_code, _ in currency_codes.items():
#
#         query = select(CurrencyRateModel).where(CurrencyRateModel.date == base_date).where(
#             CurrencyRateModel.currency_code == currency_code)
#         result = db.execute(query)
#         currency: CurrencyRateModel = result.scalar_one_or_none()
#
#         param: Parameters = db.query(Parameters).get(currency_code)
#         if param:
#             new_parameter = ParameterUpdate(
#                 base_rate=currency.rate,
#                 date_of_base_rate=base_date,
#             )
#             update_object(
#                 db=db,
#                 model=Parameters,
#                 obj_id=currency_code,
#                 schema=new_parameter
#             )
#             was_updated_counter += 1
#         else:
#             new_parameter = Parameter(
#                 currency_code=currency_code,
#                 base_rate=currency.rate,
#                 date_of_base_rate=base_date,
#             )
#             create_object(
#                 db=db,
#                 model=Parameters,
#                 schema=new_parameter
#             )
#             was_created_counter += 1
#     return was_updated_counter, was_created_counter
#
#
# def get_countries(db: Session):
#     return db.query(CountryModel).all()
#
#
# def sync_counties(
#         db: Session,
#         countries_to_sync: List[CountryUpdate]
# ):
#     """
#     Функция для сохранения курсов валют в базу.
#     """
#     was_updated_counter = 0
#     was_created_counter = 0
#
#     for country_to_sync in countries_to_sync:
#         country: CountryModel = db.query(CountryModel).get(country_to_sync.country)
#         if country:  # если такая страна нашлась, то обновляем ее актуальными данными
#             update_object(
#                 db=db,
#                 model=CountryModel,
#                 obj_id=country.country,
#                 schema=country_to_sync
#             )
#             was_updated_counter += 1
#         else:
#             create_object(
#                 db=db,
#                 model=CountryModel,
#                 schema=country_to_sync
#             )
#             was_created_counter += 1
#
#     return was_updated_counter, was_created_counter
