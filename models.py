from sqlalchemy import Column, Integer, String, Float, Date
from database import Base


class CurrencyRate(Base):
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True)
    date = Column(Date, index=True)
    rate = Column(Float)

    def __repr__(self):
        return f"<CurrencyRate(currency={self.currency}, date={self.date}, rate={self.rate})>"
