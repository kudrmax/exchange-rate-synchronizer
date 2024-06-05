from fastapi import FastAPI, Depends, Body
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
            start_date: date = date(2020, 1, 1),
            end_date: date = date(2020, 1, 30),
            currency_codes: List[str] = Body(default=None, example=['USD', 'EUR', 'GBP', 'JPY', 'TRY', 'INR', 'CNY']),
            db: Session = Depends(get_db),
    ):
        if currency_codes is None:
            currency_codes = self.currency_controller.currency_codes
        print(self.currency_controller.currency_codes)
        result = self.currency_controller.sync_and_get_currency_rates(db, start_date, end_date, currency_codes)
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
        self.currency_controller.sync_and_get_currency_related_rates(db, start_date, end_date, currency_codes)

        # получить список related валют за даты
        query = select(RelatedCurrencyRateModel).where(
            RelatedCurrencyRateModel.currency_code.in_(currency_codes)).where(
            RelatedCurrencyRateModel.date >= start_date, RelatedCurrencyRateModel.date <= end_date
        )
        result = db.execute(query)
        related_rates = result.scalars().all()

        self.plot_controller.draw_plot(related_rates, start_date, end_date, country_to_currency_code)

        return related_rates
