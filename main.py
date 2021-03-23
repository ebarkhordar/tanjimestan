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
from telegram import (
    ParseMode,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    Filters,
)

from logic.utils import get_moon_txt, planet_status
from logic.messages import Msg, Btn, Url

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)

CHOOSING, PHOTO, LOCATION, BIO = range(4)


# check user is in channel or not?
def is_member(func):
    def wrapper_is_member(*args, **kwargs):
        update = args[0]
        context = args[1]
        user_id = update.effective_user.id
        member_info = context.bot.get_chat_member(
            chat_id=os.getenv('GROUP_CHAT_ID'),
            user_id=user_id)
        if member_info.status == 'left':
            keyboard = [
                [InlineKeyboardButton(text=Btn.join_channel, url=Url.channel)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(Msg.you_are_not_member_of_channel,
                                      reply_markup=reply_markup)
        else:
            return func(*args, **kwargs)

    return wrapper_is_member


@is_member
def start(update: Update, _: CallbackContext) -> int:
    reply_keyboard = [[Btn.moon_status], [Btn.planets_status]]
    update.message.reply_text(
        Msg.start, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOOSING


@is_member
def premium_features(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        Msg.premium_msg,
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


@is_member
def photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Gorgeous! Now, send me your location please, or send /skip if you don\'t want to.'
    )

    return LOCATION


@is_member
def skip_photo(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'I bet you look great! Now, send me your location please, or send /skip.'
    )

    return LOCATION


@is_member
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


@is_member
def skip_location(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'You seem a bit paranoid! At last, tell me something about yourself.'
    )

    return BIO


@is_member
def bio(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thank you! I hope we can talk again some day.')

    return ConversationHandler.END


@is_member
def cancel(update: Update, _: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


@is_member
def moon_status(update: Update, context: CallbackContext) -> None:
    txt = get_moon_txt()
    update.message.reply_markdown_v2(txt)
    return ConversationHandler.END


@is_member
def planets_status(update: Update, context: CallbackContext) -> None:
    txt = planet_status()
    update.message.reply_markdown_v2(txt)
    return ConversationHandler.END


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
            CHOOSING: [MessageHandler(Filters.regex('^' + Btn.moon_status + '$'), moon_status),
                       MessageHandler(Filters.regex('^' + Btn.planets_status + '$'), planets_status)],
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
