import re
import urllib.request as urllib
import ssl

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
        founded[index] = valid_link(link)

    print(founded)

def valid_link(row):
    valid = row.replace(r'\\/', '/')
    return valid

for book in books:
    files_from_url(book)
