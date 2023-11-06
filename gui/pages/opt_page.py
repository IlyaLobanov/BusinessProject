import pandas as pd
import streamlit as st
from helpers.utils import init_page
from helpers.optimization import update_portfolio, portfolio_cost, draw_pie_chart, draw_line_chart
from static import STATIC_PATH
import json
import plotly.express as px
import plotly.graph_objects as go




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


btc_eth_alloc = st.slider("BTC&ETH Allocation (%)", 0, 99, 0)
altcoin_alloc = st.slider("Altcoin Allocation (%)", 0, 100-btc_eth_alloc, 0)
stable_alloc = 100 - btc_eth_alloc - altcoin_alloc

st.write(f'Allocation for stablecoins is: {stable_alloc}%')


initial_balance = 100000
current_balance = 100000

balance_history = []

st.write(f'Initial Balance: {initial_balance}$')

c1, c2 = st.columns(2)

if 'wights' not in st.session_state:
    st.session_state.weights = None

if 'amounts' not in st.session_state:
    st.session_state.amounts = None

if 'balance_history' not in st.session_state:
    st.session_state.balance_history = []

if 'current_day' not in st.session_state:
    st.session_state.current_day = 12 * 24


def dict_to_candle(candle_dict):
    return Candle([candle_dict["start_time"], candle_dict["open_price"], candle_dict["max_price"],
                   candle_dict["min_price"], candle_dict["close_price"], candle_dict["token_volume"],
                   candle_dict["end_time"], candle_dict["quote_volume"], candle_dict["trades_amount"]])

with open(STATIC_PATH / 'full_data.json') as file:
    loaded_data = json.load(file)
    all_data = {token: [dict_to_candle(c) for c in candles] for token, candles in loaded_data.items()}


if st.button('Перейти к следующему дню'):

    if st.session_state.amounts is not None:
        current_balance = portfolio_cost(all_data, st.session_state.current_day, st.session_state.amounts)
    st.session_state.balance_history.append(current_balance)

    st.session_state.weights, st.session_state.amounts = update_portfolio(all_data, st.session_state.current_day, btc_eth_alloc, altcoin_alloc, stable_alloc,current_balance)

    with c1:
        st.write(f'Current balance: {current_balance}')

    with c1:
        sorted_amounts = dict(sorted(st.session_state.amounts.items(), key=lambda item: item[1], reverse=True))
        tokens = sorted_amounts.keys()
        token_amounts = sorted_amounts.values()

        local_df = pd.DataFrame(data={'Amount of tokens': token_amounts}, index=tokens)

        st.dataframe(local_df.head(10))

    with c2:
        threshold = 0.001
        labels = st.session_state.weights.keys()
        values = st.session_state.weights.values()
        labels_new = [label for label, value in zip(labels, values) if value >= threshold]
        values_new = [value for value in values if value >= threshold]

        labels_new.append("Другие")
        values_new.append(sum(value for value in values if value < threshold))

        fig = go.Figure(data=[go.Pie(labels=labels_new, values=values_new, title='Portfolio Distribution')])

        st.plotly_chart(fig)

    balance_df = pd.DataFrame(st.session_state.balance_history)
    st.line_chart(balance_df)

    st.session_state.current_day += 1








