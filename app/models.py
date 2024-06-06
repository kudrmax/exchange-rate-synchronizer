from sqlalchemy import Column, String, Float, Date, UniqueConstraint
from database import Base


class CountryModel(Base):
    __tablename__ = "countries"

    country = Column(String, primary_key=True, index=True)
    currency_code = Column(String, index=True)
    currency_name = Column(String)


class CurrencyRateModel(Base):
    __tablename__ = "currencies_rates"

    currency_code = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    rate = Column(Float)

    __table_args__ = (
        UniqueConstraint('currency_code', 'date'),
    )


class RelatedCurrencyRateModel(Base):
    __tablename__ = "related_currencies_rates"

    currency_code = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    related_rate = Column(Float)

    __table_args__ = (
        UniqueConstraint('currency_code', 'date'),
    )


class ParametersModel(Base):
    __tablename__ = "parameters"

    currency_code = Column(String, primary_key=True, index=True)
    base_rate = Column(Float)
    date_of_base_rate = Column(Date)

    def __repr__(self):
        return f'{self.currency_code = }, {self.base_rate = }, {self.date_of_base_rate = }'
