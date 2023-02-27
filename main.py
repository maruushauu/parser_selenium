import time
import json
import datetime
import re
import sys
from db import DataBaseCommand
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
from configparser import ConfigParser
from func_res import *


config = ConfigParser()
config.read('/home/op/robots_config/config.ini')

page = 1
host = 'https://mosedo.mos.ru/'
driver = None
dnsid = None
login = None
password = None


def start(dates_proc:str):
    print(dates_proc)
    options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_settings.popups":0,
        "directory_upgrade": True,
        "extensions_to_open": "",
        "profile.default_content_settings_values.notifications": 2
    }
    options.add_argument("disable-infobars")
    options.add_argument("disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("disable-loging")
    options.add_argument('--disable-notifications')
    options.add_argument('start-maximized')
    options.add_experimental_option("prefs", prefs)

    capabilities = {
        "browserName": "chrome",
        "version": config['selenoid']['version'],
        "selenoid:options": {
            "enableVNC": True,
            "name": f"Обработка док-ов за {dates_proc}",
            "enableVideo": False
        }
    }
    driver, wait = driver_begin(capabilities, options)
    status_auth = None
    
    if login(driver, wait):
        status_auth = True
        return driver, wait, status_auth #! Возвращаем статус того,что авторизация прошла успешно
    else:
        print('Error loging')
        status_auth = False
        return driver, wait, status_auth #!

def driver_begin(capabilities, options):
    tries = 0
    while tries < 3:
        try:
            driver = webdriver.Remote(
                command_executor = config['selenoid']['prod'],
                desired_capabilities = capabilities,
                options = options)
            wait = lambda conditions, timeout=5: WebDriverWait(driver, timeout).until(conditions)
            break
        except Exception as e:
            print(e)
            tries += 1
    return driver, wait


def login(driver, wait): #? Объеденить в одну функцию по авторизации
    for i in range(3):
        try:
            set_organization(driver, wait)
            return True
        except Exception as e:
            print(e)
            if i < 2:
                continue
            print(Exception('NoSuchUserExeption'))
            return False


    # def clear(driver, wait, dates_proc, edo_double_card=None): 
    #     driver.find_element(By.XPATH, f"//i[@id='organization_clear']").click()
    #     driver.find_element(By.ID, 'password_input').clear()
    #     set_organization(driver, wait, dates_proc, edo_double_card=None, organization="Комитет по архитектуре и градостроительству города Москвы")

def set_organization(driver, wait, organization="Комитет по архитектуре и градостроительству города Москвы"):
    driver.get(host)
    wait(EC.element_to_be_clickable((By.ID, 'organizations'))).click()
    driver.find_element(By.ID, 'organizations').send_keys(organization)
    wait(EC.presence_of_element_located((By.XPATH, f"//a[.='{organization}']"))).click()
    wait(EC.invisibility_of_element_located((By.XPATH, f"//a[.='{organization}']")))

    driver.find_element(By.ID, 'logins').send_keys(config['mosedo_elma']['login'])
    wait(EC.presence_of_element_located((By.XPATH, f"//a[.='{config['mosedo_elma']['login']}']")), 3).click()
    wait(EC.invisibility_of_element_located((By.XPATH, f"//a[.='{config['mosedo_elma']['login']}']")), 3)
    wait(EC.element_to_be_clickable((By.ID, 'password_input'))).click()
    driver.find_element(By.ID, 'password_input').send_keys(config['mosedo_elma']['password'])

    try:
        driver.find_element(By.XPATH, "//input[@value='Войти']").click()
        try:
            wait(EC.element_to_be_clickable((By.XPATH, "//a[@class='change-skin-href' and @data-href-to='old']")), 3).click()
        except:
            wait(EC.element_to_be_clickable((By.XPATH, "//a[@class='change-skin-href' and @data-href-to='modern']")), 3)
    except Exception as e:
        print(e)
    

def close_window(driver):
    try:
        driver.find_element(By.XPATH,"//div[@class='s-urgent__body']//h1[contains(.,'Срочный документ')]")
        driver.find_element(By.XPATH,"//div[@class='s-urgent__body']//input[@value='Закрыть']").click()
    except:
        pass


def big_search(driver, wait, dates_proc, edo_double_card=None):
    try:
        driver.find_element(By.XPATH,".//li[@class='sd-tab__title']/a").click()
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@id='check_all_documents']").click()   # нажимаем 2 раза на Категории документов
        close_window(driver)
        time.sleep(0.5)
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@id='check_all_documents']").click()

        driver.find_element(By.XPATH,".//td[@class='b7']/input[@name='type_0']").click()          # Вх.
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@name='type_2']").click()          # Вх.Обр. гр.
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@name='type_12']").click()         # Вх.Обр. ПОС
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@name='has_period']").click()      # снять период
        driver.find_element(By.XPATH,".//td[@class='b7']/input[@name='search_wrap']").click()     # без подсчета кол-ва рез.
        if edo_double_card == None:
            element = driver.find_element(By.XPATH,".//span[@class='doc-search-input doc-search-input-period']/input[@id='rdate_f']") # вводим дату(неделя)
            element.clear()
            element.send_keys(dates_proc)
            element_two = driver.find_element(By.XPATH,".//span[@class='doc-search-input doc-search-input-period']/input[@id='rdate_t']") # до периода
            element_two.clear()
            element_two.send_keys(dates_proc)
            #! Поиск по номеру документа
            driver.find_element(By.XPATH,"//td[contains(.,'Входящий №:')]/following-sibling::td/span[@class='doc-search-input']/input")#.send_keys('МКА-81-7/22')  #.! 
        else:
            #? для скрипта record_db_to_whhom() и record_main()
            driver.find_element(By.XPATH,".//li[@class='sd-tab__title']/a").click()
            driver.find_element(By.XPATH,"//td[contains(.,'Входящий №:')]/following-sibling::td/span[@class='doc-search-input']/input").send_keys(edo_double_card)        
            driver.find_element(By.XPATH,"//button[@class='search__button search__button--blue']").click()  # кнопка "найти
            return driver, wait         
        driver.find_element(By.XPATH,"//button[@class='search__button search__button--blue']").click()   # кнопка "найти
    except Exception as e:
        print(e)
    return driver, wait
    
      
