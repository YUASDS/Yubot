import ujson
import random
import aiohttp
from io import BytesIO
from pathlib import Path
from util.web import post


url = "http://api.arknights.ptilopsis.top/api/gacha/main.php"
img_url = "http://api.arknights.ptilopsis.top/api/gacha/PG/main.php"
path = Path(__file__).parent.joinpath("settings.json")
ak_data: list = ujson.loads(path.read_text(encoding="utf-8"))["Arknights"]
datano = random.choice(ak_data)


async def get(url: str):
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url)
        res = await resp.content.read()

    return BytesIO(res).getvalue()


async def get_img(id: str, type: str = "normal"):
    """
    type:norma/limit 常驻/限定
    id:qq
    """
    global datano
    data = {
        "datano": datano,
        "agentList": "auto",
        "time": 10,
        "type": type,  # norma/limit 常驻/限定
        "id": id,  # 账号
    }
    for _ in range(3):
        js = await post(img_url, data)
        if "errno" not in js:
            break
        if js["errno"] in [-101, -3, -121]:
            datano = random.choice(ak_data)
    return await get(js["data"]["url"])
