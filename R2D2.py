import numpy as np
from tda.orders.equities import equity_buy_limit, equity_buy_market, equity_sell_limit, equity_sell_market
from tda.orders.common import Duration, Session
import atexit
import datetime
import tda
import config
import logging




today = datetime.datetime.today()

logging.basicConfig(filename='log.txt')

logger = logging.getLogger()

# logger.setLevel(logging.INFO)

# logger.info(today.strftime('%D %T'))


symbolList = ['NVDA', 'AMD'] #symbol or symbols to use


def make_webdriver():
    # Import selenium here because it's slow to import
    from selenium import webdriver

    driver = webdriver.Chrome()
    atexit.register(lambda: driver.quit())
    return driver

# create client
client = tda.auth.easy_client(
    config.api_key,
    config.redirect_uri,
    config.token_path_lightsail,
    # config.token_path_local,
    make_webdriver)


def everyMarketOpen():

    for symbol in symbolList:
        sevenDayLow = getSevenDayLow(symbol)
        twoHundredDayMovingAverage = getTwoHundredDayMovingAverage(symbol)
        sevenDayHigh = getSevenDayHigh(symbol)
        currentPositions = getCurrentPositions(config.account_id)
        yesterdayClosePrice = getYesterdayClose(symbol)
        currentAccountBalance = getCurrentAccountBalance(config.account_id)
        currentMarketPrice = getCurrentMarketPrice(symbol)
        initialBuyPrice = currentPositions #figure out way to store initial buy price
        tradePlaced = False

        print(f'{symbol}')
        print(f'Two hundred day simple moving average: {twoHundredDayMovingAverage}')
        print(f'Seven day low for {symbol}: {sevenDayLow}')
        print(f'Current market price: {currentMarketPrice}')


        #buy when current closing price is lower than previous seven day low and above it's 200 day moving average
        if yesterdayClosePrice < sevenDayLow and yesterdayClosePrice > twoHundredDayMovingAverage and currentMarketPrice < sevenDayLow:
            if currentAccountBalance > currentMarketPrice:
                print(f'Bought {symbol} at {currentMarketPrice}')
                print('\n')
                tradePlaced = True
                # logger.info(f'One share of {symbol} bought at {currentMarketPrice}')
                client.place_order(config.account_id, equity_buy_market(symbol, 1))



        #sell when it closes above its previous seven day high and is higher than initial buy price
        if yesterdayClosePrice > sevenDayHigh and currentMarketPrice > sevenDayHigh and symbol in currentPositions and currentMarketPrice > twoHundredDayMovingAverage: #maybe add another check to see if currentMarketPrice is higher than init buy price
            print(f'Sold {symbol} at {currentMarketPrice}')
            print('\n')
            tradePlaced = True
            # logger.info(f'One share of {symbol} sold at {currentMarketPrice}')
            client.place_order(config.account_id, equity_sell_market(symbol, 1))

        if not tradePlaced:
            print(f'No trades placed for {symbol}')
            print('\n')

def getTwoHundredDayMovingAverage(symbol):
    td = datetime.timedelta(200)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=today).json()
    close = []
    for day in priceHistory['candles']:
        close.append(day['close'])
    movingAverage = sum(close) / 200
    return round(movingAverage, 2)

def getSevenDayLow(symbol):
    td = datetime.timedelta(9)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=today).json()
    lows = []
    for day in priceHistory['candles']:
        lows.append(day['low'])
    return min(lows)

def getSevenDayHigh(symbol):
    td = datetime.timedelta(9)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=today).json()
    highs = []
    for day in priceHistory['candles']:
        highs.append(day['high'])
    return max(highs)

def getCurrentPositions(accountID):
    positions = client.get_account(accountID, fields=client.Account.Fields.POSITIONS).json()
    currentPositions = []

    try:
        for position in positions['securitiesAccount']['positions']:
            currentPositions.append(position['instrument']['symbol'])
        return currentPositions
    except KeyError:
        print('No current positions')

        # logger.info('No current positions')

def getYesterdayClose(symbol):
    td = datetime.timedelta(4) #goes back till last day close in market
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=today).json()
    yesterdayClose = priceHistory['candles'][-1]['close']
    return yesterdayClose

def getCurrentAccountBalance(accountID):
    accountInfo = client.get_account(accountID).json()
    currentAccountBalance = accountInfo['securitiesAccount']['initialBalances']['cashAvailableForTrading']
    return currentAccountBalance

def getCurrentMarketPrice(symbol):
    quotes = client.get_quote(symbol).json()
    currentMarketPrice = quotes[symbol]['mark']
    return currentMarketPrice

#253747756