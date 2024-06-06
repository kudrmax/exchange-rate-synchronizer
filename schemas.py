from typing import List

from pydantic import BaseModel
from datetime import date as date_t


class CurrencyRateBase(BaseModel):
    """
    Класс для курсов валют
    """
    currency_code: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    rate: float  # значение курса валют


class CurrencyRateCreate(CurrencyRateBase):
    """
    Класс для создания объекта курса валюты
    """
    pass


class CurrencyRateUpdate(CurrencyRateBase):
    """
    Класс для изменения объекта курса валюты
    """
    currency_code: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    rate: float | None = None  # значение курса валют


class CurrencyRelatedRateUpdate(BaseModel):
    """
    Класс для изменения объекта курса валюты
    """
    related_rate: float | None = None  # значение курса валют


class CurrencyRelatedRateCreate(BaseModel):
    """
    Класс для изменения объекта курса валюты
    """
    currency_code: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    related_rate: float | None = None  # значение курса валют


class CurrencyRateRead(CurrencyRateBase):
    """
    Класс для чтения (получения) объекта курса валюты
    """
    id: int


class CountryBase(BaseModel):
    """
    Класс для информации о валютах стран
    """
    country: str  # например 'Россия'
    currency_name: str  # например 'Российский рубль'
    currency_code: str | None = None  # например 'RUB'


class CountryCreate(CountryBase):
    """
    Класс для создания информации о валютах стран
    """
    pass


class CountryUpdate(CountryBase):
    """
    Класс для изменения информации о валютах стран
    """
    country: str  # например 'Россия'
    currency_name: str  # например 'Российский рубль'
    currency_code: str | None = None  # например 'RUB'


class CountryRead(CountryBase):
    """
    Класс для чтения (просмотра) информации о валютах стран
    """
    id: int


class Parameter(BaseModel):
    currency_code: str
    base_rate: float
    date_of_base_rate: date_t


class ParameterUpdate(BaseModel):
    base_rate: float | None = None
    date_of_base_rate: date_t | None = None


class CurrencyRatesRequest(BaseModel):
    start_date: date_t
    end_date: date_t
    currency_codes: List[str]


class PlotRequest(BaseModel):
    start_date: date_t
    end_date: date_t
    countries: List[str]
