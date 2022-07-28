import time
import random
from pathlib import Path

import ujson

from util.TimeTool import time_now


# path = Path(__file__).parent.joinpath("ArcNight.json")
# data: dict = json.loads(path.read_text(encoding="utf-8"))
"""[qq][date][conten]
"""


def check_time() -> int:
    now_time = time.localtime().tm_hour
    if now_time < 3:
        return -1
    elif now_time < 6:
        return 0
    elif now_time < 12:
        return 1
    elif now_time < 18:
        return 2
    else:
        return 3


def morning():
    now = check_time()
    if now < 0:
        return
    """"""


def noon():
    """"""


def night():
    """"""


func_dict = {"早上好": morning, "中午好": noon, "晚上好": night}


async def greet(func_name: str, qq: int) -> tuple[bool, list[str]]:
    """"""
    res = func_dict[func_name]()
    return True, ["晚上好哦"]
    """"""
