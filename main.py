from get_data.tickers import get_tickers_list
from calculate_data.metrics import calculate_metrics

dff = get_tickers_list()


# Если нужен ВТОРОЙ элемент (индекс 1):
# final_tickers = dff[1]
# print(f"Второй тикер: {final_tickers}")