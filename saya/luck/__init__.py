import os

from graia.saya import Saya, Channel
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Plain, At
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    RegexResult,
)

from util.control import Permission, Interval, Rest
from util.sendMessage import safeSendGroupMessage
from config import COIN_NAME
from database.db import reduce_gold, add_gold
import database.luckDb as luckDB

saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

func = os.path.dirname(__file__).split("\\")[-1]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(["heads" @ FullMatch("放乌帕"), "number" @ RegexMatch("\\d+")])
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(group: Group, member: Member, number: RegexResult):
    if number.matched:
        number = int(number.result.asDisplay())
        if number > 10:
            if not await reduce_gold(str(member.id), number + 2):
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id), Plain(f" 你的{COIN_NAME}不足。")]),
                )
            else:
                num = await luckDB.add_luck(str(member.id), number)
                await safeSendGroupMessage(
                    group,
                    MessageChain.create(
                        [
                            At(member.id),
                            Plain(f" 收取2乌帕后~\n你成功放下{number}{COIN_NAME},下次拿起的增益为{num}"),
                        ]
                    ),
                )
        else:
            await safeSendGroupMessage(group, MessageChain.create("一次性至少放下10乌帕哦~"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["heads" @ FullMatch("抽乌帕")])],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def luck_draw(group: Group, member: Member):
    qq = str(member.id)
    if await luckDB.get_user_time(qq=qq):
        change = await luckDB.get_user_change(qq=qq)
        luck_id = await luckDB.get_luck_id()
        await luckDB.sign(luck_id)
        gold = await luckDB.get_luck_gold(luck_id)
        total = gold + change
        await add_gold(qq=qq, num=total)
        await safeSendGroupMessage(
            group,
            MessageChain.create(
                f"你抽到了id为{luck_id}的盒装乌帕，其中有{gold}个乌帕，计算增益{change},共获得{total}个乌帕"
            ),
        )

    else:
        await safeSendGroupMessage(group, MessageChain.create("你还没有放下乌帕," "因此无法抽取哦~"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["heads" @ FullMatch("乌帕抽奖")])],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def luck(group: Group):

    await safeSendGroupMessage(
        group,
        "——————乌帕抽奖————\n通过放下一个乌帕然后捡起一个乌帕的简单"
        "抽奖~\n指令：\n放乌帕+数字（如：放乌帕15）（放乌帕会收取2手续费哦~）"
        "\n抽乌帕",
    )
