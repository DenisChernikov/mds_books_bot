import re
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
    
    class Meta:
        database = db
        
print(re.search('(.*)\.', text).group(1))
print(re.search('\.\ (.*)', text).group(1))

for book in Books.select().where(Books.author == None):
    text = str(book.name)
    print(text)
    book.author = re.search('(.*)\.', text).group(1)
    book.book_name = re.search('\.\ (.*)', text).group(1)
    book.save()