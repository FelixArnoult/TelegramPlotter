#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import subprocess
import sys
import os
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('../image-getter')

import fetchImageFromQwant as getImg
import processImage as procImg
import convertImage as cvtImg
import createGcode as crtGc


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup,
                        InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, PicklePersistence)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

KEYWORD, SELECTPHOTO, LAUNCHPRINT = range(3)
HOME, SET = range(2)

config_kw = ["SEARCH_ENGINE","SEARCH_TYPE","IMAGE_PROCESS","NB_DISPLAYED_PHOTO", 'SUMUP']
dico_kb = { config_kw[0]: ["Google", "Qwant"],
            config_kw[1]: ["Preference", "Mot clé"],
            config_kw[2]: ["Oui", "Non"],
            config_kw[3]: list(str(i) for i in range(1,10))}


def build_menu(buttons,
               n_cols,
               header_buttons = None,
               footer_buttons = None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def start(update, context):
    # reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hi! My name is BoardPlotter Bot. I can draw whatever you want. '
        'Send /cancel to stop talking to me.\n\n'
        'What do you want me to draw?')
        # reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return KEYWORD


def keyword(update, context):
    user = update.message.from_user
    logger.info("User %s search %s", user.first_name, update.message.text)

    update.message.reply_text('Hmmm, I\'ll see what I can find ...\nLet me few seconds ...')
    files = getImg.getImage([], update.message.text, context.user_data["NB_DISPLAYED_PHOTO"])
    update.message.reply_text('Select one image to print')

    for number, r in enumerate(files):
        update.message.reply_photo(caption='{}'.format(number), photo=open('.'.join(r), 'rb'))

    update.message.reply_text('Select one image to print', reply_markup=ReplyKeyboardMarkup([list(map(lambda x: str(x), range(len(files))))], one_time_keyboard=True))
    context.chat_data['files'] = files
    return SELECTPHOTO


def selectPhoto(update, context):
    reply_keyboard = [['UII', 'NOO']]

    user = update.message.from_user
    selected = int(update.message.text)
    files = context.chat_data['files']
    logger.info("User %s choose %s to gcode", user.first_name, files[selected])
    files[selected], files[-1] = files[-1], files[selected]
    files.extend(cvtImg.convertImageToSvg(files))
    files.extend(crtGc.writeGcode(files, ['./output', "gcode"]))

    update.message.reply_text('Gcode file created\nSend it to printer ?', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    context.chat_data['files'] = files

    return LAUNCHPRINT

def launchPrint(update, context):
    if(update.message.text == 'UII'):
        streamer = os.environ["DRAWING_BOT_STREAMER"]
        args = ['.'.join(['./output', "gcode"]), "/dev/ttyACM0"]
        returned_value = subprocess.call(streamer +' ' + ' '.join(args), shell=True)
        update.message.reply_text('Print running ...')
    else:
        update.message.reply_text('Maybe later')

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def config(update, context):
    user = update.message.from_user
    logger.info("User %s started to edit.", user.first_name)
    keyboard = []
    keyboard = list(InlineKeyboardButton(cmd, callback_data=cmd) for cmd in config_kw)
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
    update.message.reply_text(
        "Config",
        reply_markup=reply_markup
    )
    return HOME


def sumup(update, context):
    bot = context.bot
    query = update.callback_query
    # logger.info("User %s asked for a sumup.", update.callback_query.message.from.first_name)

    reply = "Sumup :\n"
    if(context.user_data.get(config_kw[0], None) != None):
        reply += "{} - {}\n".format(config_kw[0], dico_kb.get(config_kw[0])[context.user_data[config_kw[0]]])
    if(context.user_data.get(config_kw[1], None) != None):
        reply += "{} - {}\n".format(config_kw[1], dico_kb.get(config_kw[1])[context.user_data[config_kw[1]]])
    if(context.user_data.get(config_kw[2], None) != None):
        reply += "{} - {}\n".format(config_kw[2], dico_kb.get(config_kw[2])[context.user_data[config_kw[2]]])
    if(context.user_data.get(config_kw[3], None) != None):
        reply += "{} - {}".format(config_kw[3], dico_kb.get(config_kw[3])[context.user_data[config_kw[3]]])

    bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text = reply)

    return ConversationHandler.END

def chooseConfig(update, context):
    bot = context.bot
    query = update.callback_query
    # logger.info("User %s started to edit %s", update.callback_query.message.from.first_name, query.data)

    context.user_data['choice'] = query.data
    context.user_data['current_kb'] = dico_kb.get(query.data)
    keyboard = list(InlineKeyboardButton(cmd, callback_data=cmd) for cmd in dico_kb.get(query.data))
    reply_markup = InlineKeyboardMarkup(build_menu(keyboard, n_cols=2))
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Select search engine",
        reply_markup=reply_markup
    )
    return SET

def setConfig(update, context):
    bot = context.bot
    query = update.callback_query
    # logger.info("User %s changed %s = %s", update.callback_query.message.from.first_name, context.user_data['choice'], query.data)

    choice = context.user_data['choice']
    current_kb = context.user_data['current_kb']
    index = current_kb.index(query.data)
    if(index != -1):
        context.user_data[choice] = index
        bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text="Config edited"
        )
    return sumup(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater(os.environ["TELEGRAM_TOKER"], persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states KEYWORD, SELECTPHOTO, LAUNCHPRINT and BIO
    conv_draw = ConversationHandler(
        entry_points=[CommandHandler('draw', start)],

        states={
            KEYWORD: [MessageHandler(Filters.text, keyword)],

            SELECTPHOTO: [MessageHandler(Filters.regex('^[0-9]+$'), selectPhoto)],

            LAUNCHPRINT: [MessageHandler(Filters.regex('^(UII|NOO)$'), launchPrint)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    conv_config = ConversationHandler(
        entry_points=[CommandHandler('config', config)],
        states={
            HOME: [ CallbackQueryHandler(chooseConfig, pattern='^'+ '|'.join(config_kw[:-1])+'$'),
                    CallbackQueryHandler(sumup, pattern='^'+ config_kw[-1] +'$')],
            SET: [ CallbackQueryHandler(setConfig)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


    dp.add_handler(conv_draw)
    dp.add_handler(conv_config)

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
