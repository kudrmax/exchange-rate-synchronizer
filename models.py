from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
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


class RelatedCurrencyModel(Base):
    __tablename__ = "related_currencies"

    currency_code = Column(String, primary_key=True, index=True)
    date = Column(Date, primary_key=True, index=True)
    related_rate = Column(Float)

    __table_args__ = (
        UniqueConstraint('currency_code', 'date'),
    )
