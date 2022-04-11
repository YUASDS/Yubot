import os


from graia.saya import Saya, Channel
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Source
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    RegexResult,
)

from util.control import Permission, Interval, Rest
from util.sendMessage import autoSendMessage
from config import COIN_NAME
from database.db import reduce_gold, add_gold
from database.luckDb import (
    add_luck,
    get_user_change,
    get_luck_id,
    sign,
    get_luck_info,
    get_gold_raw,
)


func = os.path.dirname(__file__).split("\\")[-1]
saya = Saya.current()
channel = Channel.current()
channel.name(func)
bcc = saya.broadcast
inc = InterruptControl(bcc)


def get_reword(gold):
    if gold < 0:
        return "【老旧奖券】"
    elif gold < 10:
        return "【普通奖券】"
    elif gold <= 20:
        return "【精品奖券】"
    elif gold <= 40:
        return "【精致奖券】"
    else:
        return "【华丽奖券】"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "heads" @ FullMatch("/放乌帕"),
                    "number" @ RegexMatch("\\d+", optional=True),
                ]
            ),
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(event: MessageEvent, number: RegexResult, source: Source):
    sender = event.sender
    if not number.matched:
        return await autoSendMessage(
            sender,
            "放下乌帕要输入放下的数量哦~",
            source,
        )
    number = int(number.result.asDisplay())
    if number > 20:
        uid = str(event.sender.id)
        if await reduce_gold(uid, number + 2):
            num = add_luck(uid, number)
            await autoSendMessage(
                sender,
                f" 你轻轻将[{number}]{COIN_NAME}打包在一起放进了乌帕池中,获得了一张抽取结果变化为【{num}】的{get_reword(num)}",
                source,
            )
        else:
            await autoSendMessage(sender, f" 你的{COIN_NAME}不足。", source)
    else:
        await autoSendMessage(sender, "一次性至少放下21乌帕哦~", source)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["heads" @ FullMatch("/抽乌帕")])],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def luck_draw(event: MessageEvent, source: Source):
    qq = str(event.sender.id)
    sender = event.sender
    change = get_user_change(qq)
    if change is None:
        await autoSendMessage(sender, "你还没有抽奖卷哦~\n请先放下乌帕获取乌帕抽奖卷哦~", source)
        return await autoSendMessage(
            sender,
            "——————乌帕抽奖————\n通过放下一个乌帕然后捡起一个乌帕的简单"
            "抽奖~\n指令：\n/放乌帕+数字（如：放乌帕40）（放乌帕会收取2手续费哦~）"
            "\n/抽乌帕",
        )

    luck_id = get_luck_id()
    sign(luck_id)
    gold = get_luck_info(luck_id).gold
    total = gold + change
    add_gold(qq=qq, num=total)
    replay = get_reply(gold)
    await autoSendMessage(sender, replay, source)
    await autoSendMessage(
        sender,
        f"打开礼盒，你发现其中有{gold}个乌帕，抽奖券变化：【{change}】,共获得【{total}】个乌帕",
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["heads" @ FullMatch("/奖券列表")])],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def draw_list(event: MessageEvent, source: Source):
    qq = str(event.sender.id)
    sender = event.sender
    change = get_gold_raw(qq)
    if not change:
        return await autoSendMessage(sender, "你还没有抽奖卷哦~\n请先放下乌帕获取乌帕抽奖卷哦~", source)
    reply = "你的奖券列表：\n"
    for i in change:
        reply += f"{get_reword(i)}:【{i}】\n"
    return await autoSendMessage(sender, reply.strip(), source)


def get_reply(gold):
    if gold < 30:
        des = "【干瘪】"
    elif gold < 50:
        des = "【有些干瘪】"
    elif gold < 100:
        des = "【包装不错】"
    elif gold < 200:
        des = "【有着精致包装】"
    else:
        des = "【精致包装】"
    return f"你怀揣着激动的心情将抽奖卷放入扭蛋机中，叮咚！\n从扭蛋机中掉落了一个：{des}的乌帕礼盒。"
