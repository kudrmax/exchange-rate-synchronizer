from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class CurrencyDataModel(Base):
    __tablename__ = "currencies_data"

    id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String, unique=True, nullable=False)
    currency_code = Column(String, unique=True, nullable=True)

    __table_args__ = (
        UniqueConstraint('currency_code', 'currency_name'),
    )

    # def __repr__(self):
    #     return f"<CurrencyData(currency_name={self.currency_name}, currency_code={self.currency_code})>"


class CurrencyRateModel(Base):
    __tablename__ = "currencies_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency_id = Column(Integer, ForeignKey('currencies_data.id'), index=True)
    date = Column(Date, index=True)
    rate = Column(Float)

    # currency = relationship("CurrencyData", back_populates="rates")

    __table_args__ = (
        UniqueConstraint('currency_id', 'date'),
    )

    def __repr__(self):
        return f"<CurrencyRate(currency_id={self.currency_id}, date={self.date}, rate={self.rate})>"


# @todo добавить эту строку в класс, когда я разнесу по файлам
# CurrencyDataModel.rates = relationship("CurrencyRate", order_by=CurrencyRateModel.date, back_populates="currency")


class RelatedCurrencyModel(Base):
    __tablename__ = "related_currencies"

    # id = Column(Integer, primary_key=True, index=True)
    currency_rate_id = Column(Integer, ForeignKey('currencies_rates.id'), primary_key=True, index=True)
    related_rate = Column(Float)


class CountryModel(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, index=True, unique=True)
    currency_id = Column(Integer, ForeignKey('currencies_data.id'), index=True)
