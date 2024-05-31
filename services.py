from typing import List
from datetime import date
import requests
from bs4 import BeautifulSoup
from schemas import CurrencyRateCreate


def fetch_currency_rates(start_date: date, end_date: date) -> List[CurrencyRateCreate]:
    """
    Получить курсы валют с внешнего сайта за указанный диапазон дат.
    """
    url_template = "https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur=52170&bd={start_day}&bm={start_month}&by={start_year}&ed={end_day}&em={end_month}&ey={end_year}&x=48&y=13#archive"
    url = url_template.format(
        start_day=start_date.day, start_month=start_date.month, start_year=start_date.year,
        end_day=end_date.day, end_month=end_date.month, end_year=end_date.year
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rates = []
    print(soup)
    # Вставьте здесь ваш код для парсинга HTML и извлечения данных о курсах валют
    # ...

    return rates
