from datetime import datetime
from sqlalchemy import types
import psycopg2



class DBase():
    def __init__(self):
        self.url = ''
        self.port = ''
        self.db = ''
        self.us = ''
        self.passw = ''
        self.conn = False
        self.cur = False

    
    def connect(self):   # почему параметры для подключению записываются через self ? #!
        if self.conn == False:
            self.conn = psycopg2.connect(
                host= self.url,
                port = self.port,
                database= self.db,
                user= self.us,
                password= self.passw)
            self.cur = self.conn.cursor()
        else:
            print('reconect')


class DataBaseCommand(DBase):
    def __init__(self):
        super().__init__()


#num_edo, num_date_reg, num_to_whom, num_link_to_document, num_doc_date, num_from_whom, num_ispol, num_status_doc, num_list_number, num_type_of_delivery, num_type_of_doc_special, num_place_thirst_reg, num_content, num_tematic, num_express, num_note, num_number, num_doc_number, num_type_of_doc

    #! проверка на наличие карточки,возвращает true/ false
    def has_number_in_db(self, edo_num):
        self.cur.execute(f"select num_edo from edo_card where num_edo = '{edo_num}'")
        card = self.cur.fetchone()
        return card is not None

    # #! проверка на наличие дублей в карточках, которые мы перезаписываем через record_main
    # def has_date_in_db(self, edo_num):
    #     self.cur.execute(f"select num_edo, date_reg from edo_card where num_edo = '{edo_num}' and date_reg is not Null")
    #     card_date = self.cur.fetchone()
    #     return card_date is not None


    def db_num(self, edo_num):
        self.cur.execute(f"select id from edo_card where num_edo = '{edo_num}'")
        id = self.cur.fetchone()
        return id

    #! записываем один номер в БД
    def edo_init_card(self, num_card_now):
        self.cur.execute(f""" insert into edo_card(num_edo)
        values('{num_card_now}')
        RETURNING id
        """)
        id_card = self.cur.fetchone()[0]
        self.conn.commit()
        return id_card

   
    def res_card(self,
        new_card_id,
        type_of_res,
        from_name,
        author,
        fio,
        srok,
        sign_plus,
        date,
        text 
        ):
        try:
            tmp_srok = f"'{srok}'" if srok else 'null'
            # fio = f"'{fio}'" if fio else 'null'
            self.cur.execute(f""" insert into res_card(id_card, type, from_name, author, to_whom, srok, sign_plus, date, text)
            values('{new_card_id}', '{type_of_res}', '{from_name}', '{author}','{fio}', {tmp_srok}, '{sign_plus}', '{date}', '{text}')
            """)
            self.conn.commit()
        except Exception as e:
            print(e)

    
    def edo_card(self, data_dict_card, id_card):
        print(data_dict_card)
        try:
            self.cur.execute(f""" update edo_card set
            date_reg = '{data_dict_card["num_date_reg"]}', 
            to_whom = '{data_dict_card["num_to_whom"]}',
            link_to_document = '{data_dict_card["num_link_to_document"]}',
            doc_date_rec = '{data_dict_card["num_doc_date"]}',
            from_whom = '{data_dict_card["num_from_whom"]}',
            ispol = '{data_dict_card["num_ispol"]}',
            status_doc = '{data_dict_card["num_status_doc"]}',
            list_number = '{data_dict_card["num_list_number"]}',
            type_of_delivery = '{data_dict_card["num_type_of_delivery"]}',
            type_of_doc_special = '{data_dict_card["num_type_of_doc_special"]}',
            place_first_reg = '{data_dict_card["num_place_thirst_reg"]}',
            content = '{data_dict_card["num_content"]}',
            tematic = '{data_dict_card["num_tematic"]}',
            express = '{data_dict_card["num_express"]}',
            note = '{data_dict_card["num_note"]}',
            to_number = '{data_dict_card["num_number"]}',
            doc_number_out = '{data_dict_card["num_doc_number"]}',
            type_of_number = '{data_dict_card["num_type_of_doc"]}'
            where id = {id_card}
            """)       
            self.conn.commit()
        except Exception as e:
            print(e)


    #! первый вызов функции проверка на пустые карточки
    def res_db_record(self, resoled_person, res, id):
        self.cur.execute(f"""select id
        from res_card
        where id_card = {id} and 
        type = '{res["type_of_res"]}' and
        to_whom = '{resoled_person["fio"]}' and 
        author = '{res["author"]}'
        """)
        num_res_record = self.cur.fetchall()
        if len(num_res_record)>0:        
            return True
        return False
    

        
