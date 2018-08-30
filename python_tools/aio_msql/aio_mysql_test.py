# py3.5
#  主要是
import asyncio
import aiomysql

def aio_msql_batch_insert(self, db_config, values, loop, step=1, thread_num=30):
    """
    批量处理SQL 主要用于同步商城的产品，分类等数据
    :param db_config: 数据库配置
    :param values: 要执行的sql
    :param step: 步长 请勿随意更改会导致请求数据库异常
    :return:
    """
    asyncio.set_event_loop(loop)
    sem = asyncio.Semaphore(thread_num)
    tasks, erro_sql = [], []
    for sqls in self.env['jd.category'].chunks(values, 1):
        task = asyncio.ensure_future(self.go(loop, ';'.join(sqls) + ';', db_config, sem))
        tasks.append(task)
    loop.run_until_complete(asyncio.gather(*tasks))
    return values


async def go(self, loop, sql_str, db_config, sem):
    async with sem:
        pool = await aiomysql.create_pool(host=db_config[0], port=int(db_config[1]),
                                          user=db_config[2], password=db_config[3], db=db_config[4], loop=loop)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql_str)
                await conn.commit()
            await cur.close()
        pool.close()
        await pool.wait_closed()