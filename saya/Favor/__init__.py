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
from util.control import Permission, Rest
from .favor import re_key_word, get_reply

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
            Rest.rest_control(),
        ],
    )
)
async def main(head: RegexResult, event: MessageEvent, Source_msg: Source):
    if head.matched:
        plain = head.result.asDisplay()
        match = re.compile(re_key_word)
        order = match.findall(plain)
        order = order[0][1] if order else None
    else:
        order = None
    source = event.sender
    flags, result = await get_reply(order=order, qq=source.id)
    if not flags:
        return
    for reply in result:
        return await autoSendMessage(source, reply, Source_msg)
