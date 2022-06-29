from pathlib import Path

import ujson
import aiohttp
import asyncio
from loguru import logger


path = Path(__file__).parent.joinpath("settings.json")
data: dict = ujson.loads(path.read_text(encoding="utf-8"))


api_key = data.get("api_key")
print(api_key)
base_url = "http://arclight.space:45445"


async def search(params: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/search?api_key={api_key}"
        async with session.get(url, params=params) as resp:
            res = await resp.json()
    logger.debug(params)
    logger.debug(res)
    return res


async def change(type: str, data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"{base_url}/{type}?api_key={api_key}"
        async with session.post(url, json=data) as resp:
            res = await resp.json()
    logger.debug(res)
    return res


# add_req = {
#     "title": "很不快乐的王子",
#     "kp_name": "冬日",
#     "kp_qq": 1787569211,
#     "start_time": "2022-06-01",
#     "last_time": "2d",
#     "minper": 1,
#     "maxper": 4,
#     "isfull": False,
#     "tags": "COC",
#     "des": data["des"],
# }
# upadate_req = {
#     "id": 1,
#     "title": "快乐王子",
#     "kp_name": "冬日",
#     "kp_qq": 1787569211,
#     "start_time": "2022-06-01",
#     "last_time": "2d",
#     "minper": 1,
#     "maxper": 4,
#     "isfull": False,
#     "tags": "COC",
#     "des": "团的详细介绍~~~",
# }
# delete_req = {
#     "id": 1,
#     "qq": 1787569211,
# }
# search_data = {"kp_qq": "1787569211"}
# # asyncio.run(change("add", add_req))
# asyncio.run(search(search_data))
