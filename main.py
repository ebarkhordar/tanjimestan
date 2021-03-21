#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# This program is dedicated to the public domain under the CC0 license.

import datetime
import logging
import os

import pytz
import telegram
from dotenv import load_dotenv
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

# Enable logging
from logic.utils import get_moon_txt
from logic.messages import Msg

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, PHOTO, LOCATION, BIO = range(4)


def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [[Msg.moon_status], [Msg.premium_features]]
    update.message.reply_text(
        Msg.start,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOOSING


def premium_features(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        Msg.premium_msg,
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


def skip_photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


def location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    user_location = update.message.location
    logger.info(
        "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
    )
    update.message.reply_text(
        'Maybe I can visit you sometime! At last, tell me something about yourself.'
    )

    return BIO


def skip_location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


def bio(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def status(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /status is issued."""
    user_id = update.effective_user.id
    member_info = context.bot.get_chat_member(
        chat_id=os.getenv('GROUP_CHAT_ID'),
        user_id=user_id)
    if member_info.status == 'left':
        update.message.reply_text(Msg.you_are_not_member_of_channel)
    else:
        txt = get_moon_txt()
        update.message.reply_markdown_v2(txt)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("برای شروع /start را بفرستید.")


def astropy_daily_report(context: telegram.ext.CallbackContext):
    txt = get_moon_txt()
    context.bot.send_message(chat_id=os.getenv('GROUP_CHAT_ID'),
                             parse_mode=ParseMode.MARKDOWN_V2,
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
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [MessageHandler(Filters.regex('^' + Msg.premium_features + '$'), premium_features),
                       MessageHandler(Filters.regex('^' + Msg.moon_status + '$'), status)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            LOCATION: [
                MessageHandler(Filters.location, location),
                CommandHandler('skip', skip_location),
            ],
            BIO: [MessageHandler(Filters.text & ~Filters.command, bio)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    # on different commands - answer in Telegram

    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("help", help_command))
    tehran_timezone = pytz.timezone("Asia/Tehran")
    job_minute = updater.job_queue.run_daily(
        astropy_daily_report,
        datetime.time(6, 0, 0, tzinfo=tehran_timezone))
    # on non_command i.e message - echo the message on Telegram
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
