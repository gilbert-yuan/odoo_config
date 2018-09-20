import asyncio
import asyncpg
import datetime
async def run():
    conn = await asyncpg.connect(user='yuan', password='qq111111',
                                 database='zhengshi', host='127.0.0.1')
    values = await conn.fetch('''SELECT * FROM sale_order''')
    await conn.close()
    return values
begin_date = datetime.datetime.now()
loop = asyncio.get_event_loop()
orders = loop.run_until_complete(asyncio.gather(*[run() for i in range(10)]))
for order in orders:
    print(order)
print(begin_date)
print(len(orders))
print(datetime.datetime.now())
loop.close()
