# 1. РАЗВЕРТЫВАНИЕ ПРОЕКТА

## 1.1 Устанавливаем python, pip, pipenv.

Как это делать описано в этом гайде https://docs.python-guide.org/dev/virtualenvs/

`pip` это менеджер пакетов, с его помощью мы будем устанавливать нужные нам пакеты, нужных версий.

`pipenv` это cli для работы с проектами, с помощью него мы будем запускать наш проект в нужном окружении.

## 1.2. Создаем проект.

```bash
mkdir sinergy-schedule-parser # создаем папку с проектом
cd sinergy-schedule-parser # заходим в нее
pipenv install requests # ставим пакет requests
```

После установки пакета `requests` у нас автоматически должен был создаться `Pipfile`, в нем хранится информация о окружении, в котором будет запускаться наш код.

Так же должен был автоматически создаться `Pipfile.lock`, в нем записаны версии пакетов, которые мы используем, и версии пакетов, пакетов которые мы используем.

## 1.3. Пишем первый код

Создаем папку `src`. Там будут храниться исходники нашей программы.
Внутри нее создаем файл `index.py` с таким содержимым:

```python
import requests

def handler():
    print('requesting synergy site page...')

    # делаем GET запрос по адресу synergy.ru, используя HTTPS протокол
    response = requests.get('https://synergy.ru')

    # проверяем статус ответа (в случае успеха должен быть 200)
    if response.status_code != 200:
        print('request failed with code: ', response.status_code)

    print('success!')
    print('page html code:')
    # выводим в косоль содержание ответа
    print(response.content)

# вызываем функцию handler() при вызове файла
if __name__ == '__main__':
    handler()
```

## 1.4. Настраиваем окружение для удобной работы и проверяем его работу

Добавим в `Pipfile` новый скрипт. Он нужен для удобного запуска нашего кода.

```Pipfile
[scripts]
start = "python src/index.py"
```

Запускаем наш код командой `pipenv run start`.
Если все сделано правильно, то в консоле мы должны увидеть html-код страницы `synergy.ru`

# 2. Получение страницы с расписанием

## 2.1. Создание переменных окружения с секретами для авторизации на сайте

Создадим в корне проекта файл `.local.env` с таким содержимым:

```
LMS_USERNAME="твой_логин_здесь"
LMS_PASSWORD="твой_пароль_здесь"
```

При старте кода, `pipenv` автоматически прочитает этот файл, что позволит нам получить указанные здесь значения в коде:

```python
os.getenv('LMS_USERNAME')
```

Мы не добавили наши "секреты" в код, поскольку это считается плохой практикой. Потому что обычно код хранится в репозиториях, соответственно, если хранить "секреты" в коде, то их сможет прочитать любой, кто имеет доступ к репозиторию.

Но мы же все равно записали наши секреты, просто не в код, а рядом в файл. Так вот, для того чтобы этот файл не попал в репозиторий заигнорим его. Для этого в корне проекта нужно создать вот такой файл `.gitignore`:

```
*.env
```

`*.env` это маска файла которая говорит о том, что все файлы, имена которых заканчиваются на `.env` должны быть проигнорированы и не выгружены в репозиторий.

## 2.2. Определение окна расписания для запроса

Установим пакеты `datetime` и `dateutil`.

```bash
pipenv install datetime
pipenv install python-dateutil
```

Перепишем код в `index.py` на такой:

```python
from datetime import datetime
from dateutil.relativedelta import relativedelta
from get_schedule_html import get_schedule_html

def handler():
    # вычисляем начало текущего дня (на компьютере)
    fromDate = datetime.today().replace(hour = 0, minute = 0)
    # вычисляем конец дня ровно через месяц от текущего
    toDate = (datetime.today() + relativedelta(months = 1)).replace(hour = 23, minute = 59)

    # запрашиваем html-код страницы расписания в выбранном окне
    schedule_html = get_schedule_html(fromDate, toDate)

    print(schedule_html)

# вызываем функцию handler() при вызове файла
if __name__ == '__main__':
    handler()
```

## 2.3. Запрашиваем страницу с расписанием

Создадим в папке `src` файл `get_schedule_html.py` с таким содержимым:

