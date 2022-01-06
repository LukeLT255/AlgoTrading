import R2D2
import time
import schedule

EasternTimeMarketOpenTime = '09:30'
CentralTimeMarketOpenTime = '08:30'

if __name__ == '__main__':
    schedule.every().day.at(CentralTimeMarketOpenTime).do(R2D2.everyMarketOpen())
    while True:
        schedule.run_pending()
        time.sleep(1)
