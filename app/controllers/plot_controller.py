import os
import re
from datetime import date, datetime

import pandas as pd
from matplotlib import pyplot as plt

from .base_controller import BaseController


class PlotController(BaseController):
    def __init__(self):
        self.plot_dir = 'app/static/plots/'

    def draw_plot(self, related_rates, start_date: date, end_date: date, country_to_currency_code):
        """
        Построение графика изменения курсов валют за заданный период времени.
        """
        currency_data = {}
        for related_rate in related_rates:
            if related_rate.currency_code not in currency_data:
                currency_data[related_rate.currency_code] = {'data': [], 'countries': []}
            currency_data[related_rate.currency_code]['data'].append([related_rate.date, related_rate.related_rate])
        for country, currency_code in country_to_currency_code.items():
            currency_data[currency_code]['countries'].append(country)

        plt.figure(figsize=(10, 6))
        # plt.title('Относительное изменение курсов валют', fontsize=16)
        for currency_code, value in currency_data.items():
            data = value['data']
            countries = value['countries']
            df = pd.DataFrame(data, columns=['date', 'related_rate'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values(by='date')
            counties_label = ", ".join(countries)
            counties_label = counties_label[:50 - 3] + '...' if len(counties_label) > 50 else counties_label
            plt.plot(df['date'], df['related_rate'], label=f'{currency_code} в странах: {counties_label}')
            # plt.plot(df['date'], df['related_rate'], label=f'{currency_code}')
        plt.xlabel('Дата', fontsize=12)
        plt.ylabel('Относительное изменение курсов валют', fontsize=12)
        plt.grid(alpha=0.4)
        # plt.legend(title='Валюты', fontsize=10, title_fontsize=12, loc='lower right')
        plt.legend(fontsize=10, title_fontsize=12, loc='lower right')
        plt.tight_layout()
        # plot_link = f'{start_date}-{end_date}-{"-".join(currency_data.keys())}.png'
        plot_link = f'{datetime.now().strftime("%Y%m%d-%H%M%S")}.png'
        plt.savefig(self.plot_dir + plot_link)
        plt.close()

        # если в директории более 10 файлов с графиками, то удалить самый старый
        # не самое элегантное решение, но пойдет как временный костыль
        pattern = re.compile(r'\d{8}-\d{6}\.png')
        files = [f for f in os.listdir(self.plot_dir) if os.path.isfile(os.path.join(self.plot_dir, f))]
        plot_files = [f for f in files if pattern.match(f)]
        max_files = 10
        if len(plot_files) > max_files:
            plot_files.sort(key=lambda x: os.path.getctime(os.path.join(self.plot_dir, x)))
            files_to_delete = plot_files[:-max_files]
            for file in files_to_delete:
                os.remove(os.path.join(self.plot_dir, file))
                print(f"Deleted plot image: {file}")

        return plot_link
