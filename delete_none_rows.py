from db import DBase, DataBaseCommand

database_command = DataBaseCommand() 
database_command.connect()


#? скрипт для очистки дублирующих карточек из edo_card

database_command.cur.execute("""SELECT num_edo, count(num_edo)
from edo_card
GROUP by num_edo
having count(num_edo) > 1
""")
num_edo_list = database_command.cur.fetchall()


id_list = []
for num in num_edo_list:
    database_command.cur.execute(f"""SELECT id 
    from edo_card
    where num_edo like '%{num[0]}%'
    """)
    id_edo = database_command.cur.fetchall() 
    for i in id_edo:
        id_list.append(list(i))
    
    
for el in id_list:
    database_command.cur.execute(f"""delete from res_card
    where id_card = {el[0]}
    """)
    database_command.conn.commit()
    
    database_command.cur.execute(f"""delete from edo_card
    where id = {el[0]}
    """)
    database_command.conn.commit()