```python
import requests
import os
from datetime import date

def get_schedule_html(fromDate: date, toDate: date):
    # создаем сессию, поскольку для того чтобы запросить страницу с расписанием
    # нужно быть авторизованным
    s = requests.Session()

    print('logining...')

    # этот запрос не лишний, он нужен из-за внутреней логики сервера lms
    s.get('https://lms.synergy.ru/ping/?status=1')
    # заходим на страницу lms
    s.get('https://lms.synergy.ru/')
    # отправляем запрос на авторизацию
    # (он отправляется страницей), когда мы заполняем форму и жмем кнопку "войти"
    s.post(
        url = 'https://lms.synergy.ru/user/login',
        data = {
            # подставляем значения, которые указали в файле .local.env
            'popupUsername': os.getenv('LMS_USERNAME'),
            'popupPassword': os.getenv('LMS_PASSWORD'),
            'currentUrl': '',
            'popupRemember': '',
        }
    )

    print('logined sucessfully')

    # отправляем запрос с настройкой окна расписания
    # (этот запрос отправляется, когда мы на странице расписания указываем его окно)
    s.post(url = 'https://lms.synergy.ru/schedule/academ', data = {
        'mySchedule': 1,
        'employee': 1,
        'group': '',
        'discipline': '',
        'time_check': 1,
        'discipline_check': 1,
        'place_check': 1,
        'type_check': 1,
        'teacher_check': 1,
        'dateFrom': fromDate.strftime("%d.%m.%Y"),
        'dateTo': toDate.strftime("%d.%m.%Y"),
        'doSrch': 1
    })

    # запрашиваем страницу с расписанием
    return s.get('https://lms.synergy.ru/schedule/academ').text
```

Если все сделано правильно, то после выполнения команды `pipenv run start` в консоле должен появиться код страницы с расписанием на ближайший месяц.

# 3. Получение списка занятий

## 3.1. Парсинг строчек с расписанием

Установим пакет `bs4`:

```bash
pipenv install bs4
```

Создадим файл `get_lection_list.py` в папке `src` с таким содержимым:

