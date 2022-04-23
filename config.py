import os
from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))
api_key = config("api_key")
# token_path_local = '/Users/luketyson/PycharmProjects/AlgoTrading/token.pickle'
# token_path_ubuntu = '/home/ubuntu/AlgoTrading/token.pickle'
token_path = os.path.join(basedir, 'token.pickle')
redirect_uri = 'https://localhost'
account_id = 253530748
cron_key = '6eea94b448e642e6a75ea98daa2395a4'
