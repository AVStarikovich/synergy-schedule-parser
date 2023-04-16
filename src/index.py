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