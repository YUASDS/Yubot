import os

from graia.saya import Saya, Channel
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexResult,
    RegexMatch,
)

from util.sendMessage import autoSendMessage
from util.control import Permission, Interval, Rest
from .Arknights import get_img

"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/"),
                    "pool" @ RegexMatch("方舟寻访|方舟十连|方舟限定寻访"),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(pool: RegexResult, event: MessageEvent):
    if pool.result.asDisplay() == "方舟限定寻访":
        img = await get_img(id=str(event.sender.id), type="limit")
    else:
        img = await get_img(id=str(event.sender.id))
    return await autoSendMessage(event.sender, Image(data_bytes=img))
