import os
import random
import asyncio
from io import BytesIO

import aiohttp
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, RegexResult

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval
from .WaifuLab import waifu

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)
bcc = saya.broadcast
inc = InterruptControl(bcc)

http_proxy = {"http://127.0.0.1:33210"}

BROWER = 0


async def get_pic(pic_id: str):
    url = f"https://www.thiswaifudoesnotexist.net/example-{pic_id}.jpg"
    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url)
        res = await resp.content.read()

    return BytesIO(res).getvalue()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch("/"),
                    "head" @ RegexMatch("Waifu|头像生成|获取头像|随机头像"),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Interval.require(),
        ],
    )
)
async def main(group: Group):
    ran = random.randint(1, 100000)
    img = await get_pic(ran)
    await safeSendGroupMessage(
        group, MessageChain.create("你需要的头像已经生成好了哦~", Image(data_bytes=img))
    )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch("/"),
                    "head" @ RegexMatch("WaifuLab|Lab头像生成|Lab获取头像|Lab头像"),
                    "water" @ RegexMatch("无水印", optional=True),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Interval.require(),
        ],
    )
)
async def WaifuLab(group: Group, member: Member, water: RegexResult):
    global BROWER
    if BROWER > 5:
        return await safeSendGroupMessage(group, MessageChain.create("当前进程过多，等一会再来哦~"))
    else:
        BROWER += 1
    if water.matched:
        page = waifu(water_mark=False)
    else:
        page = waifu()
    await safeSendGroupMessage(
        group,
        "开始获取头像了哦~\n请耐心等待~",
    )
    stat = await page.gey_browser()
    if not stat:
        BROWER -= 1
        return await safeSendGroupMessage(group, MessageChain.create("连接超时，等一会再来哦~"))
    pic = await page.first_shot()
    pic = pic.getvalue()
    await safeSendGroupMessage(
        group,
        MessageChain.create("连接成功，请选择下一步哦~\n选择[序号]\n继续\n返回\n退出", Image(data_bytes=pic)),
    )
    func_dict = {
        "选择": page.other_shot,
        "继续": page.continues,
        "返回": page.back,
        "退出": page.close,
    }

    @Waiter.create_using_function(
        listening_events=[GroupMessage],
        using_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("选择|继续|返回|退出"),
                    "choose" @ RegexMatch("[0-9]+", optional=True),
                ]
            )
        ],
    )
    async def get_waifu(waiter_member: Member, head: RegexResult, choose: RegexResult):
        tar = 0
        if member.id == waiter_member.id:
            head = head.result.asDisplay()
            if choose.matched:
                choose = int(choose.result.asDisplay())
                if choose > 16:
                    await safeSendGroupMessage(group, "超出选择范围了哦~")
                    return
                if choose == 0:
                    await safeSendGroupMessage(group, "没有0这个选项哦~")
                    return
                tar = choose
            await safeSendGroupMessage(
                group,
                "操作成功~请静待结果~",
            )
            img = func_dict[head]
            if tar != 0:
                img = await img(choose)
            else:
                img = await img()
            if not img:
                return False  # 当返回为空时，选项为退出
            elif isinstance(img, tuple):
                await safeSendGroupMessage(
                    group,
                    MessageChain.create(
                        "获取成功~",
                        Image(data_bytes=img[0].getvalue()),
                        Image(data_bytes=img[1].getvalue()),
                    ),
                )
                return True
            else:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create("头像获取成功~", Image(data_bytes=img.getvalue())),
                )
                return False
        return

    sign = True
    while sign:
        try:
            sign = await asyncio.wait_for(inc.wait(get_waifu), 30)
        except asyncio.TimeoutError:
            await page.close()
            BROWER -= 1
            return await safeSendGroupMessage(group, "等待超时~")
    BROWER -= 1

    await safeSendGroupMessage(group, "你需要的头像已经生成好了哦~")
