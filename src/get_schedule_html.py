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