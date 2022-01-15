import asyncio
from pathlib import Path
import aiohttp
import requests


def very_simple_example():
    ero_url = "https://api.ixiaowai.cn/api/api.php?return=json"

    ss = requests.session()
    ret = ss.get(ero_url).json()
    pic = ss.get(ret["imgurl"]).content
    Path("/Graiax/EroEroBot/eropic.jpg").read_bytes(pic)


very_simple_example()


async def very_simple_example():
    ero_url = "https://api.ixiaowai.cn/api/api.php?return=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json()
        async with session.get(ret["imgurl"]) as r:
            pic = await r.read()

    # 将二进制数据储存在这里面
    Path("bugmaker\\eropic.jpg").read_bytes(pic)


asyncio.run(very_simple_example())


async def func1(arg1, arg2):
    return arg1 + arg2


async def func2():
    func1_return = await func1(1, 2)
    return func1_return


class Example:
    async def method1(self, arg1):
        return self.var1 + arg1 + 1

    async def method2(self):
        return await self.method1(2)


print("中文")
