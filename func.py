
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
import re

class Func():
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        

    def fio_plus(self, usr_sign=None, plt=None):
        pl = plt.replace('+', '+$')
        plus_pl = pl.split('+')
        list_fio = []
        for f in plus_pl:#!
            if '$' in f:
                f = f.replace(',', '').replace('$', '').strip()
                fi = usr_sign.find_element(By.XPATH, f".//div[@class='resolution-item__orders-wrapper']//span[contains(.,'{f}')]")
                list_fio.append(self.flow_wind(fi))
        return list_fio


    def flow_wind(self,fi):
        try:
            #! кликаем вниз 3 раза стрелкой 
            action = ActionChains(self.driver)
            action.move_to_element(self.driver.find_element(By.XPATH, "//a[@title='Вернуться на предыдущую страницу']"))
            action.move_to_element(self.driver.find_element(By.XPATH, "//parent::div/parent::div[@class='resolution-item__container']//a[contains(.,'Подробно')]"))
            action.scroll_to_element(fi)
            action.move_to_element(fi)
            action.perform()
            
            str_fio = self.wait(EC.visibility_of_element_located((By.XPATH, "//div[@id='user-info-popup']//div[contains(.,'ФИО:')]")), 20).text
            fio_reg = re.search(r'(?<=ФИО: )(?:[А-ЯЁ][а-яё]* ?){3}', str_fio)
            if fio_reg is None:
                fio_reg = re.search(r'(?<=ФИО: )[А-ЯЁ][а-яё]+\-(?:[А-ЯЁ][а-яё]+\s){2}[А-ЯЁ][а-яё]+', str_fio)
            fio_reg = fio_reg.group(0).split()
            fio_reg = f"{fio_reg[0]} {fio_reg[1][0]}.{fio_reg[2][0]}."
        except Exception as e:
            print(e)
        return fio_reg
      
