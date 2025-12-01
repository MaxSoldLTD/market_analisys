import pandas as pd
import numpy as np
from get_data.fin_reports import get_fundamental_data
from get_data.prices import get_stock_prices
from datetime import date, timedelta

def calculate_metrics(tickers):
    #Сперва получаем фундаментальные данные по выбранным компаниям
    df = get_fundamental_data(tickers)
    print('Получили фундаментальные данные')
    #Затем получаем данные по значениям котировок акций за последние дни
    today = date.today().strftime("%Y-%m-%d") 
    start_period = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
    price_data = get_stock_prices(tickers,start_period,today,'CLOSE')
    print('Получили цены')
    if price_data.empty :
        empty_letter = 'По выбранным тикерам нет данных'
        return empty_letter
    else:
        price_data = price_data.iloc[0]
        price_data.name = 'current_price'
        price_data = price_data.to_frame()
    
        #Считаем показатели для оценки компании
        metrics = df[df.index != 'LTM?'].groupby('ticker').last()[['revenue','net_debt','number_of_shares','assets','net_income','ebitda','roe']]
        metrics = metrics.merge(price_data, how = 'left', left_index= True, right_index = True)
        #Считаем P/S
        metrics['market_cap'] = metrics['number_of_shares']*metrics['current_price']
        metrics['p/s'] = round(metrics['market_cap']/(metrics['revenue']*1000),2)
        #Считаем p/e
        metrics['p/e'] = round(metrics['market_cap']/(metrics['net_income']*1000),2)
        #Считаем debt/assets
        metrics['debt/assets'] = round(metrics['market_cap']/(metrics['assets']*1000),2)
        #Считаем EV
        metrics['ev'] = metrics['market_cap']+(metrics['net_debt']*1000)
        # #Считаем метрики ev/sales
        metrics['ev/sales'] = round(metrics['ev']/(metrics['revenue']*1000),2)
        #Считаем EV/EBITDA
        metrics['ev/ebitda'] = round(metrics['ev']/(metrics['ebitda']*1000),2)
        #Финал
        metrics.sort_values(by = ['p/s'], ascending = True).head(30)
        print('Закончили расчёты')
        return metrics[['p/s','ev/sales','ev/ebitda','p/e','debt/assets','roe']]