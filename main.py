#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import datetime
import logging
import os

import pytz
import telegram
from dotenv import load_dotenv
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
from logic.astronomy import get_moon_txt
from logic.constants import you_are_not_member_of_channel

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user_id = update.effective_user.id
    member_info = context.bot.get_chat_member(chat_id=os.getenv('GROUP_CHAT_ID'), user_id=user_id)
    if member_info.status == 'left':
        update.message.reply_text(you_are_not_member_of_channel)
    else:
        txt = get_moon_txt()
        update.message.reply_markdown_v2(txt)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("برای شروع /start را بفرستید.")


def astropy_daily_report(context: telegram.ext.CallbackContext):
    txt = get_moon_txt()
    context.bot.send_message(chat_id=os.getenv('GROUP_CHAT_ID'), parse_mode=ParseMode.MARKDOWN_V2,
                             text=txt)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    load_dotenv(".env")
    updater = Updater(os.getenv('BOT_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    tehran_timezone = pytz.timezone("Asia/Tehran")
    job_minute = updater.job_queue.run_daily(astropy_daily_report, datetime.time(6, 0, 0, tzinfo=tehran_timezone))
    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
