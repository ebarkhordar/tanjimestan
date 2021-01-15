import os
import time

import schedule
from dotenv import load_dotenv
from telegram import Bot

from astronomy import get_moon_txt

load_dotenv(".env")
bot = Bot(os.getenv('BOT_TOKEN'))


def job(t):
    print("Sending new message...", t)
    txt = get_moon_txt()
    print(os.getenv("GROUP_CHAT_ID"))
    bot.send_message(chat_id=os.getenv("GROUP_CHAT_ID"),
                     text=txt)
    return


schedule.every().day.at("06:00").do(job, 'It is 06:00')

while True:
    schedule.run_pending()
    time.sleep(60)  # wait one minute
