import pdb
import client
import pandas as pd
from logzero import logger
from environs import Env
from datetime import datetime
import telegram
import config
import time

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
        if self.LIST_OF_FUTURES[0].lower() == 'all':
            self.LIST_OF_FUTURES = self.get_futures()
        
        # attempt to set up telegram client
        try:
            self.tg_client = telegram.Bot(token=env.str('TELEGRAM_TOKEN'))
            self.TELEGRAM_CHAT_ID = env.str('TELEGRAM_CHAT_ID')
        except:
            self.tg_client = None
            self.TELEGRAM_CHAT_ID = None

    def start(self):
        # keep track of starting time
        self.ts = int(time.time())
        # loop forever
        while True:
            stats = self.get_stats()
            stats = self.filter_stats(stats)
            report = self.create_report(stats)
            self.post_report(report)

            # self.ts += self.UPDATE_DELAY
            time.sleep(self.UPDATE_DELAY)

    def get_futures(self):
        names = []
        resp = self.ftx_client.get('/futures')
        for i in range(len(resp)):
            names.append(resp[i]['name'])
        return list(set(names))

    def get_stats(self):
        stats = []
        for future in self.LIST_OF_FUTURES:
            resp = self.ftx_client.get(f'/futures/{future}/stats')
            pdb.set_trace()
            try:
                stat = {'future':future, 'rate':resp['nextFundingRate']}
                stats.append(stat)
            except:
                continue
        stats = pd.DataFrame(stats)
        return stats.sort_values(by=['rate'], ascending=False).reset_index(drop=True)

    def filter_stats(self, stats):
        if len(stats) > 2 * self.OUTPUT_NUMBER:
            stats = stats[0:self.OUTPUT_NUMBER].append(stats[-self.OUTPUT_NUMBER:]).reset_index(drop=True)
        return stats[abs(stats['rate']) > self.OUTPUT_THRESHOLD].reset_index(drop=True)

    def create_report(self, stats):

        report = '{timestamp}\n'.format(
            timestamp=datetime.fromtimestamp(self.ts).strftime('%Y-%m-%d - %H:%M:%S'))
        
        report += 'Top {X}:\n'.format(X=self.OUTPUT_NUMBER)
        for i in range(self.OUTPUT_NUMBER):
            report += '{fut} ({rate})\n'.format(
                fut=stats.loc[i, 'future'], rate=stats.loc[i, 'rate'])
        
        report += 'Bottom {X}:\n'.format(X=self.OUTPUT_NUMBER)
        for i in range(self.OUTPUT_NUMBER):
            report += '{fut} ({rate})\n'.format(
                fut=stats.loc[-self.OUTPUT_NUMBER+i, 'future'], rate=stats.loc[-self.OUTPUT_NUMBER+i, 'rate'])

        return report

    def post_report(self, report):

        if self.tg_client != None:
            self.tg_client.send_message(chat_id=self.TELEGRAM_CHAT_ID, text=report)
        else:
            logger.info(report)


if __name__ == '__main__':
    bot = Bot()
    bot.start()