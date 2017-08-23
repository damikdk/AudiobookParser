import re
import urllib.request as urllib
import ssl
from peewee import *
import os.path


db = SqliteDatabase('audiobooks.db')
books = ['https://knigavuhe.ru/book/alkhimik/',
         'https://knigavuhe.ru/book/veronika-reshaet-umeret/',
         'https://knigavuhe.ru/book/pobeditel-ostaetsja-odin/',
         'https://knigavuhe.ru/book/german-ili-bozhijj-chelovek/',
         'https://knigavuhe.ru/book/na-beregu-rio-pedra-sela-ja-i-zaplakala/',
         'https://knigavuhe.ru/book/poslednijj-bojj-majjora-pettigrju/',
         'https://knigavuhe.ru/book/nezaveshhannoe-nasledstvo-pasternak-mravinskijj-efremov-i-drugie/',
         'https://knigavuhe.ru/book/vedma/',
         'https://knigavuhe.ru/book/tajozhnyjj-tupik/',
         'https://knigavuhe.ru/book/minin-i-pozharskijj/',]

def create_tables():
    db.connect()
    db.create_tables([Author, Book])

class Author(Model):
    id = IntegerField(primary_key=True, unique=True)
    name = CharField(max_length=30, null=True)
    booksCount = IntegerField(default=0)
    page = CharField(max_length=30, null=True)

    class Meta:
        database = db

class Book(Model):
    id = IntegerField(primary_key=True, unique=True)
    title = CharField(max_length=30)
    creator = ForeignKeyField(Author, related_name='books', null=True)
    page = CharField(max_length=30, null=True)
    description = CharField(max_length=300, null=True)
    genre = CharField(max_length=30, null=True)

    class Meta:
        database = db


def files_from_url(url):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = r"https:\\\\/\\\\/f[0-9]*.knigavuhe.ru[\W]+audio[\W]+[0-9]+[\W]+.{0,30}.mp3"

    if len(re.findall('book_blocked', str(html))) > 0:
        print('Доступ к аудиокниге ограничен по просьбе правообладателя')
        return

    founded = re.findall(URL_REGEX, str(html))

    for index, link in enumerate(founded):
        founded[index] = valid_link_to_file(link)

    #print(founded)


def authors_from_url(url):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = "author/[A-Za-z_-]+/"

    founded = re.findall(URL_REGEX, str(html))

    for index, link in enumerate(founded):
        author = link.split('/')[1]
        try:
            Author.get(name=author, page=valid_link_to(link))
        except DoesNotExist:
            Author.create(name=author, page=valid_link_to(link))

        books_from_author(valid_link_to(link))
        founded[index] = valid_link_to(link)

    print(founded)


def authors_from_site():
    for i in range(1, 98):
        authors_from_url('https://knigavuhe.ru/authors/' + str(i) + '/')


def books_from_page(url):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = "book/[A-Za-z_-]+/"

    founded = re.findall(URL_REGEX, str(html))
    founded = set(founded)

    for index, link in enumerate(founded):
        book = link.split('/')[1]
        try:
            Book.get(title=book, page=valid_link_to(link))
        except DoesNotExist:
            Book.create(title=book, page=valid_link_to(link))

    print(founded)


def books_from_author(url):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = "author/[A-Za-z_-]+/[0-9/]*"

    founded = re.findall(URL_REGEX, str(html))
    founded = set(founded)
    print(founded)

    for index, pageLink in enumerate(founded):
        books_from_page(valid_link_to(pageLink))

def valid_link_to_file(row):
    return row.replace(r'\\/', '/')
def valid_link_to(row):
    return 'https://knigavuhe.ru/' + str(row)


# if os.path.isfile('audiobooks.db'):
#     os.remove('audiobooks.db')
#
# create_tables()