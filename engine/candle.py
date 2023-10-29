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




