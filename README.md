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
