from pathlib import Path

import ujson
from graia.saya import Channel
from graia.ariadne.app import Ariadne
from graia.scheduler.timers import crontabify
from graia.scheduler.saya.schema import SchedulerSchema


PATH = Path(__file__).parent.joinpath("cache.json")
DATA = ujson.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else {}

channel = Channel.current()


def add_data(qq, value):
    DATA[qq] = value


@channel.use(SchedulerSchema(crontabify("* * * * *")))
async def rest_scheduled(app: Ariadne):
    PATH.write_text(ujson.dumps(DATA, ensure_ascii=False))
