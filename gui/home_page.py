import streamlit as st
from helpers.utils import init_page


import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
from candle import Candle
from static import STATIC_PATH

def dict_to_candle(candle_dict):
    return Candle([candle_dict["start_time"], candle_dict["open_price"], candle_dict["max_price"], 
                   candle_dict["min_price"], candle_dict["close_price"], candle_dict["token_volume"], 
                   candle_dict["end_time"], candle_dict["quote_volume"], candle_dict["trades_amount"]])

with open(STATIC_PATH / 'full_data.json') as file:
    loaded_data = json.load(file)
    data_dict = {token: [dict_to_candle(c) for c in candles] for token, candles in loaded_data.items()}

tokens = list(data_dict.keys())


def plot_candlestick(data):
    fig = go.Figure(data=[go.Candlestick(x=[candle.start_time for candle in data],
                open=[candle.open_price for candle in data],
                high=[candle.max_price for candle in data],
                low=[candle.min_price for candle in data],
                close=[candle.close_price for candle in data])])
    st.plotly_chart(fig)

st.title("Token Candlestick Chart")
search_term = st.text_input("Search for a token:")


filtered_tokens = [token for token in tokens if search_term.lower() in token.lower()]


selected_token = st.selectbox("Select a token:", filtered_tokens)


start_date = st.date_input("Start date",value = pd.to_datetime('2023-04-01'), min_value=pd.to_datetime('2023-04-01'), max_value=pd.to_datetime('2023-10-30'))
end_date = st.date_input("End date",value = pd.to_datetime('2023-04-10'), min_value=pd.to_datetime('2023-04-01'), max_value=pd.to_datetime('2023-10-30'))


filtered_data = [candle for candle in data_dict[selected_token] if start_date <= pd.to_datetime(candle.start_time, unit='ms').date() <= end_date]

plot_candlestick(filtered_data)


