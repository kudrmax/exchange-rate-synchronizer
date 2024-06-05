from typing import List
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup
from schemas import CurrencyRateUpdate, CountryUpdate
from abc import ABC, abstractmethod


class CurrencyParserBase(ABC):
    """
    Абсрактный класс для парсинга, который обязывает наследников реализовывать метод parse
    """

    def _get_soup(self, url: str, encoding: str | None = None) -> BeautifulSoup:
        response = requests.get(url)
        if encoding is not None:
            response.encoding = encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    @abstractmethod
    def parse(self, *args, **kwargs):
        pass


class RateParser(CurrencyParserBase):
    def __init__(self):
        self.url_template = "https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={cur}&bd={start_day}&bm={start_month}&by={start_year}&ed={end_day}&em={end_month}&ey={end_year}&x=48&y=13#archive"
        # self._get_url_codes()

        # def _get_url_codes(self):
        #     self.currency_codes = {}
        #     url = 'https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur=52148'
        #     soup = self._get_soup(url, encoding='cp1251')
        #     select = soup.find('select', {'class': 'fs11'})
        #     if select:
        #         options = select.find_all('option')
        #         for option in options:
        #             value = option.get('value')
        #             text = option.text
        #             self.currency_codes[text] = value
        #         print(options)

        self.currency_codes_urls = {
            'USD': 52148,  # доллар
            'EUR': 52170,  # евро
            'GBP': 52146,  # фунт стерлигов
            'JPY': 52246,  # японская йена
            'TRY': 52158,  # турецкая лира
            'INR': 52238,  # индийская рупия
            'CNY': 52207,  # китайский юань
        }

    def parse(self, start_date: date, end_date: date, currency_codes: List[str]) -> List[CurrencyRateUpdate]:
        rates = []

        # for curr_code, curr_code_url in self.currency_codes.items():
        for curr_code in currency_codes:
            curr_code_url = self.currency_codes_urls[curr_code]

            url = self.url_template.format(
                cur=curr_code_url,
                start_day=start_date.day, start_month=start_date.month, start_year=start_date.year,
                end_day=end_date.day, end_month=end_date.month, end_year=end_date.year
            )
            soup = self._get_soup(url, encoding='cp1251')

            table = soup.find('table', {'class': 'karramba'})
            if table:
                rows = table.find('tbody').find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:
                        date_text = columns[0].text.strip()
                        rate_text = columns[2].text.strip()
                        try:
                            rate_value = float(rate_text.replace(',', '.'))
                            rate_date = datetime.strptime(date_text, "%d.%m.%Y")
                            rate = CurrencyRateUpdate(currency_code=curr_code, date=rate_date, rate=rate_value)
                            rates.append(rate)
                        except ValueError as ex:
                            print(f"Error parsing row {row}: {ex}")
        return rates


class CountryCurrencyParser(CurrencyParserBase):
    def __init__(self):
        self.url = "https://www.iban.ru/currency-codes"

    def parse(self) -> List[CountryUpdate]:
        country_currencies = []

        soup = self._get_soup(self.url)
        table = soup.find('table', class_='table table-bordered downloads tablesorter')
        if table:
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 4:
                    country = columns[0].text.strip()
                    currency_name = columns[1].text.strip()
                    currency_code = columns[2].text.strip()
                    currency_code = currency_code if currency_code != '' else None
                    country_currency = CountryUpdate(
                        country=country,
                        currency_name=currency_name,
                        currency_code=currency_code,
                    )
                    country_currencies.append(country_currency)
        return country_currencies


if __name__ == '__main__':
    start_date = date(2023, 5, 1)
    end_date = date(2023, 6, 1)

    rate_parser = RateParser()
    country_currency_parser = CountryCurrencyParser()

    rates = rate_parser.parse(start_date=start_date, end_date=end_date)
    country_currency = country_currency_parser.parse()
    print(rates)
    print(country_currency)
