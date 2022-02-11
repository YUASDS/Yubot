import os
import asyncio
from loguru import logger

from graia.saya import Saya, Channel
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Plain, At
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch

from util.control import Permission, Interval, Rest, restrict
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
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def main(group: Group, member: Member, mod: WildcardMatch):

    func = os.path.dirname(__file__).split("\\")[-1]
    if not restrict(func=func, group=group):
        logger.info(f"{func}在{group.id}群不可用")
        return
    if mod.matched:
        mod = mod.result.asDisplay()
        if not await reduce_gold(str(member.id), 5):
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [At(member.id), Plain(f" 你的{COIN_NAME}不足。")]),
            )
        else:
            res = await dicecho(mod)
            if len(res) > 0:
                for i in res:
                    await asyncio.sleep(0.5)
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create([At(member.id),
                                             Plain("".join(i))]),
                    )
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
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def CnmodsSearch(group: Group, member: Member, mod: WildcardMatch):

    func = os.path.dirname(__file__).split("\\")[-1]
    if not restrict(func=func, group=group):
        logger.info(f"{func}在{group.id}群不可用")
        return
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
            if len(res) > 0:
                for i in res:
                    await asyncio.sleep(0.5)
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create([At(member.id),
                                             Plain("".join(i))]),
                    )
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
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def GroupRandomSearch(group: Group, member: Member):

    func = os.path.dirname(__file__).split("\\")[-1]
    if not restrict(func=func, group=group):
        logger.info(f"{func}在{group.id}群不可用")
        return

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
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def GroupRandomLoveSearch(group: Group, member: Member):

    func = os.path.dirname(__file__).split("\\")[-1]
    if not restrict(func=func, group=group):
        logger.info(f"{func}在{group.id}群不可用")
        return

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
