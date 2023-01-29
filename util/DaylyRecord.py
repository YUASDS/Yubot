from pathlib import Path
from typing import Union

from loguru import logger

import ujson
from graia.saya import Channel
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema

from .TimeTool import date_today

PATH = Path(__file__).parent.joinpath(f"day/{date_today()}.json")
if not PATH.exists():
    PATH.touch()
    PATH.write_text("{}", encoding="utf-8")
DATA: dict[str, dict[str, str]] = ujson.loads(PATH.read_text(encoding="utf-8"))
logger.info(f"{date_today()}初始化完成")


channel = Channel.current()


def add_data(qq: Union[int, str], key: str, value):
    if isinstance(qq, int):
        qq = str(qq)
    if qq not in DATA:
        DATA[qq] = {key: value}
    else:
        DATA[qq][key] = value


def get_data(qq: Union[int, str], key: str):
    if isinstance(qq, int):
        qq = str(qq)
    if qq not in DATA:
        DATA[qq] = {}
    return DATA[qq].get(key, None)


@channel.use(SchedulerSchema(crontabify("* 0 * * *")))
async def write_json():
    PATH.write_text(ujson.dumps(DATA, ensure_ascii=False), encoding="utf-8")


@channel.use(SchedulerSchema(crontabify("0 0 * * *")))
async def refresh():
    global DATA, PATH
    PATH = Path(__file__).parent.joinpath(f"day/{date_today()}.json")
    if not PATH.exists():
        PATH.touch()
        PATH.write_text("{}", encoding="utf-8")
    DATA = ujson.loads(PATH.read_text(encoding="utf-8"))
    logger.info(f"{date_today()}初始化完成")
