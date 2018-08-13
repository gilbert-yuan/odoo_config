import asyncio
import random
from aiohttp import ClientSession
        
async def fetch(url, session):
    async with session.post(url) as response:
        response = await response.read()
        return response


async def bound_fetch(sem, url, session):
    # Getter function with semaphore.
    async with sem:
        result = await fetch(url, session)
        return result

async def run(r, future):
    url = "http://dtfg:8888/api/v1/order/S1807050441/money"
    tasks = []
    # create instance of Semaphore
    sem = asyncio.Semaphore(100)

    # Create client session that will ensure we dont open new connection
    # per each request.
    async with ClientSession() as session:
        for i in range(r):
            # pass Semaphore and session to every GET request
            task = asyncio.ensure_future(bound_fetch(sem, url.format(i), session))
            tasks.append(task)
        responses = asyncio.gather(*tasks)
        await responses
        future.set_result(responses.result())
        
if __name__ == '__main__':
    loop = asyncio.new_event_loop()    
    asyncio.set_event_loop(loop)
    future1 = asyncio.Future()
    asyncio.ensure_future(run(100, future1))
    loop.run_until_complete(asyncio.gather(future1))
    for r in future1.result():
        print(r)
    loop.close()

