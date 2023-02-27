from main import *
import datetime
from multiprocessing import Pool
from record_main import *
from record_db_to_whom import *


def start_main_script(dates_proc, edo_double_card=None):
    driver, wait, auth = start(dates_proc)
    if auth == True:
        big_search(driver, wait, dates_proc)
        test_nik(driver, wait, page=None)
    close_driver(driver)
    # res_card(driver, wait, list_edo_card, data_dict_card,  page=None, edo_double_card=None)

#! Для запуска в многопоточности:         
#!--1-- собрать текущие данные за рабочую неделю
date_to_start = datetime.datetime.now()
date_to_start = date_to_start.date()
weekday = date_to_start.isoweekday()
start_days = date_to_start - datetime.timedelta(days=weekday)
print(date_to_start.weekday())
dates = [(start_days + datetime.timedelta(days=d)).strftime("%d.%m.%Y") for d in range(weekday)] #strptime(dates, "d%.%m.%Y")
# dates = ['28.11.2022', '29.11.2022', '30.11.2022']


#!--2-- собрать данные за прошлый год
# date_to_start = datetime.datetime.now()
# days_list = []
# try:
#     while date_to_start < datetime.datetime(2023,1,13):
#         if date_to_start.weekday() is not 6 and date_to_start.weekday() is not 5:
#             days_list.append(date_to_start.strftime("%d.%m.%Y"))
#             date_to_start += datetime.timedelta(days=1)
#         else:
#             date_to_start += datetime.timedelta(days=1)
# except Exception as e:
#     print(e)


# date_to_start = date_to_start.replace(year=2021, month=1, day=13)
# # number_cards = database_command.card_record()
# tt = days_list[0].strftime("%d.%m.%Y")
# for i in range(1, 7): 
#     day = date_to_start + datetime.timedelta(days=i)
#     days_list.append(day.strftime('%Y-%m-%d')) 

#!--3-- собрать данные за одно число
# if '__name__'=='__main__':
# multiprocessing(dates[2])
# for date in dates:
#     multiprocessing(date)


if __name__ == '__main__':
    with Pool(processes=10) as pool:
        pool.starmap(start_main_script, [(days,) for days in dates]) 
    # for date in days_list:
    #     multiprocessing(date)
    # [start_main_script(days) for days in days_list]
          
    # restart_main = []
    # restart_main = None
    
    
    #! функция запроса в БД вохзвращает список из карточек,если длина>0  и None если 0
    restart_main = card_record()
    if restart_main:
        if len(restart_main) > 0:
            driver, wait, auth = start(dates_proc=None)
            if auth == True:
                for num in restart_main:
                    big_search(driver, wait, dates_proc=None, edo_double_card = num)
                    test_nik(driver, wait, page=None, edo_double_card = num)
            close_driver(driver)
                
        if len(restart_main) == 0:
            start_main_script(dates_proc=None, edo_double_card = None)
         
            
    restart_db_to_whom = res_to_whon_None()
    if restart_db_to_whom:
        driver, wait, auth = start(dates_proc=None)
        if auth == True:
            #? проходим циклом по каждому слемента из списка с кортежем , передаем элемент кортежа
            for num in restart_db_to_whom:
                driver, wait= big_search(driver, wait, dates_proc=None, edo_double_card = num[1])
                test_nik(driver, wait, edo_double_card=num[1])
                delete_rows_res(num[0])
        close_driver(driver)
    



