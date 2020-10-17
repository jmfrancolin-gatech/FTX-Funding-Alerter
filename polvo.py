import pdb
import time
import client
import pandas as pd
from logzero import logger
from environs import Env
from datetime import datetime
import telegram


def get_futures(ts: int):
    names = []
    resp = ftx.get(ts, '/futures')
    for i in range(len(resp)):
        names.append(resp[i]['name'])
    return list(set(names))

def get_stats(ts: int):
    stats = []
    for future in LIST_OF_FUTURES:
        resp = ftx.get(ts, f'/futures/{future}/stats')
        try:
            stat = {'future':future, 'rate':resp['nextFundingRate']}
            stats.append(stat)
        except:
            continue
    stats = pd.DataFrame(stats)
    return stats.sort_values(by=['rate'], ascending=False).reset_index(drop=True)

def filter_stats(stats):
    if len(stats) > 2 * OUTPUT_NUMBER:
        stats = stats[0:OUTPUT_NUMBER].append(stats[-OUTPUT_NUMBER:]).reset_index(drop=True)
    return stats[abs(stats['rate']) > OUTPUT_THRESHOLD].reset_index(drop=True)

def create_report(ts: int, stats):

    report = '{timestamp}\n'.format(
        timestamp=datetime.fromtimestamp(ts/1000).strftime('%Y-%m-%d - %H:%M:%S'))
    
    report += 'Top {X}:\n'.format(X=OUTPUT_NUMBER)
    for i in range(OUTPUT_NUMBER):
        report += '{fut} ({rate})\n'.format(
            fut=stats.loc[i, 'future'], rate=stats.loc[i, 'rate'])
    
    report += 'Bottom {X}:\n'.format(X=OUTPUT_NUMBER)
    for i in range(OUTPUT_NUMBER):
        report += '{fut} ({rate})\n'.format(
            fut=stats.loc[len(stats)-1-i, 'future'], rate=stats.loc[len(stats)-1-i, 'rate'])

    return report

def output_report(report):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='FTX')
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report)

# set up env
env = Env()
env.read_env()
LIST_OF_FUTURES = env.list('LIST_OF_FUTURES')
UPDATE_DELAY = env.int('UPDATE_DELAY')
OUTPUT_NUMBER = env.int('OUTPUT_NUMBER')
OUTPUT_THRESHOLD = env.int('OUTPUT_THRESHOLD')
TELEGRAM_TOKEN = env.str('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = env.str('TELEGRAM_CHAT_ID')

# set up client
api_key = '29kj-641Ku1rAE0zHyw0YFfopYXkcr-BTz46SB2C'
api_secret = 'cZ4MWnPI-mQUvCB9G0O8NQQqkcGyXMHdBKxjz22E'
ftx = client.FtxClient(api_key=api_key, api_secret=api_secret)

ts = int(time.time() * 1000)

if LIST_OF_FUTURES[0].lower() == 'all':
    LIST_OF_FUTURES = get_futures(ts)

stats = get_stats(ts)
stats = filter_stats(stats)
report = create_report(ts, stats)
logger.info(report)
output_report(report)
