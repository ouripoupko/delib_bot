import psycopg2
import os

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#    cur = conn.cursor()
#    cur.execute("""SELECT * from topics""")
#    rows = cur.fetchall()

class DB:

    def __init__(self, table_name):
        self.cursor = conn.cursor()
        self.table_name = table_name

    def Write(self, fields):
        header = ', '.join(fields.keys())
        values = ', '.join(fields.values())
        self.cursor.execute('INSERT INTO {} ({}) VALUES ({});'.format(self.table_name, header, values))
        conn.commit()

    def Read(self, fields):
        where = ' AND '.join(['{} = {}'.format(k,v) for k, v in fields.items()])
        self.cursor.execute('SELECT * FROM {} WHERE {};'.format(self.table_name, where))
        res = self.cursor.fetchall()
        return res[0][0]

