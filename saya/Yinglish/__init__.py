import random
import re
import os

import jieba
import jieba.posseg as pseg
from graia.saya import Saya, Channel
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch

from util.sendMessage import autoSendMessage
from util.control import Permission, Interval, Rest
from database.db import favor, get_info, reduce_favor

jieba.setLogLevel(20)

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()


def _词转换(x, y, 淫乱度):
    if random.random() > 淫乱度:
        return x
    if x in {"，", "。"}:
        return "……"
    if x in {"!", "！"}:
        return "♡"
    if len(x) > 1 and random.random() < 0.5:
        if random.random() < 0.5:
            return f"{x[0]}……{x}♡"
        else:
            return f"{x[0]}……{x}"
    else:
        if y == "n" and random.random() < 0.5:
            x = "〇" * len(x)
        return f"……{x}"


def chs2yin(s, 淫乱度=0.6):
    return "".join([_词转换(x, y, 淫乱度) for x, y in pseg.cut(s)])


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("千音说淫语"),
                    "anythings": WildcardMatch(flags=re.DOTALL),
                }
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
async def main(event: MessageEvent, anythings: WildcardMatch, source: Source):
    sender = event.sender
    info = await get_info(str(sender.id))
    favor_info = favor(info.favor)
    level = favor_info.level
    if level < 6:
        await autoSendMessage(sender, "前辈这是在做什么...这样的事情是不行的哦....", source)
        return await reduce_favor(str(sender.id), 5, True)
    if anythings.matched:
        saying: str = anythings.result.asDisplay()
        if len(saying) < 200:
            await autoSendMessage(sender, "呜....这样的事情明明是不行的...但是既然" "是前辈的要求....")
            await autoSendMessage(sender, chs2yin(saying), source)
        else:
            await autoSendMessage(sender, "欸....前辈打算让千音念到什么时候啊...#恼")
    else:
        await autoSendMessage(sender, "前辈什么都不说，让千音怎么念....")
