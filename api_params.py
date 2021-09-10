from api_credentials import *
from constants import *
stock = None
company_name = None
keywords = None


def stock_api_params():
    stock_api_parameters = {
        "apikey": STOCK_API_KEY,
        "function": 'TIME_SERIES_DAILY',
        "symbol": stock,
    }
    return stock_api_parameters


def stock_news_params():
    stock_news_parameters = {
        "token":NEWS_API_KEY,
        "symbol":stock,
        "from": from_date,
        "to":to_date
    }
    return stock_news_parameters


def search_params():
    search_parameters = {
        "apikey": STOCK_API_KEY,
        "function": 'SYMBOL_SEARCH',
        "keywords": keywords
    }
    return search_parameters
