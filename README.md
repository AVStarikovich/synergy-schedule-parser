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

Установим пакеты `datetime` и `dateutil`

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
