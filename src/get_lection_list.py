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