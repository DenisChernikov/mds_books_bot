#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# MDS
# Создан с помощью библиотеки https://github.com/python-telegram-bot/python-telegram-bot

# Импортируем модули
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

import logging
import functools
import re
import ast
from dwn import (mds_fm, mds_fm_dwn)
from user_dwn import user_send
from telethon_dwn import telethon_send
import os
from settings import token
import random

from urllib.request import (urlretrieve, urlopen)

from peewee import *

db = SqliteDatabase('mds.db')

class Users(Model):
    chat_id = IntegerField()
    nickname = CharField(max_length = 255)
    first_name = CharField(max_length = 255)
    last_name = CharField(max_length = 255)
    send = CharField(max_length = 255)
    
    class Meta:
        database = db
        
class Books(Model):
    download = CharField(max_length = 255)
    name = CharField(max_length = 255)
    mds_fm_link = CharField(max_length = 255)
    mds_club_link = CharField(max_length = 255)
    file_id = CharField(max_length = 65025)
    
    class Meta:
        database = db
    
MENU, SEARCH, SEND, PARSE = range(4)

# Активируем logging
logging.basicConfig(format='%(asctime)s -%(name)s -%(levelname)s -%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def check_user(func):
    logger = logging.getLogger(func.__module__)
    @functools.wraps(func) #используем декоратор function.wraps для копирования информации об оборачиваемой функции
    def check(*args, **kwargs):
        logger.info('Entering: {}'.format(func.__name__))
        bot, update = args
        for a in args:
            logger.info(a)        
        user = Users.get(chat_id=update.message.chat_id)
        kwargs['user'] = user
        result = func(*args, **kwargs)
        logger.info('Exiting: {}'.format(func.__name__))
        return result
    return check


@check_user
def send_me_book(bot, update, **kwargs):
    user = kwargs['user']
    reply_keyboard = [['Следующая']]
    table = []
    try:
        for book in Books.select().where(Books.file_id == '50mb '):
            table.append(book.download)
        book_download = random.choice(table)
        user.send = book_download
        user.save()
    
        book = Books.get(download=book_download)
        links = mds_fm_dwn(book.mds_fm_link)
        #for link in links:
            #print("downloading with urllib")
            #file_name = "send/{}.mp3".format(book.name)
            #urlretrieve(book.mds_fm_link, file_name)
        update.message.reply_text('Пожалуйста, пришлите мне следующую книгу:\n{}\n{}\n{}'.format(book_download, book.name, book.mds_fm_link), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
        
    except:
        update.message.reply_text('Книги для закачки закончились')
    
    return SEND

@check_user
def parse_audio(bot, update, **kwargs):
    user = kwargs['user']
    reply_keyboard = [['Следующая']]
    book_file_id = update.message.audio.file_id
    book = Books.get(download=user.send)
    
    update.message.reply_text('Отлично, я записал в ячейку эту книгу:\nfile_id:\n{}\nID: {}\nНазвание: {}\n'.format(book_file_id, book.download, book.name), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    book.file_id = book_file_id + ' '
    book.save()
        
    return PARSE

@check_user
def check_books(bot, update, **kwargs):
    user = kwargs['user']
    reply_keyboard = [['Следующая']]
    text = ''
    table = []
    for book in Books.select().where(Books.file_id > 6):
        table.append([book.file_id, book.name, book.description])
    
    
    
    book_file_id = random.choice(table)
    for fileid in book_file_id[0].split(' '):
            try:
                message = bot.send_audio(chat_id=user.chat_id, audio=fileid, timeout=1000, caption=book_file_id[1])
                print(bot.send_audio.__sizeof__)
            except: #убираем конечный пустой файл таким топорным способом
                pass
    if book_file_id[2] != None:
        update.message.reply_text(book_file_id[2])
    
    update.message.reply_text('Отлично, я записал в ячейку эту книгу:\nfile_id:\n{}\nID: {}\nНазвание: {}\n'.format(book_file_id, book.download, book.name), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    book.file_id = book_file_id + ' '
    book.save()
        
    return PARSE   

def error(bot, update, error):
    logger.warning('Update "{}" caused error "{}"'.format(update, error))

def main():
    updater = Updater(token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('send', send_me_book)],
        
        states = {
            SEND: [MessageHandler(Filters.audio, parse_audio),
                   MessageHandler(Filters.text, send_me_book),
                   ],
            PARSE: [MessageHandler(Filters.text, send_me_book),
                   ],
                     
        },
        
        fallbacks = [CommandHandler('cancel', send_me_book)]
        
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()