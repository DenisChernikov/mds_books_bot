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
import random
from settings import token
ls = '0123456789'

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
    author = CharField(max_length = 255)
    book_name = CharField(max_length = 255)
    description = TextField()
    
    class Meta:
        database = db
    
MENU, SEARCH, SEND = range(3)

start_again = 'Вы можете ввести название или автора следующей книги сразу же, или, если вам так приятнее, начать с начала\n/start'

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


def start(bot, update, **kwargs):
    #reply_keyboard = [['Лучшее', 'Поиск по автору'], ['Поиск по названию', 'Помочь проекту']]
    reply_keyboard = [['Случайная книга']]
    
    try:
        user = Users.get(chat_id=update.message.chat_id)
    except:
        user = Users.create(chat_id=update.message.chat_id, nickname=update.message.from_user.username, first_name=update.message.from_user.first_name, last_name=update.message.from_user.last_name)
    
    update.message.reply_text('Привет, {}, я @mds_books_bot, введите название или автора книги, и я найду её для вас в базе. Если я туплю при ответе, значит, скорее всего, я качаю кому-то книгу)\nГруппа для вопросов, пожеланий, обратной связи: t.me/joinchat/B845txIb0XXSAS8ZLQiFPg\n(<b>Я буду очень признателен за замечания в работе бота</b>)\nВсего книг проекта "Модель для сборки": ~2300\nКниг, которые попали в поиск: 885\nИмеющихся в базе бота: 225\nТакже вы можете выбрать случайную книгу из базы бота /random и посмотреть все книги, которые есть в базе /all_books'.format(user.first_name), reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True), parse_mode='html')
    #ll = ast.literal_eval('http://d.mds-fm.ru/2007/7/2004-03-04. %d0%a5%d1%83%d0%bb%d0%b8%d0%be %d0%9a%d0%be%d1%80%d1%82%d0%b0%d1%81%d0%b0%d1%80. %d0%90%d0%b2%d1%82%d0%be%d0%b1%d1%83%d1%81.mp3')
    #bot.send_audio(chat_id=user.chat_id, audio='http://d.mds-fm.ru/2007/10/2005-06-27.%20Гарри%20Гаррисон.%20Жизнь художника.mp3', timeout=1000)
    return MENU

