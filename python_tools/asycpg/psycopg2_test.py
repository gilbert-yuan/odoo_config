import psycopg2
import datetime

begin_date = datetime.datetime.now()

for i in range(10):
    conn = psycopg2.connect("dbname=zhengshi user=yuan password=qq111111")
    cur = conn.cursor()
    cur.execute("SELECT * FROM sale_order")
    orders = cur.fetchall()
    conn.close()

for order in orders:
    print(order)
print(begin_date)
print(len(orders))
print(datetime.datetime.now())