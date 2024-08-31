#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# This program is dedicated to the public domain under the CC0 license.

import datetime
import logging
import os

import pytz
from dotenv import load_dotenv
from persiantools import digits
from persiantools.jdatetime import JalaliDateTime
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

from logic.messages import Msg, Btn, Url
from logic.utils import get_moon_txt, planet_status

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=os.getenv("LOGGING_LEVEL", logging.INFO)
)

logger = logging.getLogger(__name__)

CHOOSING, PHOTO, LOCATION, BIO, DATE, TIME = range(6)


# check user is in channel or not?
def is_member(func):
    async def wrapper_is_member(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        member_info = await context.bot.get_chat_member(
            chat_id=os.getenv('GROUP_CHAT_ID'),
            user_id=user_id)
        if member_info.status == 'left':
            keyboard = [
                [InlineKeyboardButton(text=Btn.join_channel, url=Url.channel)],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(Msg.you_are_not_member_of_channel,
                                            reply_markup=reply_markup)
        else:
            return await func(update, context)

    return wrapper_is_member


@is_member
async def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [[Btn.moon_status], [Btn.planets_status], [Btn.custom_datetime]]
    await update.message.reply_text(
        Msg.start, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOOSING


@is_member
async def premium_features(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        Msg.premium_msg,
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


@is_member
async def moon_status(update: Update, context: CallbackContext) -> None:
    txt = get_moon_txt()
    await update.message.reply_markdown_v2(txt)


@is_member
async def planets_status(update: Update, context: CallbackContext) -> None:
    txt = planet_status()
    await update.message.reply_markdown_v2(txt)


@is_member
async def get_date(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        Msg.request_date,
        reply_markup=ReplyKeyboardRemove(),
    )
    return DATE


@is_member
async def get_time(update: Update, context: CallbackContext) -> None:
    date_text = update.effective_message.text
    context.user_data['custom_date'] = date_text
    await update.message.reply_text(
        Msg.request_time,
        reply_markup=ReplyKeyboardRemove(),
    )
    return TIME


@is_member
async def custom_datetime_planets_status(update: Update, context: CallbackContext) -> None:
    try:
        custom_time = update.effective_message.text
        custom_date = context.user_data['custom_date']
        custom_time = digits.fa_to_en(custom_time)
        custom_date = digits.fa_to_en(custom_date)

        custom_date_split = custom_date.split("/")
        year = int(custom_date_split[0])
        month = int(custom_date_split[1])
        day = int(custom_date_split[2])
        custom_time_split = custom_time.split(":")
        hour = int(custom_time_split[0])
        minute = int(custom_time_split[1])
        specific_datetime = JalaliDateTime(
            year, month, day,
            hour, minute).to_gregorian().strftime("%Y-%m-%d %H:%M")
        txt = planet_status(specific_datetime)
        await update.message.reply_markdown_v2(txt, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    except Exception as e:
        print(e)
        await update.message.reply_text(
            Msg.invalid_datetime,
            reply_markup=ReplyKeyboardRemove(),
        )
        return await get_date(update, context)


async def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("برای شروع /start را بفرستید.")


async def astropy_daily_report(context: CallbackContext):
    txt = get_moon_txt()
    await context.bot.send_message(chat_id=os.getenv('GROUP_CHAT_ID'),
                                   parse_mode=ParseMode.MARKDOWN_V2,
                                   text=txt)


def main():
    """Start the bot."""
    # Load environment variables
    load_dotenv(".env")

    # Create the Application
    application = Application.builder().token(os.getenv('BOT_TOKEN')).build()

    # Get the dispatcher to register handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex('^' + Btn.moon_status + '$'), moon_status),
                MessageHandler(filters.Regex('^' + Btn.planets_status + '$'), planets_status),
                MessageHandler(filters.Regex('^' + Btn.custom_datetime + '$'), get_date),
            ],
            DATE: [MessageHandler(filters.TEXT, get_time)],
            TIME: [MessageHandler(filters.TEXT, custom_datetime_planets_status)],

        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("help", help_command))

    # Setup job queue for daily reports
    tehran_timezone = pytz.timezone("Asia/Tehran")
    application.job_queue.run_daily(
        astropy_daily_report,
        datetime.time(6, 0, 0, tzinfo=tehran_timezone))

    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()