@check_user
def random_book(bot, update, **kwargs):
    user = kwargs['user']
    table = []
    for book in Books.select().where(Books.file_id > 6):
        table.append([book.file_id, book.name, book.description])
    book_file_id = random.choice(table)
    for fileid in book_file_id[0].split(' '):
            try:
                message = bot.send_audio(chat_id=user.chat_id, audio=fileid, timeout=1000, caption=book_file_id[1])
            except: #убираем конечный пустой файл таким топорным способом
                pass
    if book_file_id[2] != None:
        update.message.reply_text(book_file_id[2])
    reply_keyboard = [['Случайная книга']]
    update.message.reply_text('Ещё одна случайная книга /random Начать сначала /start', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

@check_user
def best(bot, update, **kwargs):
    user = kwargs['user']
    
    search = update.message.text
    
    reply_keyboard = [['Вернуться в начало']]
    update.message.reply_text('Здесь пока ничего нет, но скоро будет', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

@check_user
def author(bot, update, **kwargs):
    user = kwargs['user']
    
    search = update.message.text
    
    reply_keyboard = [['Вернуться в начало']]
    update.message.reply_text('Здесь пока ничего нет, но скоро будет', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

@check_user
def name(bot, update, **kwargs):
    user = kwargs['user']
    
    search = update.message.text
    
    reply_keyboard = [['Вернуться в начало']]
    update.message.reply_text('Здесь пока ничего нет, но скоро будет', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

@check_user
def donate(bot, update, **kwargs):
    user = kwargs['user']
    
    search = update.message.text
    
    reply_keyboard = [['Вернуться в начало']]
    update.message.reply_text('Здесь пока ничего нет, но скоро будет', reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    return MENU

@check_user
def search_all(bot, update, **kwargs):
    reply_keyboard = [['Случайная книга']]
    update.message.reply_text('Поиск книг займёт небольшое время, пожалуйста, подождите')
    try:
        table = mds_fm(update.message.text)
        text = ''
        for i in table:
            try:
                new_book = Books.get(mds_fm_link=i[1])
            except:
                new_book = Books.create(download=''.join([random.choice(ls) for x in range(6)]), name=i[0], mds_fm_link=i[1])
                new_book.save()
            links = mds_fm_dwn(i[1])
            size = ''
            for link in links:
                size += str(round(float(urlopen(link).headers['content-length'])/1048576, 1)) + 'мб '
            text += '{}\n/download{} - {}\n'.format(new_book.name, new_book.download, size)
        if text == '':
            text = 'К сожалению, ничего не найдено(\n'
        update.message.reply_text(text + start_again, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    except:
        #for book in Books.select().where((Books.file_id > 6) | (re.search(update.message.text, Books.author).group(0) != '') | (re.search(update.message.text, Books.book_name).group(0) != '')):
        #    print(book.name)
        text = 'К сожалению, в данный момент сервер с загружаемыми книгами недоступен(\nНо не расстраивайтесь, вы можете:\nПослушать случайную книгу из списка уже загруженных /random\nПосмотреть все книги, имеющиеся в базе у бота /all_books'
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))
    
    return SEARCH

@check_user
def all_books(bot, update, **kwargs):
    reply_keyboard = [['Случайная книга']]
    user = kwargs['user']
    table = []
    for book in Books.select().where(Books.file_id > 6):
        table.append([book.download, book.author, book.book_name])
    for i in range(0, len(table), 30):
        text = ''
        for k in range(30):
            try:
                text += '{}. {}\n/download{}\n'.format(table[i+k][1], table[i+k][2], table[i+k][0])
            except:
                pass
        update.message.reply_text(text)
    update.message.reply_text(start_again, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True))    
    return MENU
    
@check_user
def download(bot, update, **kwargs):
    user = kwargs['user']
    search = re.search('\d+', update.message.text).group(0)
    new_book = Books.get(download=search)
    if not new_book.file_id:
        result_link = Books.get(download=search).mds_fm_link
        links = mds_fm_dwn(result_link)
        counter = 0
        file_id = ''
        for link in links:
            try:
                message = bot.send_audio(chat_id=user.chat_id, audio=link, timeout=1000, caption=new_book.name)
            except:
                if int(urlopen(link).headers['content-length']) > 52428800:
                    #bot.sendMessage(chat_id=468240823, text='Please download this book for me:\n{}'.format(link))
                    #print("downloading with urllib")
                    #file_name = "temp/{}_{}.mp3".format(new_book.name, counter)
                    #urlretrieve(link, file_name)
                    #hm = telethon_send(file_name, new_book.name)
                    update.message.reply_text('Эта аудиокнига больше 50мб, у телеграма есть ограничение на отправку аудиофайлов такого размера через бота, попробуйте пока другую книгу или скачайте её по ссылке:\n{}'.format(link))
                    file_id += '50mb '
                    #bot.send_audio(chat_id=user.chat_id, audio=fileid, timeout=1000, caption=new_book.name)
                else:
                    update.message.reply_text('Похоже, эта аудиокнига загружается впервые, мне нужно загрузить её на сервер, чтобы после отправить Вам, это может занять некоторое время. Зато в следующий раз она придёт мгновенно)')
                    try:
                        print("downloading with urllib")
                        file_name = "temp/{}_{}.mp3".format(new_book.name, counter)
                        urlretrieve(link, file_name)
                        message = bot.send_audio(chat_id=user.chat_id, audio=open(file_name, 'rb'), timeout=9999)
                        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
                        os.remove(path)
                        counter += 1
                    except:
                        update.message.reply_text('Ошибка при загрузке файла из интернета, разработчик уже поправляет) Попробуйте ещё раз другую книгу')
            try:
                file_id += '{} '.format(message.audio.file_id)
            except:
                pass
        new_book.file_id = file_id
        new_book.save()
    else:
        for fileid in new_book.file_id.split(' '):
            try:
                message = bot.send_audio(chat_id=user.chat_id, audio=fileid, timeout=1000, caption=new_book.name)
            except: #убираем конечный пустой файл таким топорным способом
                pass
    update.message.reply_text(start_again)
    return SEARCH

def error(bot, update, error):
    logger.warning('Update "{}" caused error "{}"'.format(update, error))

def main():
    updater = Updater(token, request_kwargs={'proxy_url': 'socks5://163.172.152.192:1080'})

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start), MessageHandler(Filters.text, start)],
        
        states = {
            MENU: [CommandHandler('start', start),
                   RegexHandler('^/download', download),
                   RegexHandler('^(Случайная книга$|/random)', random_book),
                   RegexHandler('^(Все книги$|/all_books)', all_books),
                   RegexHandler('^Лучшее$', best),
                   RegexHandler('^Поиск по автору$', author),
                   RegexHandler('^Поиск по названию$', name),
                   RegexHandler('^Помочь разработчику$', donate),
                   MessageHandler(Filters.text, search_all),],
            SEARCH: [CommandHandler('start', start),
                     RegexHandler('^/download', download),
                     RegexHandler('^(Случайная книга$|/random)', random_book),
                     RegexHandler('^(Все книги$|/all_books)', all_books),
                     RegexHandler('^Ничего не найдено$', start),
                     MessageHandler(Filters.text, search_all),],
            SEND: [CommandHandler('start', start),
                   RegexHandler('^/download', download),
                   RegexHandler('^(Случайная книга$|/random)', random_book),
                   RegexHandler('^(Все книги$|/all_books)', all_books),
                   RegexHandler('^Ничего не найдено$', start),
                   MessageHandler(Filters.text, search_all),],
                     
        },
        
        fallbacks = [CommandHandler('cancel', start)]
        
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()