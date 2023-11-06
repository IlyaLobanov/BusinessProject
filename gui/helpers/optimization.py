import cvxpy as cp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def optimize_portfolio(all_data, returns, big_weight, alt_weight, cash_weight, current_day_index, current_balance, big_tokens=["BTC", "ETH"],
                       cash_tokens=["USDC"]):


    btc_index = list(returns.columns).index('BTCUSDT')
    eth_index = list(returns.columns).index('ETHUSDT')

    stable_index = list(returns.columns).index('USDCUSDT')

    n = returns.shape[1]
    mu = returns.mean().values
    Sigma = returns.cov().values

    w = cp.Variable(n)
    gamma = cp.Parameter(nonneg=True)
    ret = mu.T @ w

    risk = cp.quad_form(w, Sigma)
    objective = cp.Maximize(ret - gamma * risk)

    constraints = [w >= 0, cp.sum(w) == 1]

    big_total = cp.sum(w[[btc_index, eth_index]])
    cash_total = cp.sum(w[stable_index])

    constraints.extend([
        big_total == big_weight / 100,
        cash_total == cash_weight / 100
    ])

    for token in list(returns.columns):
        if (token != 'BTCUSDT') & (token != 'ETHUSDT') &(token != 'USDCUSDT'):
            local_index = list(returns.columns).index(token)
            constraints.extend([w[local_index] <= 0.05])

    prob = cp.Problem(objective, constraints)
    gamma.value = 0.4
    prob.solve(solver=cp.ECOS)

    weights = dict(zip(returns.columns, w.value))

    amounts = {}

    for token in weights.keys():
        local_money = current_balance * weights[token]
        amounts[token] = local_money / all_data[token][current_day_index].close_price


    return weights, amounts

def portfolio_cost(data: dict, current_day_index: int, amounts: dict) -> float:
    cost = 0
    for token, candles in data.items():
        last_price = candles[current_day_index: current_day_index + 24][-1].close_price
        token_amount = amounts[token]
        cost += last_price * token_amount

    return cost


def compute_returns(data, start_day=0, days=7):
    all_returns = {}

    for token, candles in data.items():
        prices = [candle.close_price for candle in candles[start_day - days * 24:start_day + 1]]
        returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))]
        all_returns[token] = returns

    return pd.DataFrame(all_returns)


def update_portfolio(data, current_day_index, big_weight, alt_weight, cash_weight, current_balance):
    next_day_returns = compute_returns(data, start_day=current_day_index, days=5)
    new_weights, amounts = optimize_portfolio(data, next_day_returns, big_weight, alt_weight, cash_weight, current_day_index, current_balance)
    return new_weights, amounts

def draw_pie_chart(data_dict):

    fig, ax = plt.subplots()
    ax.pie(data_dict.values(), labels=data_dict.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)


def draw_line_chart(values_list):
    fig, ax = plt.subplots()
    ax.plot(values_list)
    ax.set_xlabel('Index')
    ax.set_ylabel('Value')
    ax.set_title('Line Chart')
    st.pyplot(fig)

