from main import start
from db import DBase, DataBaseCommand

database_command = DataBaseCommand() #! создали обьект для соединения с классом БД 
database_command.connect()


def card_record():
    database_command.cur.execute("""select num_edo
    from edo_card
    where date_reg is Null
    """)
    num_edo_record = database_command.cur.fetchall()
    if len(num_edo_record)>0:        
        return [num[0] for num in num_edo_record]
    return None

        


