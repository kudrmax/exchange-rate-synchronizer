from typing import List

from pydantic import BaseModel
from datetime import date as date_t


class CurrencyRateSchema(BaseModel):
    currency_code: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    rate: float | None = None  # значение курса валют


class CurrencyRelatedRateSchema(BaseModel):
    currency_code: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    related_rate: float | None = None  # значение курса валют


class CurrencyRelatedRateUpdateSchema(BaseModel):
    related_rate: float | None = None  # значение курса валют


class CountrySchema(BaseModel):
    country: str  # например 'Россия'
    currency_name: str  # например 'Российский рубль'
    currency_code: str | None = None  # например 'RUB'


class ParameterSchema(BaseModel):
    currency_code: str
    base_rate: float | None = None
    date_of_base_rate: date_t | None = None


class ParameterUpdateSchema(BaseModel):
    base_rate: float | None = None
    date_of_base_rate: date_t | None = None


class CurrencyRatesRequestSchema(BaseModel):
    start_date: date_t  # начальная дата
    end_date: date_t  # конечная дата
    currency_codes: List[str]  # список кодов стран (например ['USD', 'EUR', ...]


class PlotRequestSchema(BaseModel):
    start_date: date_t  # начальная дата
    end_date: date_t  # конечная дата
    countries: List[str]  # список стран
