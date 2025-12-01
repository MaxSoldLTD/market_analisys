import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

def get_fundamental_data(tickers):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    periods_lst = [] 
    for y in range(2022,2028):
        for q in range(1,5):
            periods_lst.append(f'{y}Q{q}')
    periods_lst.append('LTM?')
    
    
    final_df = pd.DataFrame(index = periods_lst)

    #Функция для обработки полученного списка в пригодный для анализа вид
    def striping_lst(lst):
        modified = lst[1:-2] + lst[-1:]
        return modified
        
    for ticker in tickers:
        # URL отчёта   
        try:
            url = f'https://smart-lab.ru/q/{ticker}/f/q/MSFO/'
            # Заголовки для запроса
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            
            # Запрос к странице
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print("Ошибка при запросе страницы:", response.status_code)
            
            # Парсинг HTML
            soup = BeautifulSoup(response.text, "html.parser")
            # Поиск строки с годами/кварталами
            header_row = soup.find("tr", {"class": "header_row"})
            
            if not header_row:
                print(f"Не удалось найти заголовок для тикера {ticker}")
                continue
            
            # Извлечение текстовых данных из всех <td> и <th> в строке, игнорируя пустые
            years_and_quarters = [
                cell.get_text(strip=True) 
                for cell in header_row.find_all(["td", "th"]) 
                if cell.get_text(strip=True) and cell.get_text(strip=True) != "LTM"
            ]
        
            # Создание объекта Series
            df_dates = pd.DataFrame(years_and_quarters, columns=["Years and Quarters"])
            df_dates = df_dates.iloc[1:].reset_index().drop('index', axis = 1)
            df_dates['Company'] = f'{ticker}'
            keys_to_dict = list(df_dates["Years and Quarters"])
        
            rows = {}  # Словарь для хранения результатов
            row_values = {}  # Словарь для хранения обработанных значений
            indicators = ['revenue', 'net_operating_income', 'net_income', 'assets',
                          'bank_assets', 'net_debt', 'number_of_shares', 'ebitda', 'roe']
        
            for indicator in indicators:
                row = soup.find("tr", {"field": indicator})
                rows[f"row_{indicator}"] = row  # Сохраняем в словарь
                if row:
                    row_values[f"row_{indicator}_values"] = [td.get_text(strip=True) for td in row.find_all("td")]
                    row_values[f"row_{indicator}_values"] = striping_lst(row_values[f"row_{indicator}_values"])
                else:
                    row_values[f"row_{indicator}_values"] = [''] * 6  # Если данных нет, записываем пустые значения
            
            #Так как Чистый операционных доход это аналог выручки в отчётности банков, то заменяем его на "Выручку"
            if row_values['row_revenue_values'] == ['']*6 and row_values['row_net_operating_income_values'] != ['']*6:
                row_values['row_revenue_values'] = row_values.pop('row_net_operating_income_values')
            else:
                row_values.pop('row_net_operating_income_values')
            #Так как Активы банка это аналог Активов в отчётности банков, то заменяем их на "Активы"
            if row_values['row_assets_values'] == ['']*6 and row_values['row_bank_assets_values'] != ['']*6:
                row_values['row_assets_values'] = row_values.pop('row_bank_assets_values')
            else:
                row_values.pop('row_bank_assets_values')
            
            stocks_df = pd.DataFrame.from_dict(row_values)
            stocks_df.index = keys_to_dict
            stocks_df['ticker'] = f'{ticker}'
            final_df = pd.concat([final_df,stocks_df], axis = 0)
            final_df = final_df.dropna()
        except:
            print(f'Для тикера {ticker} нет фундаментальных данных')

    final_df = final_df.reset_index()
    final_df = final_df.rename(columns = {'index':'period','row_revenue_values':'revenue',
                                          'row_net_income_values':'net_income','row_assets_values':'assets',
                                          'row_net_debt_values':'net_debt','row_number_of_shares_values':'number_of_shares',
                                          'row_ebitda_values':'ebitda','row_roe_values':'roe'})
    final_df = final_df.set_index(['ticker','period'])  #приводим к мультииндексу
    final_df[['revenue','net_income','net_debt','number_of_shares','assets','ebitda','roe']] = final_df[['revenue','net_income','net_debt','number_of_shares','assets','ebitda','roe']].apply(lambda x: x.str.replace(' ',''))
    final_df['roe'] = final_df['roe'].apply(
                                            lambda x: float(x.strip('%')) / 100 
                                            if isinstance(x, str) and x.strip('%').replace('.', '').isdigit() 
                                            else None
                                        )
    final_df[['revenue','net_income','net_debt','number_of_shares','assets','ebitda','roe']] = final_df[['revenue','net_income','net_debt','number_of_shares','assets','ebitda','roe']].apply(pd.to_numeric)
    return final_df