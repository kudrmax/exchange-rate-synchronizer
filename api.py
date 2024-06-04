from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from controllers import CurrencyController, CountryController


class CurrencyAPI:
    def __init__(self):
        self.app = FastAPI()
        self.currency_controller = CurrencyController()
        self.country_controller = CountryController()
        self.setup_routes()

    def setup_routes(self):
        self.app.post("/sync-and-get-currency-rates/")(self.sync_and_get_currency_rates_endpoint)
        self.app.post("/sync-and-get-currency-related-rates/")(self.sync_and_get_currency_related_rates_endpoint)
        self.app.post("/sync-and-get-countries/")(self.sync_and_get_country_currency_rates_endpoint)

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
