import os
from datetime import datetime

from graia.saya import Saya, Channel
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Plain, At, Forward, ForwardNode
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    WildcardMatch,
    RegexResult,
)

from util.control import Permission, Interval
from util.sendMessage import autoForwMessage, autoSendMessage, get_name
from config import COIN_NAME
from database.db import reduce_gold
from .dicecho import dicecho_search
from .RandomSearch import random_tag_search
from .cnmods import cnmods_search

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)
bcc = saya.broadcast
inc = InterruptControl(bcc)  # type: ignore


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/模组搜索"),
                    "mod" @ WildcardMatch(),
                ]
            )
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Interval.require(),
        ],
    )
)
async def main(event: MessageEvent, mod: RegexResult):
    if not mod.matched:
        return
    qq = event.sender.id
    sender = event.sender
    mod_name: str = mod.result.asDisplay()  # type: ignore
    if not await reduce_gold(str(qq), 5):
        return await autoSendMessage(
            sender,
            f" 你的{COIN_NAME}不够了哦~",
        )

    dicecho_res = await dicecho_search(mod_name)
    cnmods_res = await cnmods_search(mod_name)
    send_list = []
    if dicecho_res:
        send_list.append("骰声回响检索结果为:\n————")
        send_list += dicecho_res
    else:
        send_list.append("骰声回响暂无检索结果")
    if cnmods_res:
        send_list.append("魔都检索结果为:\n————")
        send_list += cnmods_res
    else:
        send_list.append("魔都暂无检索结果")
    await autoForwMessage(sender, send_list, get_name(sender))  # type: ignore


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [FullMatch("/随机")],
                "tag" @ RegexMatch(".+", True),
                FullMatch("模组"),
                "times" @ RegexMatch("\\d+", True),
            )
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Interval.require(),
        ],
    )
)
async def GroupRandomSearch(event: MessageEvent, tag: RegexResult, times: RegexResult):
    qq = event.sender.id
    sender = event.sender
    if not await reduce_gold(str(qq), 5):
        return await autoSendMessage(
            sender,
            f" 你的{COIN_NAME}不够了哦~。",
        )
    times_origin = int(times.result.asDisplay()) if times.result else 1
    times_res = min(times_origin, 2)
    times_res = max(times_res, 1)
    res_list = []
    if times_origin > 2:
        res_list.append("一次最多随机两个模组哦~")
    res_list.extend(
        await random_tag_search(tag.result.asDisplay(), times_res)
        if tag.result
        else await random_tag_search(times=times_res)
    )

    await autoForwMessage(sender, res_list, get_name(sender))  # type: ignore
