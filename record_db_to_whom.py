from db import *
from main import *


database_command = DataBaseCommand()
database_command.connect()


#?  Сделать проверку на наличие карточки в БД, у которой в res_card -> to_whom = None
def res_to_whon_None():
    database_command.cur.execute(f"""select res_card.id as id, edo_card.num_edo as num_edo
    from res_card
    Inner join edo_card ON res_card.id_card = edo_card.id
    where  res_card.to_whom = 'None'
    """)
    edo_num = database_command.cur.fetchall()
    #? вернет список, внитри которого словарь         
    if len(edo_num)>0:        
        return edo_num
    return None


#! нужно подставлять в id - id from res_card
#? удаляем резолюции    
def delete_rows_res(id_res_unick):
    database_command.cur.execute(f"""delete from res_card
    where to_whom = 'None' and id = {id_res_unick}
    """)
    database_command.conn.commit()
        
 

    
    

    



    
    
    
    
    
   
