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
    # WildcardMatch,
)

from util.sendMessage import autoSendMessage
from util.control import Permission, Interval, Rest

path = Path(__file__).parent.joinpath("check.json")
data: dict = json.loads(path.read_text(encoding="utf-8"))
"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]
saya = Saya.current()
channel = Channel.current()
channel.name(func)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(["head" @ FullMatch("/攻受鉴定")])],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(member: Member, source: Source, event: MessageEvent):
    type = random.choice(data)
    await autoSendMessage(member, f"在千音看来，前辈是一只：\n{type}")
    """"""
