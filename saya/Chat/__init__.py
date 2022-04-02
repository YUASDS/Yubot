import os
import json
import random

from pathlib import Path
from graia.saya import Saya, Channel
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
)


from util.sendMessage import autoSendMessage
from util.control import Permission, Rest

path = Path(__file__).parent.joinpath("chat.json")
data: dict = json.loads(path.read_text(encoding="utf-8"))
"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ FullMatch("呜呜呜"),
                    "anythings" @ WildcardMatch(),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
        ],
    )
)
async def main(event: MessageEvent, source: Source):
    if random.random() < 0.5:
        await autoSendMessage(event.sender, "前辈不要哭泣哦~哭泣可是会让幸福溜走的哦~", source)
    """"""
