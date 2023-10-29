import cvxpy as cp
import numpy as np
import pandas as pd

def optimize_portfolio(returns, current_weights, big_tokens=["BTC", "ETH"], cash_tokens=["USDT", "USDC", "BUSD"], alpha=0.05):
    n = returns.shape[1]
    mu = returns.mean().values
    Sigma = returns.cov().values
    
    w = cp.Variable(n)
    gamma = cp.Parameter(nonneg=True)
    ret = mu.T @ w
    risk = cp.quad_form(w, Sigma)
    objective = cp.Maximize(ret - gamma*risk)
    
    constraints = [
        cp.sum(w) == 1,
        w >= 0
    ]

    for token, weight in current_weights.items():
        index = list(returns.columns).index(token)
        if token in big_tokens:
            constraints.append(w[index] >= weight * (1 - alpha))
            constraints.append(w[index] <= weight * (1 + alpha))
        elif token in cash_tokens:
            constraints.append(w[index] == weight)
        else:
            constraints.append(w[index] >= 0)
            constraints.append(w[index] <= weight * (1 + alpha))
    
    prob = cp.Problem(objective, constraints)
    gamma.value = 0.1
    prob.solve()
    

    return dict(zip(returns.columns, w.value))


def compute_returns(data, start_day=0, days=7):
    all_returns = {}

    for token, candles in data.items():
        prices = [candle.close_price for candle in candles[start_day:start_day+days*24]]
        returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(1, len(prices))]
        all_returns[token] = returns

    return pd.DataFrame(all_returns)


def next_day_update(data, current_day_index):
    
    next_day_returns = compute_returns(data, start_day=current_day_index, days=1)


    current_weights = optimize_portfolio(next_day_returns)
    
    
    next_day_data = {
        token: data[token][current_day_index+1:current_day_index+25] for token in data.keys()
    }

    
    next_day_returns = compute_returns(next_day_data, start_day=0, days=1)
    
    
    next_day_optimized_weights = optimize_portfolio(next_day_returns)
    
    return next_day_optimized_weights