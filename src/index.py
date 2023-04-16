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