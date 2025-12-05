import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_tickers_list(): #Функция для получения списка котировок, отсортированного по капитализаци
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get('https://smart-lab.ru/q/shares/', headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Получаем данные о капитализации компании
    caps_cells = soup.find_all('td', {'class': 'trades-table__rub'})[1:]
    caps_cells = [cell.get_text(strip=True) for cell in caps_cells]
    caps_cells = list(map(lambda s: float(s.replace(' ', '')), caps_cells)) #очищаем цифры
    stock_tickers = soup.find_all('td', {'class': 'trades-table__ticker'})[1:]
    stock_tickers = [cell.get_text(strip=True) for cell in stock_tickers]
    stocks_caps = list(zip(stock_tickers,caps_cells))
    stocks_caps_sorted = sorted(stocks_caps, key=lambda x: x[1], reverse=True) #оставляем только ТОП 100 компаний по капитализации
    stocks_caps_df = pd.DataFrame(stocks_caps_sorted,columns=['ticker', 'capitalisation'])#Преобразуем в датафрейм
    uniq_tickers = [item[0] for item in stocks_caps_sorted] #Оставляем только уникальные тикеры
    print('Получили нужные тикеры')
    return uniq_tickers