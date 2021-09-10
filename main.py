import time
import requests
import api_credentials
import api_params
from twilio.rest import Client
from constants import *
import PySimpleGUI as sg


def search_for_stock(params):
    response = requests.get(url='https://www.alphavantage.co/query', params=params)
    response.raise_for_status()
    search_data = response.json()["bestMatches"]
    if len(search_data) != 0:
        stock = search_data[0][symbol]
        company_name = search_data[0][name]
        return stock, company_name
    else:
        return None


def get_stock_stats(params):
    stock_response = requests.get(url='https://www.alphavantage.co/query', params=params)
    stock_response.raise_for_status()
    stock_data = dict(stock_response.json()["Time Series (Daily)"])
    keys = list(stock_data.keys())
    cpr = float(stock_data[keys[0]][closing_price])
    cpp = float(stock_data[keys[9]][closing_price])
    percent = (abs(cpp - cpr) / cpp) * 100
    return cpr, cpp, percent, (cpr - cpp > 0)


def get_stock_news(params):
    news_response = requests.get(url="https://finnhub.io/api/v1/company-news", params=params)
    news_response.raise_for_status()
    stock_news_data = news_response.json()
    if len(stock_news_data) != 0:
        return stock_news_data[0]
    else:
        return None


def send_sms(body):
    client = Client(api_credentials.ACC_SID, api_credentials.AUTH_TOKEN)
    msg = client.messages.create(
        to="+918008369511",
        from_=api_credentials.TWILIO_PHONE,
        body=body
    )
    print(msg.status)
    print(msg.body)

def sym_emoji(increased):
    if increased:
        sym = "⬆⬆"
        emoji = '😃'
    else:
        sym = '⬇⬇'
        emoji = '😔'
    return  sym,emoji

def generate_message_body(news, percent_change, increased):
    sym,emoji = sym_emoji(increased)
    if not news:
        return f'''\n
                {api_params.company_name}:  {sym} {percent_change:.2f}%  {emoji}
            '''
    else:
        return f'''\n
            {api_params.company_name}:  {sym} {percent_change:.2f}% {emoji}
            Headline: {news['headline']}
            Brief: {news['summary']}
        '''


layout = [
    [sg.Text(text="Type the name of the company you invested in or want to know about", key='t1')],
    [sg.Input(key='i1')],
    [sg.Text(key='-OUTPUT-', size=(60, 1))],
    [sg.Text(key="msg", size=(60, 2))],
    [sg.Button('Ok')]
]
window = sg.Window('Stock Messenger', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        window.close()
        break
    else:
        if event == 'Ok':
            api_params.keywords = values['i1'].strip()
            search_result = search_for_stock(api_params.search_params())
            if not search_result:
                window['-OUTPUT-'].update(value="Sorry no matches found for the company searched.Please try again!",
                                          text_color='#cc0000')
                window.refresh()
            else:
                api_params.stock, api_params.company_name = search_result
                window['-OUTPUT-'].update(value=f"Match Found: {api_params.company_name}.", text_color='yellow')
                window.refresh()
                close_price_recent, close_price_past, percent_change, increased = get_stock_stats(
                    api_params.stock_api_params())
                stock_news = get_stock_news(params=api_params.stock_news_params())
                msg_body = generate_message_body(news=stock_news, percent_change=percent_change, increased=increased)
                send_sms(body=msg_body)
                sym,emoji = sym_emoji(increased)
                window['msg'].update(
                    value=f"The stock prices changed by {sym} {percent_change:.2f}% {emoji} during the last 10 days.\nA message has been set to the mobile number 8008369511. ")
                window.refresh()
                time.sleep(5)
                break
