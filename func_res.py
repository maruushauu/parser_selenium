from func import Func
import datetime
import re
from selenium.webdriver.common.by import By


def yellow_card_vzamen(usr_sign, driver, wait):
    try:
        text_w = None
        ter = None
        res = {
                "from_name": None,
                "author": None,
                "date": None,
                'type_of_res': 'yellow',
                "resolve": []
            }
        res['author'] = usr_sign.find_element(By.XPATH,'.//div[@class="resolution-item__vzamen resolution-item__vzamen--forward"]').text
        res['from_name'] = usr_sign.find_element(By.XPATH,'.//div[@class="resolution-item__behalf resolution-item__row"]').text
        ast = str(usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author-info"]').text).split()[-1].replace(']', '').split('):')[0]
        ast = ast.replace('.','-')
        res['date'] = datetime.datetime.strptime( ast, "%d-%m-%Y").strftime('%Y-%m-%d')
        to_usr_reason = usr_sign.find_element(By.XPATH,'.//div[@class="resolution-item__row"]/span[@axuiuserid]/parent::div').text.split('\n')
        for reason in to_usr_reason: 
            if 'срок исполнения' in reason.lower() or 'на контроле' in reason.lower():
                continue
            if '- ' not in reason:
                res['resolve'] = only_autors(usr_sign, reason, driver, wait)
            reason_pod = str(reason).split(' - ')
            if len(reason_pod) == 3:
                if res['resolve'] != None:
                    tree_el = tree_element(reason_pod, reason, usr_sign, ter, text_w, driver, wait)
                    name_resolve(res['resolve'], tree_el, driver, wait)
                else:
                    res['resolve'] = tree_element(reason_pod, reason, usr_sign, ter, text_w, driver, wait)
            if len(reason_pod) == 2:
                res['resolve'].extend(two_element(usr_sign, reason, reason_pod, driver, wait))
                if 'Подведомственным организациям' in reason_pod[0]:
                    text_w = reason_pod[1].strip()
                    ter = True
        return res
    except Exception as e:
        print(e)


def blu_card(usr_sign, driver, wait):
    try:
        test_func = Func(driver, wait)
        res = {
                "from_name": None,
                "author": None,
                "date": None,
                'type_of_res': 'blue',
                "resolve": []
            }
        #! создаем в ключе "resolve_to" массив из словарей с каждой фамилией, на кого расписана резолюция 
        author_from = usr_sign.find_elements(By.XPATH, './/span[contains(.,"От кого: ")]/following-sibling::span')[0].text
        if '/' in author_from:
            test = str(author_from).split('/')
            res['from_name'] = test[0].strip()
            res['author'] = test[1].strip()
        else:
            res['from_name'] = author_from
        wwy = str(str(usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__timestamp"]').text).split(',')[-1]).split(']')[0].split('):')[0].strip()
        wwy = wwy.split(' ')[0]
        wwy = wwy.replace('.','-')
        res['date'] = datetime.datetime.strptime( wwy, "%d-%m-%Y").strftime('%Y-%m-%d')

        to_user_napr = usr_sign.find_elements(By.XPATH, './/div[@class="resolution-item__orders-wrapper"]/div/span')
        for user_napr in to_user_napr:
            name = None
            #! создаем макет словаря, задаем дефолтные значения
            resolve_to = {
                "fio": None,
                "srok": None,
                "text": None,
                "sign_plus": False
                }
            if 'кому:' in user_napr.text.lower() or '- 'in user_napr.text.lower():
                continue
            #! функция для определении фамилии в Начальной форме,возвращаем fio автора
            #! общаемся к обьекту класса func
            if '+' not in user_napr.text:
                #! делаем проверку на список,кому направлена резолюция
                name = re.findall(r'\w+ \w\.\w\.', user_napr.text)
                if len(name) == 0:
                    continue 
                resolve_to['fio'] = test_func.flow_wind(user_napr)
                #!
                if '-' in usr_sign.find_element(By.XPATH, './/div[@class="resolution-item__orders-wrapper"]').text:
                    try:
                        napr_text = str(usr_sign.find_element(By.XPATH, './/div[@class="resolution-item__row"]').text).split('- ')[1]
                        resolve_to['text'] = napr_text
                        if '+' in napr_text:
                            resolve_to['text'] = napr_text.split('+')[0]
                    except:
                        resolve_to['text'] = None
                res['resolve'].append(resolve_to)
            else:
                user_plus = usr_sign.find_element(By.XPATH, './/div[@class="resolution-item__orders-wrapper"]').text
                if '+' in user_plus:
                    #! определяем + в списке авторов -- user_plus
                    fur = test_func.fio_plus(usr_sign, user_plus)
                    for fu in fur:
                        resolve_to['fio'] = fu
                        resolve_to['sign_plus'] = True
                res['resolve'].append(resolve_to)  
                #! в словарь res добавляем как ключ 'resolve' - список с вложенными словарями 'resolve_to'
        return res
    except Exception as e:
        print(e)

    
def green_card(usr_sign, driver, wait):
    try:
        res = {
                "from_name": None,
                "author": None,
                "date": None,
                'type_of_res': 'green',
                "resolve": []
            }
        
        resolve_to = {
                "fio": None,
                "srok": None,
                "text": None,
                "sign_plus": False
                }

        author_from = usr_sign.find_elements(By.XPATH, './/span[contains(.,"ИСП: ")]/following-sibling::span')[0].text
        if '/' in author_from:
            test = str(author_from).split('/')
            res['from_name'] = test[0].strip()
            res['author'] = test[1].strip()
            resolve_to['fio'] = test[0].strip()
        else:
            res['from_name'] = author_from
            resolve_to['fio'] = author_from
        try:
            tmp_text = usr_sign.find_element(By.XPATH, './/div[@class="resolution-item__row resolution-item__row--text"]').text
            resolve_to['text'] = tmp_text
        except:
            tmp_text = None
        tou = str(str(usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__timestamp"]').text).split(',')[-1]).split(']')[0].split('):')[0].strip()
        tou = tou.split(' ')[0]
        tou = tou.replace('.','-')
        res['date'] = datetime.datetime.strptime( tou, "%d-%m-%Y").strftime('%Y-%m-%d')
        res['resolve'].append(resolve_to)    
        return res
    except Exception as e:
        print(e)

        

def yellow_card(usr_sign, driver, wait):
    try:
        ter = None
        text_w = None
        res = {
                "from_name": None,
                "author": None,
                "date": None,
                'type_of_res': 'yellow',
                "resolve": []
            }
        author_from = usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author"]').text
        if '/' in author_from:
            test = str(author_from).split('/')
            res['from_name'] = test[0].strip()
            res['author'] = test[1].strip()
        else:
            res['author'] = usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author"]').text
        tre = str(usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author-info"]').text).split()[-1].replace(']', '').split('):')[0]
        tre = tre.replace('.','-')
        res['date'] = datetime.datetime.strptime( tre, "%d-%m-%Y").strftime('%Y-%m-%d')
        try:
            res['from_name'] = usr_sign.find_element(By.XPATH,'.//div[@class="resolution-item__behalf resolution-item__row"]').text
        except:
            res['from_name'] = usr_sign.find_element(By.XPATH,'.//span[@class="resolution-item__author"]').text
        to_usr_reason = []
        try:
            to_usr_reason = usr_sign.find_element(By.XPATH,'.//div[@class="resolution-item__orders-wrapper"]//span[@axuiuserid]/parent::div/parent::div').text.split('\n')
        except:
            pass
        #! для обработки резолюции с мобильной версии
        if len(to_usr_reason) == 0:
            resolve_to = {
                "fio": None,
                "srok": None,
                "text": None,
                "sign_plus": False
                }
            res['resolve'].append(resolve_to)
            return res
        else:
            for idx, reason in enumerate(to_usr_reason):
                text_fio = re.findall(r'[А-Я][а-я]+ [А-Я]\.[А-Я]\.', reason)
                if len(text_fio) == 0:
                    continue
                if 'срок исполнения' in reason.lower() or 'на контроле' in reason.lower():
                    continue
                if '- ' not in reason:
                    res['resolve'] = only_autors(usr_sign, reason, driver, wait)
                    continue
                prov = re.search(r'\- \w{4}\: \d{2}.\d{2}.\d{4} \- ',reason)
                reason_pod = str(reason).split(' - ')
                if prov and prov[0] in reason:
                    if res['resolve'] != None:
                        tree_el = tree_element(reason_pod, reason, usr_sign, ter, text_w, driver, wait)
                        name_resolve(res['resolve'], tree_el, driver, wait)
                    else:
                        res['resolve'] = tree_element(reason_pod, reason, usr_sign, ter, text_w, driver, wait)
                else:
                    tww = two_element(usr_sign, reason, reason_pod, driver, wait)
                    if idx+1 < len(to_usr_reason):
                        reas = to_usr_reason[idx +1]
                        text_fio = re.findall(r'[А-Я][а-я]+ [А-Я]\.[А-Я]\.', reas)
                        if 'Срок исполнения:' in reas or 'На контроле:' in reas:
                            pass
                        else:
                            if len(text_fio) == 0:
                                for el in tww:
                                    el['text'] = el['text'] + reas
                    res['resolve'].extend(tww)
                    if 'Подведомственным организациям' in reason_pod[0]:
                        text_w = reason_pod[1].strip()
                        ter = True
            return res
    except Exception as e:
        print(e)

# nres['fio'] - новый словарь
# res['fio'] - старый словарь
# проверка на наличие fio в словарях
def name_resolve(resolve, new_res, driver, wait):
    try:
        for nres in new_res:
            is_updated = False
            for res in resolve:
                if nres['fio'] == res['fio']:
                    is_updated = True
                    resolve = res
                    new_res = nres
                    resolve.update(new_res) # метод update  просто перезаписывает новый словарь поверх старого -- применяется для словарей
                    break
            if not is_updated:
                pass
    except Exception as e:
        print(e)



def only_autors(usr_sign, reason, driver, wait):
    try:
        test_func = Func(driver, wait)
        aut = []
        for raw in usr_sign.find_elements(By.XPATH, ".//div[@class='resolution-item__row']/span"):
            if '+' in raw.text:
                plus = test_func.fio_plus(usr_sign, raw.text)
                for fo in plus:#!
                    test = {
                        'sign_plus': True,
                        'fio': fo,
                        'srok': None,
                        'text': None
                        }
                    aut.append(test)   
            else:
                test = {
                'sign_plus': False,
                'fio': test_func.flow_wind(raw),
                'srok': None,
                'text': None
                }
                aut.append(test)     
        return aut
    except Exception as e:
        print(e)


def tree_element(reason_pod, reason, usr_sign, ter, text_w, driver, wait):
    try:
        if 'до 15-00' in reason_pod[1]:
            srok = reason_pod[2].split(' ')
            srok = srok[0].replace(' ','')
            srok = srok.replace('.','-')
            srok = datetime.datetime.strptime(srok, "%d-%m-%Y").strftime('%Y-%m-%d')
        else:
            srok = reason_pod[1].split(': ')[-1].replace(' ','')
            srok = srok.replace('.','-')
            srok = datetime.datetime.strptime(srok, "%d-%m-%Y").strftime('%Y-%m-%d')
        test_func = Func(driver, wait)
        author_tree = []
        rawfio = reason_pod[0].strip()
        author_tree.append({
                'sign_plus': False,
                'fio': rawfio,
                'srok': srok
            })
        
        if '+' in reason:
            plus = test_func.fio_plus(usr_sign, reason)
            for f in plus:#!
                author_tree.append({
                    'sign_plus': True,
                    'fio': f
                })
        return author_tree
    except Exception as e:
        print(e)


def two_element(usr_sign, reason, reason_pod, driver, wait):
    try:
        author_two = []
        fio_res = None
        test_func = Func(driver, wait)
        # сплитим по первому дефису
        reason_pod = reason.split('-', 1)
        text_plus = re.findall(r'\w+ \+ \w+', reason_pod[1])
        if len(text_plus) != 0:
            text = reason_pod[1].strip()
        else:
            if '+' in reason_pod[1]:
                text =  reason_pod[1].split('+')
                text = text[0].strip()
            else:
                text = reason_pod[1].strip()
        try:
            if 'Подведомственным организациям' in reason_pod[0]:
                reason_p = reason_pod[0].split(' Подведомственным организациям')
                fiom = reason_p[0]
            else:
                fiom = reason_pod[0]
        except Exception as e:
            print(e) 
        fio_res = fiom.split(',')
        for fio in fio_res:
            name = re.findall(r'\w+ \w\.\w\.', fio)
            if len(name) == 0:
                continue  
            fio = fio.replace(',', '')
            fio = fio.split(' (')[0]
            try:
                if 'Начальникам УГР' in fio:
                    continue
            except Exception as e:
                print(e)
            fio = fio.strip()
            rawfio = usr_sign.find_element(By.XPATH, f".//div[@class='resolution-item__orders-wrapper']//span[contains(., '{fio}')]")
            author_two.append({
                'sign_plus': False,
                'fio': test_func.flow_wind(rawfio),
                'text': text,
                'srok': None
            })

        if '+' in reason_pod[1]:
            text_plus = re.findall(r'\w+ \+ \w+', reason_pod[1])
            if len(text_plus) != 0:
                pass
            else:
                plus = test_func.fio_plus(usr_sign, reason_pod[1])
                for f in plus:#!
                    author_two.append({
                        'sign_plus': True,
                        'fio': f,
                        'text': text,
                        'srok': None
                    })            
        return author_two
    except Exception as e:
        print(e)








