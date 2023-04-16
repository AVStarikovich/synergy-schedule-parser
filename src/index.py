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