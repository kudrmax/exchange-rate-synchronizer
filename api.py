from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from controllers import CurrencyController, CountryController, PlotController
from typing import List

from models import CountryModel, RelatedCurrencyRateModel


class CurrencyAPI:
    def __init__(self):
        self.app = FastAPI()
        self.currency_controller = CurrencyController()
        self.country_controller = CountryController()
        self.plot_controller = PlotController()
        self.setup_routes()

    def setup_routes(self):
        self.app.post("/sync-and-get-currency-rates/")(self.sync_and_get_currency_rates_endpoint)
        self.app.post("/sync-and-get-currency-related-rates/")(self.sync_and_get_currency_related_rates_endpoint)
        self.app.post("/sync-and-get-countries/")(self.sync_and_get_country_currency_rates_endpoint)
        self.app.post("/draw_plot/")(self.draw_plot)

    def sync_and_get_currency_rates_endpoint(
            self,
            start_date: date,
            end_date: date,
            db: Session = Depends(get_db)
    ):
        result = self.currency_controller.sync_and_get_currency_rates(db, start_date, end_date)
        return result

    def sync_and_get_currency_related_rates_endpoint(
            self,
            start_date: date,
            end_date: date,
            db: Session = Depends(get_db)
    ):
        result = self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date)
        return result

    def sync_and_get_country_currency_rates_endpoint(
            self,
            db: Session = Depends(get_db)
    ):
        result = self.country_controller.sync_and_get_countries(db)
        return result

    def draw_plot(
            self,
            start_date: date,
            end_date: date,
            countries: List[str],
            db: Session = Depends(get_db)
    ):
        self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date)

        codes = []
        for country in countries:
            query = select(CountryModel).where(CountryModel.country == country)
            country_model: CountryModel = db.execute(query).scalar_one_or_none()
            if country_model:
                codes.append(country_model.currency_code)

        # получить список related валют за даты
        query = select(RelatedCurrencyRateModel).where(RelatedCurrencyRateModel.currency_code.in_(codes)).where(
            RelatedCurrencyRateModel.date >= start_date, RelatedCurrencyRateModel.date <= end_date
        )
        result = db.execute(query)
        related_rates = result.scalars().all()

        self.plot_controller.draw_plot(related_rates, start_date, end_date)

        return related_rates

