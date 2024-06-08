from sqlalchemy import Column, String, Float, Date, UniqueConstraint
from database import Base


class CountryModel(Base):
    """
    Модель для хранения страны и кода ее валюты.
    """
    __tablename__ = "countries"

    country = Column(String, primary_key=True, index=True)
    currency_code = Column(String, index=True)
    currency_name = Column(String)

    def __repr__(self):
        return f"<CountryModel(country={self.country}, currency_code={self.currency_code}, currency_name={self.currency_name})>"


class CurrencyRateModel(Base):
    """
    Модель для хранения значения валюты в определенную дату.
    """
    __tablename__ = "currencies_rates"

    currency_code = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    rate = Column(Float)

    __table_args__ = (
        UniqueConstraint('currency_code', 'date'),
    )

    def __repr__(self):
        return f"<CurrencyRateModel(currency_code={self.currency_code}, date={self.date}, rate={self.rate})>"


class RelatedCurrencyRateModel(Base):
    """
    Модель для хранения относительного изменения значения валюты в определенную дату.
    """
    __tablename__ = "related_currencies_rates"

    currency_code = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    related_rate = Column(Float)

    __table_args__ = (
        UniqueConstraint('currency_code', 'date'),
    )

    def __repr__(self):
        return f"<RelatedCurrencyRateModel(currency_code={self.currency_code}, date={self.date}, related_rate={self.related_rate})>"


class ParametersModel(Base):
    """
    Модель для хранения "базового" значения валюты, относительно которого будет рассчитываться относительное изменение валюты.
    """
    __tablename__ = "parameters"

    currency_code = Column(String, primary_key=True, index=True)
    base_rate = Column(Float)
    date_of_base_rate = Column(Date)

    def __repr__(self):
        return f"<ParametersModel(currency_code={self.currency_code}, base_rate={self.base_rate}, date_of_base_rate={self.date_of_base_rate})>"
