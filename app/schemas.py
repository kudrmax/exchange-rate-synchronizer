from typing import List

from pydantic import BaseModel
from datetime import date as date_type


class CurrencyRateSchema(BaseModel):
    currency_code: str  # код валюты (например 'RUB')
    date: date_type  # дата, в которой был данный курс валют
    rate: float | None = None  # значение курса валют


class CurrencyRelatedRateSchema(BaseModel):
    currency_code: str
    date: date_type
    related_rate: float | None = None


class CurrencyRelatedRateUpdateSchema(BaseModel):
    related_rate: float | None = None


class CountrySchema(BaseModel):
    country: str  # страна
    currency_name: str  # название валюты (например 'Российский рубль')
    currency_code: str | None = None  # код валюты (например 'RUB')


class ParameterSchema(BaseModel):
    currency_code: str
    base_rate: float | None = None
    date_of_base_rate: date_type | None = None


class ParameterUpdateSchema(BaseModel):
    base_rate: float | None = None
    date_of_base_rate: date_type | None = None


class CurrencyRatesRequestSchema(BaseModel):
    start_date: date_type
    end_date: date_type
    currency_codes: List[str]  # список кодов стран (например ['USD', 'EUR', ...]


class PlotRequestSchema(BaseModel):
    start_date: date_type
    end_date: date_type
    countries: List[str]  # список стран (например ['Китай', ...]
