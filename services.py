from typing import List
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup
from schemas import CurrencyRateCreate, CountryCurrencyCreate


def parse_country_currency() -> List[CountryCurrencyCreate]:
    url = "https://www.iban.ru/currency-codes"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    country_currencies = []

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
                currency_number = columns[3].text.strip()
                currency_number = int(currency_number) if currency_number != '' else None
                country_currency = CountryCurrencyCreate(
                    country=country,
                    currency_name=currency_name,
                    currency_code=currency_code,
                    currency_number=currency_number
                )
                country_currencies.append(country_currency)
    return country_currencies


def parse_rates(start_date: date, end_date: date) -> List[CurrencyRateCreate]:
    currs = {
        'USD': 52148,  # доллар
        'EUR': 52170,  # евро
        'GBP': 52146,  # фунт стерлигов
        'JPY': 52246,  # японская йена
        'TRY': 52158,  # турецкая лира
        'INR': 52238,  # индийская рупия
        'CNY': 52207,  # китайский юань
    }

    rates = []

    for curr_name, curr_code in currs.items():

        url_fstring = "https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur={cur}&bd={start_day}&bm={start_month}&by={start_year}&ed={end_day}&em={end_month}&ey={end_year}&x=48&y=13#archive"
        url = url_fstring.format(
            cur=curr_code,
            start_day=start_date.day, start_month=start_date.month, start_year=start_date.year,
            end_day=end_date.day, end_month=end_date.month, end_year=end_date.year
        )
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

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
                        rate = CurrencyRateCreate(currency=curr_name, date=rate_date, rate=rate_value)
                        rates.append(rate)
                        # print(rate_date, rate_value)
                    except ValueError as ex:
                        print(f"Error parsing row {row}: {ex}")
    return rates


if __name__ == '__main__':  # для тестирования парсера
    start_date = date(2023, 5, 1)
    end_date = date(2023, 6, 1)
    rates = parse_rates(start_date=start_date, end_date=end_date)
    country_currency = parse_country_currency()
    # print(rates)
    print(country_currency)
