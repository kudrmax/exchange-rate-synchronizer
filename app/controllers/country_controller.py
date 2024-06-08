from typing import List

from sqlalchemy.orm import Session

from .base_controller import BaseController
from models import CountryModel
from parsers import CountryCurrencyParser
from schemas import CountrySchema


class CountryController(BaseController):
    def __init__(self):
        self.parser = CountryCurrencyParser()

    def sync_counties(self, db: Session, countries_to_sync: List[CountrySchema]):
        """
        Синхронизация данных о странах и их валютах с базой данных.

        Parameters
        ----------
        db : Session
            Сессия базы данных.
        countries_to_sync : List[CountrySchema]
            Список схем данных для синхронизации.
        """
        for country_to_sync in countries_to_sync:
            country: CountryModel = db.query(CountryModel).get(country_to_sync.country)
            if country:
                if country.currency_name != country_to_sync.currency_name or country.currency_code != country_to_sync.currency_code:
                    self.update_object(
                        db=db,
                        model=CountryModel,
                        obj_id=country.country,
                        schema=country_to_sync
                    )
            else:
                self.create_object(
                    db=db,
                    model=CountryModel,
                    schema=country_to_sync
                )

    @staticmethod
    def get_countries(db: Session):
        """
        Получение всех стран из базы данных.
        """
        return db.query(CountryModel).all()

    def sync_and_get_countries(self, db: Session):
        """
        Синхронизация и получение данных о странах и их валютах из базы данных.
        """
        countries = self.parser.parse()
        self.sync_counties(db, countries_to_sync=countries)
        country_currencies = self.get_countries(db)
        return country_currencies
