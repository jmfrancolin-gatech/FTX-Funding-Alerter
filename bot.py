import pdb
import client
import pandas as pd
from logzero import logger
from environs import Env
from datetime import datetime
import telegram
import config
import time

from dateutil import tz

class Bot:

    def __init__(self):
        # set up ftx client
        self.ftx_client = client.FtxClient(
            api_key=config.ftx_api_key, api_secret=config.ftx_api_secret)

        # set up bot parameters
        env = Env()
        env.read_env()
        self.UPDATE_DELAY = env.int('UPDATE_DELAY')
        self.OUTPUT_NUMBER = env.int('OUTPUT_NUMBER')
        self.OUTPUT_THRESHOLD = env.int('OUTPUT_THRESHOLD')
        self.LIST_OF_FUTURES = env.list('LIST_OF_FUTURES')
        
        # attempt to set up telegram client
        try:
            self.tg_client = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
            self.TELEGRAM_CHAT_ID = env.str('TELEGRAM_CHAT_ID')
        except:
            self.tg_client = None
            self.TELEGRAM_CHAT_ID = None

        # time of lastest queried rate
        self.rate_time = None

    def start(self):

        # loop forever
        while True:
            rates = self.get_rates()
            rates = self.filter_rates(rates)
            report = self.create_report(rates)
            self.post_report(report)
            time.sleep(self.UPDATE_DELAY)

    def get_rates(self):
        resp = self.ftx_client.get('/funding_rates')
        rates = pd.DataFrame(resp)
        return rates.sort_values(by=['rate'], ascending=False).reset_index(drop=True)
 
    def filter_rates(self, rates):

        # filter by latest time
        max_utc = max(rates['time'])
        rates = rates[rates['time'] == max_utc]

        # save max_utc as local time
        self.rate_time = self.convert_timezone(max_utc)

        # filter by future names
        if self.LIST_OF_FUTURES[0].lower() != 'all':
            rates = rates[rates['future'].isin(LIST_OF_FUTURES)]

        # filter by number of futures
        if len(rates) > 2 * self.OUTPUT_NUMBER:
            rates = rates.reset_index(drop=True)
            rates = rates[0:self.OUTPUT_NUMBER].append(rates[-self.OUTPUT_NUMBER:])

        # filter by rate threshold
        rates = rates[abs(rates['rate']) > self.OUTPUT_THRESHOLD]

        return rates.reset_index(drop=True)

    def create_report(self, rates):

        report = '[{timestamp}]\n'.format(
            timestamp=self.rate_time.strftime("%Y-%m-%d - %H:%M:%S"))
        
        report += 'Top {X}:\n'.format(X=self.OUTPUT_NUMBER)
        for i in range(self.OUTPUT_NUMBER):
            report += '{fut} ({rate:.6f})\n'.format(
                fut=rates.loc[i, 'future'], rate=rates.loc[i, 'rate'])
        
        report += 'Bottom {X}:\n'.format(X=self.OUTPUT_NUMBER)
        for i in range(self.OUTPUT_NUMBER):
            report += '{fut} ({rate:.6f})\n'.format(
                fut=rates.loc[len(rates)-1-i, 'future'], rate=rates.loc[len(rates)-1-i, 'rate'])

        return report

    def post_report(self, report):
        if self.tg_client != None:
            self.tg_client.send_message(chat_id=self.TELEGRAM_CHAT_ID, text=report)
        else:
            logger.info(report)

    def convert_timezone(self, utc: str):
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S%z')
        utc = utc.replace(tzinfo=from_zone)
        return utc.astimezone(to_zone)

if __name__ == '__main__':
    bot = Bot()
    bot.start()