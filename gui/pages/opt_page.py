import streamlit as st
from helpers.utils import init_page
from helpers.optimization import next_day_update
from static import STATIC_PATH
import json




class Candle():

    def __init__(self, arr: list):
        self.start_time: int = arr[0]
        self.open_price: float = float(arr[1])
        self.max_price: float = float(arr[2])
        self.min_price: float = float(arr[3])
        self.close_price: float = float(arr[4])
        self.token_volume: float = float(arr[5])
        self.quote_volume: float = float(arr[7])
        self.end_time: int = arr[6]
        self.trades_amount: int = arr[8]

    def __repr__(self):
        return f'quote_volume: {self.quote_volume}'
    
    def price_change_percent(self):
        return (self.close_price / self.open_price - 1) * 100

def make_candle(arr: list):
    return Candle(arr)

st.title("Portfolio Optimization")


btc_eth_alloc = st.slider("BTC&ETH Allocation (%)", 0, 100, 50)
altcoin_alloc = st.slider("Altcoin Allocation (%)", 0, 100-btc_eth_alloc*100, 25)
stable_alloc = 100 - btc_eth_alloc - altcoin_alloc

current_day = 7 * 24

def dict_to_candle(candle_dict):
    return Candle([candle_dict["start_time"], candle_dict["open_price"], candle_dict["max_price"], 
                   candle_dict["min_price"], candle_dict["close_price"], candle_dict["token_volume"], 
                   candle_dict["end_time"], candle_dict["quote_volume"], candle_dict["trades_amount"]])

with open(STATIC_PATH / 'full_data.json') as file:
    loaded_data = json.load(file)
    all_data = {token: [dict_to_candle(c) for c in candles] for token, candles in loaded_data.items()}


if st.button('Перейти к следующему дню'):
    updated_weights = next_day_update(all_data, current_day)
    
    
    
    current_day += 24




