import numpy as np
from tda.orders.equities import equity_buy_limit, equity_buy_market, equity_sell_limit
from tda.orders.common import Duration, Session
import atexit
import datetime
import tda
import config

lookBack = 20
initStopRisk = 0.98
trailingStopRisk = 0.9
ceiling, floor = 30, 10
today = datetime.datetime.today()



print(today.strftime('%D %T'))


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
    make_webdriver)

# @cronitor.job('trading-bot')
def everyMarketOpen():
    for symbol in symbolList:
        dataForLastMonth = client.get_price_history_every_day(symbol, start_datetime=today - datetime.timedelta(days=31), end_datetime=today).json()

        close = []
        for day in dataForLastMonth['candles']: #get close prices for previous month
            close.append(day['close'])

        todayVol = np.std(close[1:len(close)])
        yesterdayVol = np.std(close[0:len(close)-1])
        deltaVol = (todayVol - yesterdayVol) / todayVol
        global lookBack
        lookBack = round(lookBack * (1 + deltaVol))

        if lookBack > ceiling: #checking if dynamic lookBack is greater than ceiling
            lookBack = ceiling
        elif lookBack < floor: #checking if dynamic lookBack is less than floor
            lookBack = floor

        dataFromLookBackDate = client.get_price_history_every_day(symbol, start_datetime=today - datetime.timedelta(days=lookBack),
                                                              end_datetime=today).json()
        highs = []
        for day in dataFromLookBackDate['candles']: #get price highs from lookback date to now
            highs.append(day['high'])

        accountInfo = client.get_account(config.account_id, fields=client.Account.Fields.POSITIONS).json()
        cashAvailableForTrading = accountInfo['securitiesAccount']['initialBalances']['cashAvailableForTrading']
        currentlyInvested = []
        try:
            for position in accountInfo['securitiesAccount']['positions']:
                currentlyInvested.append(position['instrument']['symbol'])
        except KeyError:
            print('No positions found')
        symbolQuote = client.get_quotes(symbol).json()
        currentSymbolPrice = symbolQuote[symbol]['askPrice']
        print(f'Yesterday close for {symbol}: ' + str(close[-2]))
        h = max(highs[:-1])
        print(f'High for {symbol} ' + f'in last {lookBack} days: ' + str(h))
        if symbol not in currentlyInvested and close[-2] >= max(highs[:-1]): # checks if we are currently invested, and if the last close was higher than the highest high, buy at market price
            if cashAvailableForTrading > currentSymbolPrice:
                print('Buy Order placed for ' + symbol + ' at ' + str(currentSymbolPrice) + '\n')
                client.place_order(config.account_id, equity_buy_market(symbol, 1)) #buy quantity
                breakoutlvl = max(highs[:-1])
                highestPrice = breakoutlvl


        orders = client.get_orders_by_path(config.account_id, status=client.Order.Status.FILLED).json()
        print('Orders: ')
        print(*orders, sep='\n')
        openOrders = []
        for order in orders:
            openOrders.append(order['orderLegCollection'][0]['instrument']['symbol'])


        #trailing stop loss sell
        if symbol in currentlyInvested: #check if we are currently invested in symbol
            if not symbol in openOrders: #check if there is an open order for symbol
                print('Stop order sell placed for ' + symbol + 'at ' + str(initStopRisk * breakoutlvl) + '\n')
                client.place_order(config.account_id, equity_sell_limit(symbol, 1, initStopRisk * breakoutlvl))

            if close[-1] > highestPrice and initStopRisk * breakoutlvl < close[-2] * trailingStopRisk: #makes this a trailing stop loss
                highestPrice = close[-2]
                order_id = ''
                orders = client.get_orders_by_path(config.account_id, status=client.Order.Status.AWAITING_CONDITION)
                for order in orders:
                    if order['orderLegCollection'][0]['instrument']['symbol'] == symbol:
                        order_id = order['orderId']
                stopPrice = close[-2] * trailingStopRisk
                client.replace_order(config.account_id, order_id, equity_sell_limit(symbol, 1, stopPrice))

                print(f'New stop price for {symbol}: ' + str(stopPrice)) #print new stop price to terminal


everyMarketOpen()

# 253747756