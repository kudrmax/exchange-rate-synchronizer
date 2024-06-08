from datetime import date
from typing import List

from fastapi import FastAPI, Depends, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from controllers import CurrencyController, CountryController, PlotController
from database import get_db
from models import CountryModel, RelatedCurrencyRateModel
from schemas import CurrencyRatesRequestSchema, PlotRequestSchema


class CurrencyAPI:
    def __init__(self):
        self.app = FastAPI()
        self.currency_controller = CurrencyController()
        self.country_controller = CountryController()
        self.plot_controller = PlotController()
        self.setup_routes()
        self.templates = Jinja2Templates(directory="app/templates")

    def setup_routes(self):
        self.app.get("/", response_class=HTMLResponse)(self.read_root)
        self.app.get("/currency-rates", response_class=HTMLResponse)(self.read_currency_rates)
        self.app.get("/country-currencies", response_class=HTMLResponse)(self.read_country_currencies)
        self.app.get("/currency-changes", response_class=HTMLResponse)(self.read_currency_changes)

        self.app.post("/sync-and-get-currency-rates/")(self.sync_and_get_currency_rates_endpoint)
        self.app.post("/sync-and-get-currency-related-rates/")(self.sync_and_get_currency_related_rates_endpoint)
        self.app.post("/sync-and-get-countries/")(self.sync_and_get_country_currency_rates_endpoint)
        self.app.post("/draw_plot/")(self.draw_plot)

    def read_root(self, request: Request):
        """
        Отображение главной страницы.
        """
        return self.templates.TemplateResponse("index.html", {"request": request})

    def read_currency_rates(self, request: Request):
        """
        Отображение страницы с курсами валют.
        """
        return self.templates.TemplateResponse("currency_rates.html", {"request": request})

    def read_country_currencies(self, request: Request):
        """
        Отображение страницы с валютами стран.
        """
        return self.templates.TemplateResponse("country_currencies.html", {"request": request})

    def read_currency_changes(self, request: Request):
        """
        Отображение страницы с изменением курсов валют.
        """
        return self.templates.TemplateResponse("currency_changes.html", {"request": request})

    def sync_and_get_currency_rates_endpoint(
            self,
            request: CurrencyRatesRequestSchema,
            db: Session = Depends(get_db),
    ):
        """
        Синхронизация и получение курсов валют.

        Parameters
        ----------
        request : CurrencyRatesRequestSchema
            Запрос с данными для получения курсов валют.
        db : Session
            Сессия базы данных.
        """
        result = self.currency_controller.sync_and_get_currency_rates(
            db,
            request.start_date,
            request.end_date,
            request.currency_codes
        )
        return result

    def sync_and_get_currency_related_rates_endpoint(
            self,
            start_date: date = date(2020, 1, 1),
            end_date: date = date(2020, 1, 30),
            currency_codes: List[str] = Body(default=None, example=['USD', 'EUR', 'GBP', 'JPY', 'TRY', 'INR', 'CNY']),
            db: Session = Depends(get_db)
    ):
        """
        Синхронизация и получение связанных курсов валют.

        Parameters
        ----------
        start_date : date
            Начальная дата.
        end_date : date
            Конечная дата.
        currency_codes : List[str]
            Список кодов валют.
        db : Session
            Сессия базы данных.
        """
        if currency_codes is None:
            currency_codes = self.currency_controller.currency_codes
        result = self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date, currency_codes)
        return result

    def sync_and_get_country_currency_rates_endpoint(
            self,
            db: Session = Depends(get_db)
    ):
        """
        Синхронизация и получение валют стран.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        """
        result = self.country_controller.sync_and_get_countries(db)
        return result

    def draw_plot(
            self,
            request: PlotRequestSchema,
            db: Session = Depends(get_db),
    ):
        """
        Построение графика изменения курсов валют.

        Parameters
        ----------
        request : PlotRequestSchema
            Запрос с данными для построения графика.
        db : Session
            Сессия базы данных.
        """
        countries = request.countries
        start_date = request.start_date
        end_date = request.end_date

        # обновить относительные изменения курсов валют
        self.country_controller.sync_and_get_countries(db)

        country_to_currency_code = {}
        for country in countries:
            country_model = db.query(CountryModel).get(country)
            if country_model:
                currency_code = country_model.currency_code
                if currency_code in self.currency_controller.currency_codes:
                    country_to_currency_code[country] = currency_code

        currency_codes = list(set(country_to_currency_code.values()))
        res = self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date, currency_codes)
        was_updated_counter, was_created_counter = res['was_updated'], res['was_created']

        # получить список related валют за даты
        query = select(RelatedCurrencyRateModel).where(
            RelatedCurrencyRateModel.currency_code.in_(currency_codes)).where(
            RelatedCurrencyRateModel.date >= start_date, RelatedCurrencyRateModel.date <= end_date
        )
        result = db.execute(query)
        related_rates = result.scalars().all()

        # построение графика
        plot_link = self.plot_controller.draw_plot(related_rates, start_date, end_date, country_to_currency_code)

        result = {
            'was_updated': was_updated_counter,
            'was_created': was_created_counter,
            'plot_link': plot_link,
            'data': related_rates,
        }

        return result
