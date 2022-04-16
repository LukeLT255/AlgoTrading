import logging
from tda.orders.equities import equity_buy_market, equity_sell_market
import atexit
import datetime
import tda
import config
from app import db
from app import Account
import time

logging.basicConfig(level=logging.INFO,
                    format='{asctime} {levelname:<8} {message}',
                    style='{',
                    # force=True,
                    filename='%slog' % __file__[:-2],
                    filemode='a')

today = datetime.datetime.today()
yesterday = datetime.datetime.today() - datetime.timedelta(1)

symbolList = ['NVDA', 'AMD']  # symbol or symbols to use


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
    config.token_path,
    make_webdriver)


def every_market_open():

    for symbol in symbolList:
        sevenDayLow = get_seven_day_low(symbol)
        twoHundredDayMovingAverage = get_two_hundred_day_moving_average(symbol)
        sevenDayHigh = get_seven_day_high(symbol)
        currentPositions = get_current_positions(config.account_id)
        yesterdayClosePrice = get_yesterday_close(symbol)
        currentAccountBalance = get_current_account_balance(config.account_id)
        currentMarketPrice = get_current_market_price(symbol)
        tradePlaced = False
        numberOfShares = get_number_of_shares(symbol, config.account_id)

        logging.info(f'{symbol}')
        logging.info(f'Two hundred day simple moving average: {twoHundredDayMovingAverage}')
        logging.info(f'Seven day low for {symbol}: {sevenDayLow}')
        logging.info(f'Seven day high for {symbol}: {sevenDayHigh}')
        logging.info(f'Current market price: {currentMarketPrice}')
        logging.info(currentPositions)
        logging.info(numberOfShares)
        logging.info(currentAccountBalance)

        # buy when current closing price is lower than previous seven day low and above it's 200 day moving average
        if yesterdayClosePrice < sevenDayLow and yesterdayClosePrice > twoHundredDayMovingAverage and currentMarketPrice < sevenDayLow:
            if currentAccountBalance > currentMarketPrice:  # and config.max_shares > numberOfShares:
                logging.info(f'Bought {symbol} at {currentMarketPrice}')
                logging.info('\n')
                tradePlaced = True
                client.place_order(config.account_id, equity_buy_market(symbol, 1))

        # sell when it closes above its previous seven day high and is higher than initial buy price
        if currentMarketPrice > sevenDayHigh and symbol in currentPositions and currentMarketPrice > twoHundredDayMovingAverage:  # maybe add another check to see if currentMarketPrice is higher than init buy price
            logging.info(f'Sold {symbol} at {currentMarketPrice}')
            logging.info('\n')
            tradePlaced = True
            client.place_order(config.account_id, equity_sell_market(symbol, 1))

        if not tradePlaced:
            logging.info(f'No trades placed for {symbol}')
            logging.info('\n')

    account_value = get_total_account_value(config.account_id, symbolList)
    accountValue = Account(value=account_value)
    db.session.add(accountValue)
    db.session.commit()


def get_two_hundred_day_moving_average(symbol):
    td = datetime.timedelta(200)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=yesterday).json()
    close = []
    for day in priceHistory['candles']:
        close.append(day['close'])
    movingAverage = sum(close) / 200
    return round(movingAverage, 2)


def get_seven_day_low(symbol):
    td = datetime.timedelta(8)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=yesterday).json()
    lows = []
    for day in priceHistory['candles']:
        lows.append(day['low'])
    return min(lows)


def get_seven_day_high(symbol):
    td = datetime.timedelta(8)
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=yesterday).json()
    highs = []
    for day in priceHistory['candles']:
        highs.append(day['high'])
    return max(highs)


def get_current_positions(accountID):
    positions = client.get_account(accountID, fields=client.Account.Fields.POSITIONS).json()
    currentPositions = []
    # print(positions)

    try:
        for position in positions['securitiesAccount']['positions']:
            currentPositions.append(position['instrument']['symbol'])
        return currentPositions
    except KeyError:
        return currentPositions


def get_yesterday_close(symbol):
    td = datetime.timedelta(4)  # goes back till last day close in market
    priceHistory = client.get_price_history_every_day(symbol, start_datetime=today - td, end_datetime=today).json()
    yesterdayClose = priceHistory['candles'][-1]['close']
    return yesterdayClose


def get_current_account_balance(accountID):
    accountInfo = client.get_account(accountID).json()
    currentAccountBalance = accountInfo['securitiesAccount']['currentBalances']['cashBalance']
    return currentAccountBalance


def get_current_market_price(symbol):
    quotes = client.get_quote(symbol).json()
    currentMarketPrice = quotes[symbol]['mark']
    return currentMarketPrice


def get_number_of_shares(symbol, accountID):
    positions = client.get_account(accountID, fields=client.Account.Fields.POSITIONS).json()
    numOfShares = 0
    try:
        for position in positions['securitiesAccount']['positions']:
            if position['instrument']['symbol'] == symbol:
                numOfShares = position['longQuantity']
        return numOfShares
    except KeyError:
        return numOfShares

def get_total_account_value(accountID, symbols):
    # balance = getCurrentAccountBalance(accountID)

    accountInfo = client.get_account(accountID).json()
    currentAccountBalance = accountInfo['securitiesAccount']['currentBalances']['cashBalance']

    for symbol in symbols:
        positions = client.get_account(accountID, fields=client.Account.Fields.POSITIONS).json()
        numOfShares = 0
        try:
            for position in positions['securitiesAccount']['positions']:
                if position['instrument']['symbol'] == symbol:
                    numOfShares = position['longQuantity']
        except KeyError:
            pass
        symbolValue = getCurrentMarketPrice(symbol)
        value = symbolValue * numOfShares
        currentAccountBalance += round(value, 2)

    return round(currentAccountBalance, 2)




# 253747756
