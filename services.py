from typing import List
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup
from schemas import CurrencyRateCreate


def parse_rates(start_date: date, end_date: date) -> List[CurrencyRateCreate]:
    url_fstring = "https://www.finmarket.ru/currency/rates/?id=10148&pv=1&cur=52170&bd={start_day}&bm={start_month}&by={start_year}&ed={end_day}&em={end_month}&ey={end_year}&x=48&y=13#archive"
    url = url_fstring.format(
        start_day=start_date.day, start_month=start_date.month, start_year=start_date.year,
        end_day=end_date.day, end_month=end_date.month, end_year=end_date.year
    )
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    rates = []
    table = soup.find('table', {'class': 'karramba'})
    if table:
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 3:  # @todo
                date_text = columns[0].text.strip()
                rate_text = columns[2].text.strip()
                try:
                    rate_value = float(rate_text.replace(',', '.'))
                    rate_date = datetime.strptime(date_text, "%d.%m.%Y")
                    rate = CurrencyRateCreate(currency='USD', date=rate_date, rate=rate_value)
                    rates.append(rate)
                    print(rate_date, rate_value)
                except ValueError as ex:
                    print(f"Error parsing row {row}: {ex}")
    return rates


if __name__ == '__main__':
    start_date = date(2023, 5, 1)
    end_date = date(2023, 6, 1)

    res = parse_rates(start_date=start_date, end_date=end_date)
    print(res)
