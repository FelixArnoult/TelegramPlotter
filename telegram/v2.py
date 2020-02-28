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

import subprocessTest
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import Pool
import logging
import subprocess
import sys
import os
import time
# the mock-0.3.1 dir contains testcase.py, testutils.py & mock.py
sys.path.append('../image-getter')

import fetchImageFromQwant as getImg
import processImage as procImg
import convertImage as cvtImg
import createGcode as crtGc


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup,
                        InlineKeyboardButton, File)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, PicklePersistence)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)#,
                    # filename='drawing_telegram2.log')

logger = logging.getLogger(__name__)
AVAILABLE, SEARCHING, COMPUTING, PRINTING = range(4)
HOME, SET = range(2)

config_kw = ["SEARCH_ENGINE","SEARCH_TYPE","IMAGE_PROCESS","NB_DISPLAYED_PHOTO", 'SUMUP']
dico_kb = { config_kw[0]: ["Google", "Qwant"],
            config_kw[1]: ["Preference", "Mot clé"],
            config_kw[2]: ["Oui", "Non"],
            config_kw[3]: list(str(i) for i in range(1,10))}

DEFAULT_SETTINGS = {'SEARCH_ENGINE': 1, 'IMAGE_PROCESS': 1, 'SEARCH_TYPE': 1, 'NB_DISPLAYED_PHOTO': 3}


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

class DrawingTelegram(object):
    def __init__(self):
        self.PYTHON = '/usr/bin/python3'
        self.STREAM = os.environ["DRAWING_BOT_STREAM"]
        # self.STREAM = "./subprocessTest.py"
        self.IMAGE_GETTER = './subprocessTest.py'
        self.fileCreated = []
        self.fetchImage_pool = Pool()
        self.state = AVAILABLE


    def fetchImage(self, update, context):
        user = update.message.from_user
        search_text = context.args[0]
        logger.info("User %s search %s", user.first_name, search_text)
        # print(self.fetchImage_pool.ready())
        if(self.state == AVAILABLE):
            self.state = SEARCHING
            update.message.reply_text('Hmmm, I\'ll see what I can find ...\nLet me few seconds ...')
            callback = lambda result: self.fetchImageDone(update, context, result)
            nbPhoto, searchType = getUserParam(context.user_data, ["NB_DISPLAYED_PHOTO", "SEARCH_TYPE"])
            print(nbPhoto)
            print(searchType)
            args = (search_text, nbPhoto, searchType)
            self.fetchImage_pool.apply_async(getImg.fetchQwantImages, args, callback=callback)
        else:
            update.message.reply_text('Not available')

    def fetchImageDone(self, update, context, result):
        for number, r in enumerate(result):
            update.message.reply_photo(photo=open('.'.join(r), 'rb'))
        # update.message.reply_text('Select one image to print', reply_markup=ReplyKeyboardMarkup([list(map(lambda x: '~'+str(x), range(len(result))))], one_time_keyboard=True))
        update.message.reply_text('Reply to one of the images with command /print')
        self.fileCreated.extend(result)
        self.state = AVAILABLE

    def selectPhoto(self, update, context):

        reply_keyboard = [['UII', 'NOO']]
        if(self.state == AVAILABLE):
            self.state = COMPUTING
            self.fileCreated.extend([["./image/" + str(int(time.time())), 'jpg']])
            photo_file = getPhoto(update)
            photo_file.download(".".join(self.fileCreated[-1]))

            self.fileCreated.extend(cvtImg.convertImageToSvg(self.fileCreated))
            self.fileCreated.extend(crtGc.writeGcode(self.fileCreated, [[self.fileCreated[-1][0], "gcode"]]))
            update.message.reply_document(document=open(".".join(self.fileCreated[-1]), 'rb'))
            update.message.reply_text('Select one image to print', reply_markup=ReplyKeyboardMarkup([["/print last"]], one_time_keyboard=True))
            self.state = AVAILABLE

        else:
            update.message.reply_text('Not available')

    def launchPrint(self, update, context):
        if(self.state == AVAILABLE):
            self.state = PRINTING
            self.fileCreated.extend([["./image/" + str(int(time.time())), 'gcode']])
            gcode_file = getGcode(update)
            gcode_file.download(".".join(self.fileCreated[-1]))
            args = (["/usr/bin/python3", self.STREAM, '.'.join(self.fileCreated[-1]), "/dev/ttyACM0"],)
            update.message.reply_text('Print running ...')
            callback = lambda result: self.printingDone(update, context, result)
            self.fetchImage_pool.apply_async(subprocess.call, args, callback=callback)
        else:
            update.message.reply_text('Not available')

        return ConversationHandler.END

    def printingDone(self, update, context, result):
        update.message.reply_text('Print done !')
        args = (['rm'] + list('.'.join(file) for file in self.fileCreated),)
        self.fetchImage_pool.apply_async(subprocess.call, args)
        self.fileCreated = []
        self.state = AVAILABLE

def start(self, update, context):
    update.message.reply_text(
        'Hi! My name is BoardPlotter Bot. I can draw whatever you want. '
        'Send /cancel to stop talking to me.\n\n'
        'What do you want me to draw?')
    # return KEYWORD

def getPhoto(update):
    if(update.message.reply_to_message):
        return update.message.reply_to_message.photo[-1].get_file()
    return update.message.photo[-1].get_file()

def getGcode(update):
    if(update.message.reply_to_message):
        return update.message.reply_to_message.document.get_file()
    return update.message.document.get_file()

def getUserParam(store, param):
    ret = []
    for p in param:
        ret.append(store.get(p, DEFAULT_SETTINGS[p]))
    return ret

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


def cancel(self, update, context):
    logger.warning("canceling%s", 'test')
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    myBot = DrawingTelegram()

    pp = PicklePersistence(filename='DrawingTelegram')
    updater = Updater(os.environ["TELEGRAM_TOKER"], persistence=pp, use_context=True)
    # print(pp.get_user_data())
        # for i in PicklePersistence(filename='DrawingTelegram').get_bot_data():

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states KEYWORD, SELECTPHOTO, LAUNCHPRINT and BIO

    dp.add_handler(CommandHandler("search", myBot.fetchImage,
                                  pass_args=True))

    dp.add_handler(MessageHandler((Filters.reply & Filters.regex('^\/gcode$')), myBot.selectPhoto))
    dp.add_handler(MessageHandler((Filters.photo & Filters.caption(["/gcode"])), myBot.selectPhoto))

    dp.add_handler(MessageHandler((Filters.reply & Filters.regex('^\/print$')), myBot.launchPrint))
    dp.add_handler(MessageHandler((Filters.photo & Filters.caption(["/print"])), myBot.launchPrint))

    conv_config = ConversationHandler(
        entry_points=[CommandHandler('config', config)],
        states={
            HOME: [ CallbackQueryHandler(chooseConfig, pattern='^'+ '|'.join(config_kw[:-1])+'$'),
                    CallbackQueryHandler(sumup, pattern='^'+ config_kw[-1] +'$')],
            SET: [ CallbackQueryHandler(setConfig)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )


    # dp.add_handler(conv_draw)
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