def next_edo_page(driver, wait, page, edo_double_card):
    try:
        if page == None:
            page = 2
        driver.switch_to.window(driver.window_handles[0])
        while True:
            try:
                if page != 1:
                    wait(EC.element_to_be_clickable((By.XPATH, f"//span[@class='s-pager__pages']/a[@data-n={page}]")), 10).click() 
            except Exception as e:
                print(e)
                break
            page += 1
            test_nik(driver, wait, page, edo_double_card)
    except Exception as e:
        print(e)
    return driver, wait


def test_nik(driver, wait, page=None, edo_double_card=None):
    
    database_command = DataBaseCommand() 
    database_command.connect() 
    
    #? Проверка , на наличие списка из ссылок карточек(для главного скрипта)
    #? обработка случая,если список из карточек пустой - выходные дни
    if edo_double_card == None:
        try:
            try:
                wait(EC.presence_of_element_located((By.XPATH, '//tr//td[4]/a')))
            except Exception as e:
                print(e)
                pass
            list_edo_card = driver.find_elements(By.XPATH, '//tr//td[4]/a')
        except:
            list_edo_card = None
        if len(list_edo_card) == 0:
            return driver, wait
    else:
        list_edo_card = edo_double_card
    
             
    #? НОМЕР КАРТОЧКИ ДОКУМЕНТА
    num_card_now = None    
        
    for edo_card in list_edo_card:
        
        #? для случая record_db_to_whhom() и record_main()
        if edo_double_card != None :
            #? достаем номер карточки edo_num
            num_card_now = list_edo_card
            try:
                element = driver.find_element(By.XPATH, f'.//div[@class="s-table__clamping main_doc_table-doc-number"]/b[@class="num-hyphens"]')
                element.click()
                #? в случае,если нет карточки,то закрываем driver
            except:
                # driver.close()
                return driver

        #? для main скрипта
        else:
            num_card_now = edo_card.find_element(By.XPATH,'.//div[@class="s-table__clamping main_doc_table-doc-number"]/b[@class="num-hyphens"]').text
            driver.switch_to.window(driver.window_handles[0])
            driver.execute_script(f"window.open('{edo_card.get_attribute('href')}')")
            driver.switch_to.window(driver.window_handles[1])
        

        #! проверка на дубли + на пустоту
        if edo_double_card is None:
            if database_command.has_number_in_db(num_card_now):
                continue
        
        data_list_card = []
        data_itog = {}
        close_window(driver)
        #! -- выполняем insert номера карточки в БД - чтобы зарезервировать карточку для одного потока
        try:
            if edo_double_card is None:
                new_card_id = database_command.edo_init_card(num_card_now)
            else:
                new_card_id = database_command.db_num(num_card_now)
                new_card_id = new_card_id[0]
        except Exception as e:
            print(e)
        #!

        data_dict_card = dict()
        wait(EC.element_to_be_clickable((By.XPATH, "//div[@class='action-panel-container']/a[contains(.,'Вернуться назад')]")), 3)

        num_edo_cd = driver.find_element(By.XPATH, '//td[contains(.,"Входящий №")]/following-sibling::td/span').text 
        data_dict_card['num_edo'] = num_edo_cd.split(' ')[0]
        aw = driver.find_element(By.XPATH, '//td[contains(.,"Дата регистрации")]/following-sibling::td/span').text
        aw = aw.replace('.','-')
        data_dict_card['num_date_reg'] = datetime.datetime.strptime( aw, "%d-%m-%Y").strftime('%Y-%m-%d')

        data_dict_card['num_to_whom'] = driver.find_element(By.XPATH, '//td[contains(.,"Кому")]/following-sibling::td/span').text
        try:
            data_dict_card['num_number'] = driver.find_element(By.XPATH, '//td[contains(.,"На №:")]/following-sibling::td').text
        except:
            data_dict_card['num_number'] = None
        try:
            data_dict_card['num_link_to_document'] = driver.find_element(By.XPATH, '//td[contains(.,"На документ ссылаются:")]/following-sibling::td').text
        except:
            data_dict_card['num_link_to_document'] = None
        try:
            data_dict_card['num_doc_number'] = driver.find_element(By.XPATH, '//td[contains(.,"№ документа:")]/following-sibling::td').text
        except:
            data_dict_card['num_doc_number'] = None

        try:
            wr = driver.find_element(By.XPATH, '//td[contains(.,"Дата документа:")]/following-sibling::td/span').text
            wr = wr.replace('.','-')
            data_dict_card['num_doc_date'] = datetime.datetime.strptime( wr, "%d-%m-%Y").strftime('%Y-%m-%d')
        except:
            еw = driver.find_element(By.XPATH, '//td[contains(.,"Дата регистрации")]/following-sibling::td/span').text
            еw = aw.replace('.','-')
            data_dict_card['num_doc_date'] = datetime.datetime.strptime( еw, "%d-%m-%Y").strftime('%Y-%m-%d')

        try:
            data_dict_card['num_from_whom'] = driver.find_element(By.XPATH, '//td[contains(.,"От кого:")]/following-sibling::td/span').text
        except:
            data_dict_card['num_from_whom'] = None
        try:
            data_dict_card['num_ispol'] = driver.find_element(By.XPATH, '//td[contains(.,"Исполнитель:")]/following-sibling::td').text
        except:
            data_dict_card['num_ispol'] = None
        try:
            data_dict_card['num_status_doc'] = driver.find_element(By.XPATH, '//td[contains(.,"Статус документа")]/following-sibling::td/span').text
        except:
            data_dict_card['num_status_doc'] = None
        try:
            all_list_doc = driver.find_element(By.XPATH, '//td[contains(.,"Кол-во листов, прил., экз.:")]/following-sibling::td/span').text
            all_list_doc = all_list_doc.split('+')
            sum_list = 0
            for list_d in  all_list_doc:
                sum_list += int(list_d)
            data_dict_card['num_list_number'] = sum_list
        except:
            data_dict_card['num_list_number'] = '0'
        
        data_dict_card['num_type_of_doc'] = driver.find_element(By.XPATH, '//td[contains(.,"Вид документа:")]/following-sibling::td/span').text
        try:
            data_dict_card['num_type_of_delivery'] = driver.find_element(By.XPATH, '//td[contains(.,"Вид доставки:")]/following-sibling::td/span').text
        except:
            data_dict_card['num_type_of_delivery'] = None
        try:
            data_dict_card['num_type_of_doc_special'] = driver.find_element(By.XPATH, '//td[contains(.,"Вид документа по особым признакам:")]/following-sibling::td').text
        except:
            data_dict_card['num_type_of_doc_special'] = None
        try:
            data_dict_card['num_place_thirst_reg'] = driver.find_element(By.XPATH,  '//td[contains(.,"Место первичной регистрации:")]/following-sibling::td/span').text
        except:
            data_dict_card['num_place_thirst_reg'] = None
        try:
            data_dict_card['num_content'] = driver.find_element(By.XPATH, '//td[contains(.,"Краткое содержание:")]/following-sibling::td').text.replace('\n','')
        except:
            data_dict_card['num_content'] = None
        try:
            data_dict_card['num_tematic'] = driver.find_element(By.XPATH, '//td[contains(.,"Тематика")]/following-sibling::td').text
        except:
            data_dict_card['num_tematic'] = None
        try:
            data_dict_card['num_express'] = driver.find_element(By.XPATH, '//td[contains(.,"Срочный:")]/following-sibling::td/div/span').text
        except:
            data_dict_card['num_express'] = None
        data_dict_card['num_note'] = driver.find_element(By.XPATH, '//td[contains(.,"Примечание:")]/following-sibling::td').text.replace('\n','')

        list_usr_signed = driver.find_elements(By.XPATH,'//div[@class="resolution-item__main-content"]')
        data_list_res = list()
        for usr_sign in list_usr_signed:
            try:
                usr_sign.find_element(By.XPATH,".//div[@class='resolution-item__vzamen']").text
                continue
            except:
                pass
            try:
                usr_sign.find_element(By.XPATH,".//span[@class='resolution-item__prefix' and contains(.,'Направление документа. ')]").text
                blu_res = blu_card(usr_sign, driver, wait)
                data_list_res.append(blu_res)
            except Exception as e:
                print(e)
            try:
                usr_sign.find_element(By.XPATH,".//span[@class='resolution-item__prefix' and contains(.,'ИСП:')]")
                green_res = green_card(usr_sign, driver, wait)
                data_list_res.append(green_res)
            except Exception as e:
                print(e)
                pass
            try:
                status_res_vzamen = True if len(usr_sign.find_elements(By.XPATH,".//div[@class='resolution-item__vzamen resolution-item__vzamen--forward']")) else False
                usr_info_edo = usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author-info"]')
                ActionChains(driver).move_to_element(usr_info_edo).perform()
                usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author-info"]').text
                if status_res_vzamen:
                    yellow_res_vzamen = yellow_card_vzamen(usr_sign, driver, wait)
                    data_list_res.append(yellow_res_vzamen)
                else:
                    yellow_res = yellow_card(usr_sign, driver, wait)
                    data_list_res.append(yellow_res)
            except Exception as e:
                print(e)
                pass
            #!#!#!#!#!#!     
            try:
                for res in data_list_res:
                    for resoled_person in res['resolve']:
                        if edo_double_card is not None:
                            #? проверка на пустые карточки,чтобы не возникало дублей в резалюции
                            if database_command.res_db_record(resoled_person, res, new_card_id):
                                continue   
                        database_command.res_card(
                            new_card_id,
                            res['type_of_res'],
                            res['from_name'],
                            res['author'],
                            resoled_person['fio'],
                            resoled_person['srok'],
                            resoled_person['sign_plus'],
                            res['date'],
                            resoled_person['text'])  
                #!#!#!#!#!#!
                data_list_card.append(data_dict_card)
                data_itog["num_edo"] = {'card': data_dict_card,
                            'res' : data_list_res}
                res['resolve'] = []
            except Exception as e:
                print(e)
            # with open(f'./jsons/{data_dict_card["num_edo"].replace("/", "-")}.json', 'w', encoding='utf8') as outfile:   # записывает каждую карточку 
            #     json.dump(data_itog, outfile, ensure_ascii=False)
        new_card_id = database_command.edo_card(data_dict_card, new_card_id)

        #? для main скрипта
        if edo_double_card == None:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
                   
    #? для record_db_to_whom() и record_main()          
    if edo_double_card != None:
        # driver.close()
        return driver    
    
    #? для main скрипта
    next_edo_page(driver, wait, page, edo_double_card)

def close_driver(driver):
    driver.close()
    driver.quit()

