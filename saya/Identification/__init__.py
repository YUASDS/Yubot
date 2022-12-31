import os
import json
import random

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.parser.twilight import (
    RegexResult,
)

from util.sendMessage import autoSendMessage
from util.control import Permission, DaylyLimit
from util.DaylyRecord import add_data, get_data
from util.SchemaManager import Schema

path = Path(__file__).parent.joinpath("check.json")
XP_PATH = Path(__file__).parent.joinpath("XP.json")
CHECK_DATA: list = json.loads(path.read_text(encoding="utf-8"))
XP: list = json.loads(XP_PATH.read_text(encoding="utf-8"))
"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]
saya = Saya.current()
channel = Channel.current()
channel.name(func)
schema = Schema(channel)


@schema.use(("/XP鉴定"))
async def xp(event: MessageEvent):
    res = random.choice(XP)
    await autoSendMessage(event.sender, f"前辈抽到的XP是：\n【{res}】")
    """"""


@schema.use(("/今日鉴定"))
async def today(event: MessageEvent):
    qq = event.sender.id
    res = get_data(qq, func)
    await autoSendMessage(event.sender, f"今天的前辈毫无疑问是一只：\n{res}")


@schema.use(("/攻受鉴定"))
async def main(event: MessageEvent):
    qq = event.sender.id
    func_time = DaylyLimit.limit_dict.get(str(qq), {func: 0}).get(func, 0)
    if func_time >= 3:
        res = get_data(qq, func)
        await autoSendMessage(event.sender, f"今天的前辈毫无疑问是一只：\n{res}")
        return
    res = random.choice(CHECK_DATA)
    add_data(qq, func, res)
    await autoSendMessage(event.sender, f"在千音看来，前辈是一只：\n{res}")
    """"""


@schema.use(("/鉴定添加", ["data"]), permission=Permission.MASTER)
async def add(data: RegexResult, event: MessageEvent):
    if data.result:
        res = data.result.asDisplay()
        CHECK_DATA.append(res)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(CHECK_DATA, f, ensure_ascii=False, indent=2)
        return await autoSendMessage(event.sender, f"添加成功！\n{res}")
