import re  # библиотечка для работы с регулярными выражениями
import urllib.request as urllib  # библиотечка для работы с сетью. Даю ей ссылку, а он отдает мне html страницу
import ssl  # библиотечка для работы с защищенным соединением (https). Сайт наш как его и использует
from peewee import *  # библиотечка для работы с базой данных. создает ее и позволяет немного абстрагироваться от таблиц
import os.path  #  это часть пайтона, для работы с системой. Я тут ее использую чтобы файлы удалять

db = SqliteDatabase('audiobooks.db')  # db теперь это база данных с таким названием, чуть позже создадим файл

# все, что начинается с def - функции. Просто их описание, они не работают, пока их не вызвать.
# вызываю я в самом конце файла. Поэтому когда будешь читать код в следующий раз - он читается по ходу выполнения.


# это описание модельки базы данных
# каждый атрибут (поле) в конце концов станет столбиком в таблице авторов
# но для нас это нужно, потому что ORM. Object-Relational Mapping, объектно-реляционное отображение.
# мы не работаем с таблицами, мы работаем с объектами, с абстракцией над таблицами.
class Author(Model):
    id = IntegerField(primary_key=True, unique=True)  # поле с id, Integer - целочисленное, unique - для каждого должен быть уникальный
    name = CharField(max_length=30, null=True)  # поле с имя, Char - символьное, null - поле может быть пустым
    booksCount = IntegerField(default=0)
    page = CharField(max_length=30, null=True)

    class Meta:
        database = db  # это какая то метаинформация, видимо для привязки к конкретной базе данных


# по прежнему, просто описание, мы еще ничего не делаем
class Book(Model):
    id = IntegerField(primary_key=True, unique=True)
    title = CharField(max_length=30)
    creator = ForeignKeyField(Author, related_name='books', null=True)  # ForeignKey значит, что поле ссылается на объект из другой таблицы.
                                                                        # Book.creator это не символ, не строка и не число. Это объект Author
    page = CharField(max_length=30, null=True)
    description = CharField(max_length=300, null=True)
    genre = CharField(max_length=30, null=True)

    class Meta:
        database = db


#  функция, которая создает базу данных. Когда вызывем ее.
def create_tables():
    db.connect()
    db.create_tables([Author, Book])  # вот тут вроде создается файл audiobooks.db, прямо в папке проекта


#  функция принимает ссылку, находит все ссылки файлов на странице, но ничо не делает.
def files_from_url(url):
    context = ssl._create_unverified_context()  # забей, это для того, чтобы работать с https
    response = urllib.urlopen(url, context=context) # urlopen(url) идет по данной ссылке и возвращает страницу (и еще статусы)
    html = response.read() # взяли response и положили в переменную html. Это просто огромная строка со всей html страницей

    # В данной строке функция находит все, что подошло по данному шаблону и возвращает это массивом.
    if len(re.findall('book_blocked', str(html))) > 0:
     # len(                                     ) определяет длину обьекта. Для строки определит количество символов, для массива количество элементов.
     #     re.findall('что ищу',      гдеищу   )  re это библиотечка, смотри импорты. у нее есть метод (функция) findall(шаблон, строка). Она вернет массив со всем, что подошло по шаблону
     #                                str(html) html вроде и так строка, но мы его на всякий случай превратим в строку.

        # в итоге мы посмотрели, есть ли на странице строка 'book_blocked'. Она есть где то на странице, если книга заблокирована
        print('Доступ к аудиокниге ограничен по просьбе правообладателя')
        return # это остановит выполнение функции.

    # Если книга заблокирована, то мы здесь не можем оказаться. Функция закончила выполнение на return.
    URL_REGEX = r"https:\\/\\/f[0-9]*.knigavuhe.ru[\W]+audio[\W]+[0-9]+[\W]+.{0,30}.mp3"  # регулярное выражение/шаблон

    founded = re.findall(URL_REGEX, str(html.decode('utf-8')))    # founded это теперь массив со всеми ссылками.
    # html.decode('utf-8') здесь, потому что в другой (первоначальной) кодировке слэши дублируются (хз почему). Мы сменили кодировку на UTF-8

    # enumerate(массив) делает массив итерабельным. Это отдельно можешь почитать, можешь забить.
    for index, link in enumerate(founded):
        founded[index] = valid_link_to_file(link)  # у нас сейчас ссылки в гавноформате (https:\/\/f.knigavuhe.ru),
                                                   # поэтому используем функцию valid_link_to_file(link). Иди смотри ее
        # в итоге мы проходим по всем элементам массива (строки с ссылками) и меняем их на валидные ссылки. Если не понимаешь - забей

    print(founded)  # просто выводим результат, ничо не делаем, ничо не возвращаем.

