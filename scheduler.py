# import R2D2
import cronitor
import config

cronitor.api_key = config.cron_key

@cronitor.job('trading-bot')
def runR2D2():
    print('job ran')
runR2D2()



