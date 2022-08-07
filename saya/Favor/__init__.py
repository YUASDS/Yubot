import os
import re

from typing import DefaultDict, Tuple
from collections import defaultdict
from graia.saya import Saya, Channel
from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.ariadne.message.chain import Source
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexResult,
    FullMatch,
    WildcardMatch,
)

from util.sendMessage import autoSendMessage
from util.control import Permission
from .reply import get_reply

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)

last_exe = []


last_exec_favor: DefaultDict[str, Tuple[int, float]] = defaultdict(lambda: (1, 0.0))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage, GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("千音"),
                    "head" @ WildcardMatch(optional=True).flags(re.DOTALL),
                ],
            ),
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
        ],
    )
)
async def main(head: RegexResult, event: MessageEvent, Source_msg: Source):
    if head.matched:
        msg = head.result.asDisplay()
    else:
        msg = ""
    if "生日" in msg:
        return
    source = event.sender
    flags, result = await get_reply(msg=msg, qq=source.id)
    if not flags:
        return
    for reply in result:
        return await autoSendMessage(source, reply, Source_msg)
