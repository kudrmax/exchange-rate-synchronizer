from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class CurrencyRate(Base):
    """
    SQLAlchemy ORM модель курсов валют.

    Parameters
    --------
    id: int
        Primary key записи курса валют.
    currency : str
        Код валюты (например, 'USD', 'EUR').
    date: datetime.date
        Дата курса валюты.
    rate: float
        Значение курса валюты.
    """
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True)
    date = Column(Date, index=True)
    rate = Column(Float)

    def __repr__(self):
        return f"<CurrencyRate(currency={self.currency}, date={self.date}, rate={self.rate})>"


class CountryModel(Base):
    """
    SQLAlchemy ORM модель @todo.
    """
    __tablename__ = "country_currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, index=True)
    currency_name = Column(String, index=True)
    currency_code = Column(String, index=True)
    currency_number = Column(Integer, index=True)

    def __repr__(self):
        return (f"<CountryModel(country={self.country}, "
                f"currency_name={self.currency_name}, "
                f"currency_code={self.currency_code}, "
                f"currency_number={self.currency_number})>")
