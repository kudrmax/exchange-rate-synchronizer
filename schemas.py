from pydantic import BaseModel
from datetime import date as date_t


class CurrencyRateBase(BaseModel):
    """
    Класс для курсов валют
    """
    currency: str  # название валюты (например 'USD')
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
    currency: str  # название валюты (например 'USD')
    date: date_t  # дата, в которой был данный курс валют
    rate: float | None = None  # значение курса валют


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
    currency_number: int | None = None  # например 643


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
