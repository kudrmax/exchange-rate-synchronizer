from pydantic import BaseModel
from datetime import date


class CurrencyRateBase(BaseModel):
    currency: str  # название валюты (например 'USD')
    date: date  # дата, в которой был данный курс валют
    rate: float  # значение курса валют


class CurrencyRateCreate(CurrencyRateBase):
    """
    Класс для создания объекта курса валюты
    """
    pass


class CurrencyRateRead(CurrencyRateBase):
    """
    Класс для чтения (получения) объекта курса валюты
    """
    id: int