import os
import json
import random

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Member
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
)

from util.sendMessage import autoSendMessage
from util.control import Permission, Interval
from util.SchemaManager import Schema

path = Path(__file__).parent.joinpath("check.json")
DATA: list = json.loads(path.read_text(encoding="utf-8"))
"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]
saya = Saya.current()
channel = Channel.current()
channel.name(func)
schema = Schema(channel)


@schema.use(("/攻受鉴定"))
async def main(event: MessageEvent):
    res = random.choice(DATA)
    await autoSendMessage(event.sender, f"在千音看来，前辈是一只：\n{res}")
    """"""


@schema.use(("/鉴定添加", ["data"]), permission=Permission.MASTER)
async def add(data: RegexResult, event: MessageEvent):
    if data.result:
        res = data.result.asDisplay()
        DATA.append(res)
        with open(path, "w") as f:
            json.dump(DATA, f, ensure_ascii=False, indent=2)
        return await autoSendMessage(event.sender, f"添加成功！\n{res}")
