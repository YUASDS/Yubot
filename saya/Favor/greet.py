import time
import random
from pathlib import Path
from .favor import normal_favor
import ujson

from util.TimeTool import time_now


path = Path(__file__).parent.joinpath("other.json")
greet_data: dict = ujson.loads(path.read_text(encoding="utf-8"))
greet_order = ["早上好", "中午好", "晚上好", "晚安"]
"""[qq][date][conten]
"""


def check_time() -> int:
    now_time = time.localtime().tm_hour
    return now_time // 3


def morning(qq: int):
    now = check_time()
    if now < 1:
        return ""
    """"""


def noon(qq: int):
    """"""
    return ""


def night(qq: int):
    """"""
    return ""


async def good_night(qq: int) -> list[str]:
    """"""
    now = check_time()
    if now == 7:
        flag, reply = await normal_favor("晚安", qq)
        return reply
    else:
        reply = random.choice(greet_data["greet"]["good_night"][str(now)])
        return [reply]


func_dict = {"早上好": morning, "中午好": noon, "晚上好": night, "晚安": good_night}


async def greet(func_name: str, qq: int) -> list[str]:
    res = await func_dict[func_name](qq)
    return res
