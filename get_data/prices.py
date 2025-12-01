import pandas as pd
import requests
import apimoex
from datetime import datetime



def get_stock_prices(stock_lst,start_date,end_date,indicator):

    #Задаём пустой список, куда будем размещать индекс Мосбиржи, чтобы прогнать его отдельным методом
    indexes = []
    print('Начинаем выгружать цены')
    #Отдельно выносим из общего списка индекс Мосбиржи, если его указали в списке

    for i in stock_lst:
        try:
            if i == 'IMOEX':
                indexes.append(i)
                stock_lst.remove(i)
            else:
                pass
        except:
            print(f'Для тикера {i} не найдены цены')


    dataframe = pd.DataFrame()

    with requests.Session() as session:
        #Получаем данные по историческим ценам акций
        try:
            for t in stock_lst:
                prices = apimoex.get_board_history(session,t)
                prices = pd.DataFrame(prices)
                prices.set_index('TRADEDATE', inplace=True)
                prices = prices[indicator]
                prices = prices.rename(t)
                dataframe = pd.concat([dataframe,prices], axis = 1)
        except:
            pass
        #Получаем данные по историческим ценам индекса, если такой тикер указан
        try:
            for i in indexes:
                prices = apimoex.get_board_history(session,i,engine='stock',market='index',board = 'SNDX')
                prices = pd.DataFrame(prices)
                prices.set_index('TRADEDATE', inplace=True)
                prices = prices[indicator]
                prices = prices.rename(i)
                dataframe = pd.concat([dataframe,prices], axis = 1)
        except:
            pass

    dataframe.index.name = 'Date'
    dataframe = dataframe.sort_index(ascending=False)
    dataframe = dataframe.loc[(dataframe.index >= start_date) & (dataframe.index <= end_date)]
    dataframe = dataframe.dropna(axis=1, how='all')
    print('Все цены выгрузили')
    return dataframe