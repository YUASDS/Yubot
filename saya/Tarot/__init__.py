import os
import asyncio

from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.message.element import Image, Source
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    RegexResult,
)

from .draw import Tarot, draw_tarot, last_draw, get_bytes
from util.sendMessage import autoSendMessage
from util.control import Permission, Interval, DaylyLimit


"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)
bcc = saya.broadcast
inc = InterruptControl(bcc)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("/"), RegexMatch("塔罗牌|塔罗牌占卜")])],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Interval.require(),
            DaylyLimit.DayCheck(func, 15),
        ],
    )
)
async def main(event: MessageEvent):
    tarot = Tarot(str(event.sender.id))
    await autoSendMessage(
        event.sender,
        "就这样你走入了占卜店中，少女面带着微笑说着：“前辈既然来了，不如抽三张塔罗牌看看今天的运势哦~”(输入三次/选择[数字]抽取三张塔罗牌，如/选择1)",
    )
    draw_bytes = get_bytes(await asyncio.to_thread(draw_tarot, tarot.list_tarot))
    await autoSendMessage(event.sender, Image(data_bytes=draw_bytes))

    @Waiter.create_using_function(
        listening_events=[GroupMessage, FriendMessage],
        priority=16,
        using_dispatchers=[
            Twilight(
                [
                    FullMatch("/选择"),
                    "choose" @ RegexMatch("\\d+"),
                ]
            )
        ],
    )
    async def reply_ling(
        choose: RegexResult, wait_event: MessageEvent, waite_source: Source
    ):
        logger.info(f"==> {choose}{wait_event.sender.id}{event.sender.id}")
        if wait_event.sender.id != event.sender.id:
            return
        res = int(choose.result.asDisplay())
        if res > 22 or res < 1:
            await autoSendMessage(wait_event.sender, "前辈！没有这张塔罗牌的！", waite_source)
            return
        return int(choose.result.asDisplay())

    i = 0
    try:
        while i < 3:
            res = await asyncio.wait_for(inc.wait(reply_ling), 30)
            card = tarot.choose(res)
            if not card:
                await autoSendMessage(event.sender, "唔。。前辈!这张卡已经抽过了！")
                continue
            img = await asyncio.to_thread(draw_tarot, tarot.list_tarot)
            await autoSendMessage(
                event.sender,
                (
                    f"唔。。前辈这次抽到的是【{card[0]}】呢，这代表着\n————————\n{card[1]}",
                    Image(data_bytes=get_bytes(img)),
                ),
            )
            if i < 2:
                if card[0] in ["恶魔正位", "月亮正位", "塔正位", "塔逆位"] or (
                    "逆位" in card[0] and "恶魔逆位" not in card[0]
                ):
                    await autoSendMessage(
                        event.sender, "唔。。看起来前辈似乎不太好运的样子呢，不过不要担心，这并不是结局哦，所以前辈，再来一次吧！"
                    )
                else:
                    await autoSendMessage(event.sender, "嗯！。。看起来似乎不错的样子呢，前辈，再来一张吧！")
            else:
                await autoSendMessage(
                    event.sender,
                    "前辈抽出了第三张塔罗牌了，看来这次占卜已经结束了呢，不过不管好运还是坏运，千音都会陪着前辈的！",
                )
            i += 1
    except asyncio.TimeoutError:
        return await autoSendMessage(
            event.sender, "“前辈，真是笨蛋！。。”少女看着你一动不动，于是有点嗔怒的收起了塔罗牌。"
        )
    img = await asyncio.to_thread(last_draw, tarot.list_tarot)
    return await autoSendMessage(event.sender, Image(data_bytes=get_bytes(img)))
    """"""
