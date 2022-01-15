import asyncio
from pathlib import Path
import aiohttp

async def very_simple_example():
    #注：这里为了教学，故意让 api 返回 json 形式
    ero_url = "https://api.ixiaowai.cn/api/api.php?return=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json()
        async with session.get(ret["imgurl"]) as r:
            pic = await r.read()
    
    #将二进制数据储存在这里面
    Path("/Graiax/EroEroBot/eropic.jpg").read_bytes(pic)

asyncio.run(very_simple_example())
