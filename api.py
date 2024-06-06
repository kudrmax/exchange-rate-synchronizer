from fastapi import FastAPI, Depends, Body, Request, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from controllers import CurrencyController, CountryController, PlotController
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models import CountryModel, RelatedCurrencyRateModel

from schemas import CurrencyRatesRequest


class CurrencyAPI:
    def __init__(self):
        self.app = FastAPI()
        self.currency_controller = CurrencyController()
        self.country_controller = CountryController()
        self.plot_controller = PlotController()
        self.setup_routes()
        self.templates = Jinja2Templates(directory="templates")

    def setup_routes(self):
        self.app.get("/", response_class=HTMLResponse)(self.read_root)
        self.app.get("/currency-rates", response_class=HTMLResponse)(self.read_currency_rates)
        self.app.get("/country-currencies", response_class=HTMLResponse)(self.read_country_currencies)


        self.app.post("/sync-and-get-currency-rates/")(self.sync_and_get_currency_rates_endpoint)
        self.app.post("/sync-and-get-currency-related-rates/")(self.sync_and_get_currency_related_rates_endpoint)
        self.app.post("/sync-and-get-countries/")(self.sync_and_get_country_currency_rates_endpoint)
        self.app.post("/draw_plot/")(self.draw_plot)

    def read_root(self, request: Request):
        return self.templates.TemplateResponse("index.html", {"request": request})

    def read_currency_rates(self, request: Request):
        return self.templates.TemplateResponse("currency_rates.html", {"request": request})

    def read_country_currencies(self, request: Request):
        return self.templates.TemplateResponse("country_currencies.html", {"request": request})

    # def sync_and_get_currency_rates_endpoint(
    #         self,
    #         # start_date: date = date(2020, 1, 1),
    #         # end_date: date = date(2020, 1, 30),
    #         # currency_codes: List[str] = Body(default=None, example=['USD', 'EUR', 'GBP', 'JPY', 'TRY', 'INR', 'CNY']),
    #         start_date: date = Query(date(2020, 1, 1)),
    #         end_date: date = Query(date(2020, 1, 30)),
    #         currency_codes: Optional[List[str]] = Query(None),
    #         db: Session = Depends(get_db),
    # ):
    #     if currency_codes is None:
    #         currency_codes = self.currency_controller.currency_codes
    #     result = self.currency_controller.sync_and_get_currency_rates(db, start_date, end_date, currency_codes)
    #     return result

    def sync_and_get_currency_rates_endpoint(
            self,
            request: CurrencyRatesRequest,
            db: Session = Depends(get_db),
    ):
        result = self.currency_controller.sync_and_get_currency_rates(
            db, request.start_date, request.end_date, request.currency_codes)
        return result

    def sync_and_get_currency_related_rates_endpoint(
            self,
            start_date: date = date(2020, 1, 1),
            end_date: date = date(2020, 1, 30),
            currency_codes: List[str] = Body(default=None, example=['USD', 'EUR', 'GBP', 'JPY', 'TRY', 'INR', 'CNY']),
            db: Session = Depends(get_db)
    ):
        if currency_codes is None:
            currency_codes = self.currency_controller.currency_codes
        result = self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date, currency_codes)
        return result

    def sync_and_get_country_currency_rates_endpoint(
            self,
            db: Session = Depends(get_db)
    ):
        result = self.country_controller.sync_and_get_countries(db)
        return result

    def draw_plot(
            self,
            start_date: date = date(2020, 1, 1),
            end_date: date = date(2020, 1, 30),
            countries: List[str] = Body(default=None, example=['Китай', 'Аландские острова', 'Андорра', 'Австрия', 'Бельгия', 'Кипр', 'Эстония',
                         'Европейский Союх', 'Финляндия', 'Франция', 'Гвиана',
                         'Французские Южные и Антарктические территории', 'Германия', 'Греция', 'Гваделупа', 'Ватикан',
                         'Ирландия', 'Италия', 'Латвия', 'Литва', 'Люксембург', 'Мальта', 'Мартиника', 'Майотта',
                         'Монако', 'Черногория', 'Голландия', 'Португалия', 'Реуньон', 'Сен-Бартелеми', 'Сен-Мартин',
                         'Сен-Пьер и Микелон', 'Сан-Марино', 'Словакия', 'Словения', 'Испания', 'Гернси', 'Остров Мен',
                         'Джерси', 'Великобритания', 'Бутан', 'Индия', 'Япония', 'Турция', 'Американское Самоа',
                         'Бонэйр', 'Британские территории в Индийском Океане', 'Эквадор', 'Сальвадор', 'Гуам', 'Гаити',
                         'Маршалловы острова', 'Микронезия', 'Северные Марианские острова', 'Палау', 'Панама',
                         'Пуэрто-Рико', 'Западный Тимор', 'Тёркс и Кайкос', 'Острова США',
                         'Британские Виргинские Острова', 'Виргинские Острова']),
            db: Session = Depends(get_db)
    ):
        if countries is None:
            countries = ['Китай', 'Аландские острова', 'Андорра', 'Австрия', 'Бельгия', 'Кипр', 'Эстония',
                         'Европейский Союх', 'Финляндия', 'Франция', 'Гвиана',
                         'Французские Южные и Антарктические территории', 'Германия', 'Греция', 'Гваделупа', 'Ватикан',
                         'Ирландия', 'Италия', 'Латвия', 'Литва', 'Люксембург', 'Мальта', 'Мартиника', 'Майотта',
                         'Монако', 'Черногория', 'Голландия', 'Португалия', 'Реуньон', 'Сен-Бартелеми', 'Сен-Мартин',
                         'Сен-Пьер и Микелон', 'Сан-Марино', 'Словакия', 'Словения', 'Испания', 'Гернси', 'Остров Мен',
                         'Джерси', 'Великобритания', 'Бутан', 'Индия', 'Япония', 'Турция', 'Американское Самоа',
                         'Бонэйр', 'Британские территории в Индийском Океане', 'Эквадор', 'Сальвадор', 'Гуам', 'Гаити',
                         'Маршалловы острова', 'Микронезия', 'Северные Марианские острова', 'Палау', 'Панама',
                         'Пуэрто-Рико', 'Западный Тимор', 'Тёркс и Кайкос', 'Острова США',
                         'Британские Виргинские Острова', 'Виргинские Острова']
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

        plot_link = self.plot_controller.draw_plot(related_rates, start_date, end_date, country_to_currency_code)

        result = {
            'was_updated': was_updated_counter,
            'was_created': was_created_counter,
            'plot_link': plot_link,
            'data': related_rates,
        }

        return result