```python
from datetime import datetime, date, timedelta
from typing import List
from bs4 import BeautifulSoup, Tag
from get_schedule_html import get_schedule_html

# парсим строки с датой и временем и получаем экземпляр класса datetime
def parse_date(date, time):
    # разбиваем строку на массив значений и берем первые два элемента как часы и минуты
    hours, minutes = time.split(':')
    # разбиваем строку на массив значений и берем первые три элемента как день, месяц и год
    day, month, year= date.split('.')

    # создаем экземпляр класса datetime
    return datetime(2000 + int(year), int(month), int(day), int(hours), int(minutes))


class Lection:
    # объявляем конструктор класса Lection
    def __init__(self, datePreview: str, timeInterval: str, lectionName: str, place: str, lectionType: str, teacher: str):
        # достаем из времени расписания дату путем разбивания строки по запятой на масив значений
        # и запоминания первого элемента
        date, _ = datePreview.split(', ')

        # если в "столбце" времени занятия есть " - ", то значит что это интервал занятия
        if " - " in timeInterval:
            # извлекаем из него время начала и конца, путем разбивания строки на массив значений
            timeFrom, timeTo = timeInterval.split(' - ')

            # заполняем в экземпляре класса Lection время начала и окончания занятия
            self.dateFrom = parse_date(date, timeFrom)
            self.dateTo = parse_date(date, timeTo)
        else:
            # когда пришел не интервал, а только одно значение
            timeFrom = timeInterval

            # заполняем в экземпляре класса Lection время начала и окончания занятия
            self.dateFrom = parse_date(date, timeFrom)
            self.dateTo = parse_date(date, timeFrom) + timedelta(minutes= 45)

        # заполняем в экземпляре класса Lection название, помещение, тип и преподавателя
        self.lectionName = lectionName
        self.place = place
        self.lectionType = lectionType
        self.teacher = teacher

    # если мы попытаемся прокинуть экземпляр класса Lection в метод print()
    # то для того чтобы получить его строковое представление, движок питона вызовет этот метод
    def __str__(self):
        # выводим строчку со значениями лекции
        # датой в формате день.меся.год
        # временем в формате часы:минуты
        # и остальной информацией

        # здесь мы используем шаблонные строки, для компоновки данных в строку
        return f'{self.dateFrom.strftime("%d.%m.%y %a")} {self.dateFrom.strftime("%H:%M")} - {self.dateTo.strftime("%H:%M")} {self.lectionName} ({self.lectionType}) {self.place} {self.teacher}'


# нормализуем содержимое тега и приводим его в строку со значениями
def parse_tag(tag: Tag):
    # split() разбивает исходную строку на массив значений
    # это нужно для того чтобы разом вычистить все лишние пробелы и табуляции
    # ' '.join() приводит массив значений в строку которая состоит из значений
    # разделенных пробелом
    return ' '.join(tag.text.split())


def html_to_lection_list(html: str):
    # создаем экземляр класса BeautifulSoup, в качестве аргумента
    # передавая html-код страницы с расписанием.
    soup = BeautifulSoup(html, 'html.parser')

    # библиотека BeautifulSoup позволяем извлекать нужные
    # данные из html-кода
    # здесь мы говорим что хотим извлечь все тэги <tr>,
    # которые лежат внутри любого тега с id="dictionaryTable"
    rows = soup.select('#dictionaryTable > tr')

    lastDatePreview = None
    lection_list: List[Lection] = []

    # проходимся по всем тегам <tr> что мы извлекли,
    # и парсим значение
    for row in rows:
        # парсим содержимое тега
        parsed_value_list = map(parse_tag, list(row.children))
        # выфильтровываем все пустые значения
        filtered_value_list = [child for child in parsed_value_list if child != '']

        if len(filtered_value_list) == 1:
            # если в строке только один "столбец" то это дата дня
            # запоминаем ее
            lastDatePreview = filtered_value_list[0]
        else:
            # если в строке не один "столбец" то это данные о занятии.
            # создаем экземпляр класса Lection на основе запомненной даты
            # и "сырой" информации о занятии
            # прокидываем в конструктор Lection дату и все "столбцы",
            # каждый отдельно, используя spread оператор *
            lection_list.append(Lection(lastDatePreview, *filtered_value_list))

    # сортируем список занятий по дате начала
    # в качестве ключа прокидываем лямбда (анонимную) функцию, которая
    # возвращает значение, по которому будет происходить сортировка
    lection_list.sort(key = lambda lection: lection.dateFrom)

    return lection_list


def get_lection_list(fromDate: date, toDate: date):
    # получаем html-код страницы с расписанием в выбранном окне
    html = get_schedule_html(fromDate, toDate)
    # получаем список занятий из html-кода страницы
    lection_list = html_to_lection_list(html)

    return lection_list
```

Перепишем код файла `index.py` на этот:

```python
from datetime import datetime
from dateutil.relativedelta import relativedelta
from get_lection_list import get_lection_list

def handler():
    # вычисляем начало текущего дня (на компьютере)
    fromDate = datetime.today().replace(hour = 0, minute = 0)
    # вычисляем конец дня ровно через месяц от текущего
    toDate = (datetime.today() + relativedelta(months = 1)).replace(hour = 23, minute = 59)

    # запрашиваем список занятий
    lection_list = get_lection_list(fromDate, toDate)

    print('schedule parsed:')
    # итерируемся по списку занятий и выводим его в консоль.
    # для того чтобы получить не только значения, но еще индекс
    # используем функцию enumerate(), которая оборачивает каждый
    # элемент массива в массив и первым элементом кладет в него индекс
    for index, item in enumerate(lection_list):
        print(f'{index + 1}. {item}')

# вызываем функцию handler() при вызове файла
if __name__ == '__main__':
    handler()
```

Если все сделано правильно, то при запуске кода в консоль выведется список занятий на ближайший месяц, похожий на этот:

```
1. 19.04.23 Wed 10:10 - 11:40 Командная работа и лидерство (зст) (Вебинар) 0 Машарина А.Ф.
2. 19.04.23 Wed 11:50 - 13:20 Командная работа и лидерство (л) (Вебинар) 0 Машарина А.Ф.
3. 20.04.23 Thu 13:50 - 15:20 Программирование на языке Python (лр) (Вебинар) 0 Терехова Л.А.
4. 20.04.23 Thu 15:30 - 17:00 Программирование на языке С++ (лр) (Вебинар) 0 Мастяев Ф.А.
5. 20.04.23 Thu 17:10 - 18:40 Программирование на языке С++ (л) (Вебинар) 0 Мастяев Ф.А.
```