# принимает строку
def valid_link_to_file(str):
        return str.replace(r'\/', '/')  # тупо заменяем \/ на / и возвращаем нормальную рабочую ссылку


# берет строку ссылку на страницу с авторами (https://knigavuhe.ru/authors/, например), скачивает страницу,
# находит на странице все ссылки на авторов, пишет авторов в базу данных
def authors_from_url(url):
    context = ssl._create_unverified_context()  # вот эти три строки просто глазами пропускай везде
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = "author/[A-Za-z_-]+/"  # шаблон

    founded = re.findall(URL_REGEX, str(html))  # массив со строками формата 'author/tolstoy'

    for index, link in enumerate(founded):
        author = link.split('/')[1]  # link это строка 'author/tolstoy'
                                     # str.split('разделитель') разбивает строку по данной строке.
                                     # Нашу строку он разделит по слэшу и вернет массив с двумя строками - 'author' и 'tolstoy'. Мы берем первый (а не нулевой) элемент.
                                     # Это и есть наш автор. Правда на транслите, но хоть как то

        # try пробует что-то сделать, если получает определенную ошибку - мы можем принять меры
        try:
            Author.get(name=author, page=valid_link_to(link))  # пробуем получить из базы данных автора 'tolstoy' с такой же ссылкой на страницу
        except DoesNotExist:                                   # если код сверху упадет с ошибкой "Нет такого обьекта!", то создаем нового автора
            Author.create(name=author, page=valid_link_to(link))

        founded[index] = valid_link_to(link)

        # ну все, записали автора в таблицу. Тут все заканчивалось раньше, но теперь я беру ссылку https://knigavuhe.ru/author/lev-tolstojj/
        # и ищу все книги этого автора

        books_from_author(valid_link_to(link))  # го в эту функцию

    # это был цикл, для всех авторов на странице https://knigavuhe.ru/authors/
    print(founded)


# проходит по всем 98 страницам списка авторов (https://knigavuhe.ru/authors/42/) и запускает функцию authors_from_url(url)
def authors_from_site():
    for i in range(1, 98):
        authors_from_url('https://knigavuhe.ru/authors/' + str(i) + '/')


# делает то же, что и authors_from_url(), только с книгами
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


# на странице автора есть многостраничный список с его книгами (https://knigavuhe.ru/author/lev-tolstojj/, https://knigavuhe.ru/author/lev-tolstojj/2/)
# функция на странице автора (https://knigavuhe.ru/author/lev-tolstojj/) находит ссылки на все эти страницы и вызывает books_from_page(url)
def books_from_author(url):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(url, context=context)
    html = response.read()

    URL_REGEX = "author/[A-Za-z_-]+/[0-9/]*"

    founded = re.findall(URL_REGEX, str(html))
    founded = set(founded)
    print(founded)

    for pageLink in founded:
        books_from_page(valid_link_to(pageLink))


def valid_bookname_from_url_with_name(page, name):
    context = ssl._create_unverified_context()
    response = urllib.urlopen(page, context=context)
    html = response.read()

    URL_REGEX = r"book_title_name\">[\w]+<"

    founded = re.findall(URL_REGEX, str(html.decode('utf-8')))
    founded = set(founded)
    print(founded)

    for index, link in enumerate(founded):
        bookName = link[:-1].split('>')[1]
        try:
            Book.get(title=name, page=page)
        except DoesNotExist:
            Book.create(title=name, page=page)


def valid_link_to(row):
    return 'https://knigavuhe.ru/' + str(row)


# ВОТ ТУТ НАЧИНАЕТСЯ ЗАПУСК КОДА!!!!!!!!!!!!!!!!

# if os.path.isfile('audiobooks.db'):          # если база данных уже есть, удаляет ее
#     os.remove('audiobooks.db')
#
# create_tables()                              # создает новую


# вот маленький виновник всего кода вообще.
# Он проходит по списку авторов, заходит в список книг автора и проходит по всем его книгам.
# Вот одна строчка вызывает цепочку других, в итоге это 15 минут работает. (98 страниц с авторами, 50 авторов на каждой, по паре книг у каждого в среднем)
# 4900 запросов по сети
# 12639 книг спаршено
authors_from_site()
