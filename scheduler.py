
import cronitor
import R2D2
import config

cronitor.api_key = config.cron_key

@cronitor.job('trading-bot')
def runR2D2():
    R2D2.every_market_open()

if __name__ == '__main__':
    runR2D2()



