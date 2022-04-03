from tda import auth
import config

from selenium import webdriver

with webdriver.Chrome(executable_path='/Users/luketyson/PycharmProjects/AlgoTrading/chromedriver') as driver:
        c = auth.client_from_login_flow(
            driver, config.api_key, config.redirect_uri, config.token_path_local)