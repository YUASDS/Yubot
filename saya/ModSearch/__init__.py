import os
import asyncio
from datetime import datetime

from graia.saya import Saya, Channel
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Plain, At,Forward, ForwardNode
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import (Twilight, FullMatch,
                                                   WildcardMatch)

from util.control import Permission, Interval, Rest
from util.sendMessage import safeSendGroupMessage
from config import COIN_NAME
from database.db import reduce_gold
from .dicecho import dicecho
from .RandomSearch import RandomSearch, RandomLoveSearch
from .cnmods import cnmods

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)
func = os.path.dirname(__file__).split("\\")[-1]

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "heads": FullMatch("模组搜索"),
                "mod": WildcardMatch()
            })
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def main(group: Group, member: Member, mod: WildcardMatch):

    if mod.matched:
        mod = mod.result.asDisplay()
        if not await reduce_gold(str(member.id), 5):
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [At(member.id), Plain(f" 你的{COIN_NAME}不足。")]),
            )
        else:
            fwd_nodeList = []
            res = await dicecho(mod)
            if len(res) > 0:
                for i in res:
                    fwd_nodeList.append(
                    ForwardNode(
                    target=member,
                    time=datetime.now(),
                    message=MessageChain.create("".join(i))
                    ))
                message = MessageChain.create(Forward(nodeList=fwd_nodeList))
                await safeSendGroupMessage(group,message)
            else:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id),
                                         Plain("\n无该搜索项")]),
                )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "heads": FullMatch("魔都搜索"),
                "mod": WildcardMatch()
            })
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def CnmodsSearch(group: Group, member: Member, mod: WildcardMatch):

    if mod.matched:
        mod = mod.result.asDisplay()
        if not await reduce_gold(str(member.id), 5):
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [At(member.id), Plain(f" 你的{COIN_NAME}不足。")]),
            )
        else:
            res = await cnmods(mod)
            fwd_nodeList = []
            if len(res) > 0:
                for i in res:
                    fwd_nodeList.append(
                    ForwardNode(
                    target=member,
                    time=datetime.now(),
                    message=MessageChain.create("".join(i))
                    ))
                message = MessageChain.create(Forward(nodeList=fwd_nodeList))
                await safeSendGroupMessage(group,message)
            else:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id),
                                         Plain("\n无该搜索项")]),
                )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"heads": FullMatch("随机模组")})],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def GroupRandomSearch(group: Group, member: Member):



    if not await reduce_gold(str(member.id), 5):
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id),
                                 Plain(f" 你的{COIN_NAME}不足。")]),
        )
    else:
        res = await RandomSearch()
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id),
                                 Plain("".join(res))]),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"heads": FullMatch("随机贴贴模组")})],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def GroupRandomLoveSearch(group: Group, member: Member):



    if not await reduce_gold(str(member.id), 5):
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id),
                                 Plain(f" 你的{COIN_NAME}不足。")]),
        )
    else:
        res = await RandomLoveSearch()
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id),
                                 Plain("".join(res))]),
        )
