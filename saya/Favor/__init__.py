import os
import re
import time

from typing import DefaultDict, Tuple
from collections import defaultdict
from graia.ariadne import get_running
from graia.saya import Saya, Channel
from graia.ariadne.model import Member, Friend
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.event.message import MessageEvent, FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain, Source
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

print(re_key_word)
last_exe = []


last_exec_favor: DefaultDict[str, Tuple[int, float]] = defaultdict(lambda: (1, 0.0))


async def cd_check(
    event: MessageEvent, suspend_time: float = 60, silent: bool = False, sent_alert=None
):
    if sent_alert is None:
        sent_alert = []
    current = time.time()
    eid = str(event.sender.id)
    if current - last_exec_favor[eid][1] >= suspend_time:
        last_exec_favor[eid] = (1, current)
        if eid in sent_alert:
            sent_alert.remove(eid)
        return
    if eid not in sent_alert:
        app = get_running()
        if not silent:
            if isinstance(event.sender, Member):
                await app.sendGroupMessage(
                    event.sender.group,
                    MessageChain.create("前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）"),
                    quote=event.messageChain.getFirst(Source).id,
                )

            elif isinstance(event.sender, Friend):

                await app.sendFriendMessage(
                    event.sender,
                    MessageChain.create("前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）"),
                    quote=event.messageChain.getFirst(Source).id,
                )

        sent_alert.append(eid)
    raise ExecutionStop()


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
    await cd_check(event)
    if head.matched:
        plain = head.result.asDisplay()
        match = re.compile(re_key_word)
        order = match.findall(plain)
        if order:
            order = order[0][1]
        else:
            order = None
    else:
        order = None
    source = event.sender
    flags, result = await get_reply(order=order, qq=source.id)
    if not flags:
        return
    for reply in result:
        return await autoSendMessage(source, reply, Source_msg)
