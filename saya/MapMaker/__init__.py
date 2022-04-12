import os
import re

from PIL import UnidentifiedImageError
from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    WildcardMatch,
    RegexResult,
)

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest
from .LineMaker import line_maker, get_pet

func = os.path.dirname(__file__).split("\\")[-1]
bg = os.path.join(os.path.dirname(__file__), "bg.jpg")
CONFIG_FILE = Path(__file__).parent.joinpath("config.json")
MAP = {}
msg = [
    "功能([]内为可选参数，|为同一个指令,【】内为必须参数,()内为解释说明)：\n"
    "制作地图|制造地图|创建地图|刷新地图 [格子数（默认为6x6）][背景图片]\n使用方式：制造地图 8 [图片]\n\n"
    "加入地图【x】【分割符(任意非数字即可)】【y】\n使用方法：加入地图3 3\n\n"
    "移动【x】【分割符(任意非数字即可)】【y】\n使用方法：移动3 3（需要先加入地图）\n\n"
    "添加角色|增加角色|添加NPC【空格分割】【NPC名】【空格分割】【x】"
    "【分割符(任意非数字即可)】【y】[NPC立绘]\n使用方法：添加角色 白千音 3 3[图片]\n\n"
    "移动NPC|移动角色 【NPC名】【x】【分割符(任意非数字即可)】【y】\n使用方法：移动角色 白千音 3 5"
]
# if not os.path.exists(config_path):
#     with open(config_path, 'w', encoding='utf8') as f:
#         f.write("{}")
# config = load_config(config_path)

saya = Saya.current()
channel = Channel.current()
channel.name(func)


async def now_map(gid: str):

    if gid not in MAP:
        maker = line_maker(bg, part=6)
        maker.map_pice()
        lis = [[0 for _ in range(maker.rg1)] for _ in range(maker.rg2)]
        MAP[gid] = {
            "pet": {},
            "array": lis,
            "bg": maker.Img,
            "size": maker.cell_size,
            "part": 6,
        }
    else:
        maker = line_maker(MAP[gid]["bg"], part=MAP[gid]["part"])
        maker.map_pice(1)
        MAP[gid]["size"] = maker.cell_size
        MAP[gid]["bg"] = maker.Img
    file = MAP[gid]["bg"].copy()
    maker = line_maker(file=file, cell_size=MAP[gid]["size"])

    return maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])


async def join_map(x: int, y: int, gid: str, mid: str, npc_url=False):
    if gid not in MAP:
        maker = line_maker(bg, part=6)
        maker.map_pice()
        lis = [[0 for _ in range(maker.rg1)] for _ in range(maker.rg2)]
        MAP[gid] = {
            "pet": {},
            "array": lis,
            "bg": maker.Img,
            "size": maker.cell_size,
            "part": 6,
        }

    if mid not in MAP[gid]["pet"]:
        pet = await get_pet(image_url=npc_url) if npc_url else await get_pet(mid)
        MAP[gid]["pet"][mid] = pet

    file = MAP[gid]["bg"].copy()
    if True not in [mid in i for i in MAP[gid]["array"]]:
        MAP[gid]["array"][x][y] = mid

    else:
        for w, i in enumerate(MAP[gid]["array"]):
            for h, j in enumerate(i):
                if j == mid:
                    MAP[gid]["array"][w][h] = 0
                    MAP[gid]["array"][x][y] = mid
                    # print(w, h)
                    # print(MAP[gid]["array"])
    maker = line_maker(file=file, cell_size=MAP[gid]["size"])
    # logger.info(MAP[gid]["array"])
    return maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])


@channel.use(
    ListenerSchema(
        priority=16,  # 优先度
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("地图|地图帮助|地图功能"),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(group: Group):

    message = msg[0]

    return await safeSendGroupMessage(group, MessageChain.create(message))


@channel.use(
    ListenerSchema(
        priority=16,  # 优先度
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("制作地图|制造地图|创建地图|刷新地图"),
                    "space" @ RegexMatch("[\\s]+", optional=True),
                    "size" @ RegexMatch("[0-9]+", optional=True),
                    "anythings" @ WildcardMatch(optional=True),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def make(group: Group, anythings: RegexResult, size: RegexResult):
    gid = str(group.id)
    num = int(size.result.asDisplay()) if size.matched else 6
    maker = line_maker(bg, part=num)
    img = maker.map_pice()
    if anythings.matched:
        message_chain = anythings.result
        if message_chain.has(Image):
            image_url = message_chain.getFirst(Image).url
            try:
                back = await get_pet(image_url=image_url)
            except Exception:
                return await safeSendGroupMessage(
                    group, MessageChain.create("图片获取失败，换张图片吧~")
                )
            maker = line_maker(back, part=num)
            img = maker.map_pice(1)
    lis = [[0 for _ in range(maker.rg1)] for _ in range(maker.rg2)]
    MAP[gid] = {
        "pet": {},
        "array": lis,
        "bg": maker.Img,
        "size": maker.cell_size,
        "part": num,
    }
    await safeSendGroupMessage(group, "地图重置完成~")
    await safeSendGroupMessage(group, Image(data_bytes=img))


@channel.use(
    ListenerSchema(
        priority=16,  # 优先度
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch("更换背景|更换地图背景"),
                    "anythings" @ WildcardMatch().flags(re.DOTALL),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def refresh(group: Group, anythings: RegexResult):
    gid = str(group.id)
    if str(group.id) not in MAP:
        return await safeSendGroupMessage(group, "地图不存在，请先制作地图~")
    if anythings.matched:
        message_chain = anythings.result
        if message_chain.has(Image):
            image_url = message_chain.getFirst(Image).url
            try:
                back = await get_pet(image_url=image_url)
            except Exception:
                return await safeSendGroupMessage(group, "图片获取失败，换张图片吧~")
    MAP[gid]["bg"] = back
    img = await now_map(gid)
    await safeSendGroupMessage(group, "地图背景更换完成~")
    await safeSendGroupMessage(group, Image(data_bytes=img))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch("加入地图|移动"),
                    "x"
                    @ RegexMatch(
                        "[0-9]+",
                    ),
                    RegexMatch("\\D+"),
                    "y" @ RegexMatch("[0-9]+"),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def join(group: Group, x: RegexResult, y: RegexResult, member: Member):
    x = int(x.result.asDisplay()) - 1
    y = int(y.result.asDisplay()) - 1
    gid = str(group.id)
    mid = str(member.id)
    try:
        img = await join_map(x, y, gid, mid)
    except IndexError:
        return await safeSendGroupMessage(group, "超出范围了哦~")
    await safeSendGroupMessage(group, f"你已成功移动到地图[{x+1}] [{y+1}]位置~")
    await safeSendGroupMessage(group, Image(data_bytes=img))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("添加角色|增加角色|添加NPC|移动NPC|移动角色"),
                    RegexMatch("[\\s]+", optional=True),
                    "npc" @ RegexMatch("[\\S]+"),
                    RegexMatch("[\\s]+", optional=True),
                    "x" @ RegexMatch("[0-9]+"),
                    RegexMatch("\\D+"),
                    "y" @ RegexMatch("[0-9]+"),
                    FullMatch("\n", optional=True),
                    "anythings1" @ WildcardMatch(optional=True),
                ]
            )
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def joinImage(
    group: Group,
    npc: RegexResult,
    x: RegexResult,
    y: RegexResult,
    anythings1: RegexResult,
    member: Member,
):

    gid = str(group.id)
    x = int(x.result.asDisplay()) - 1
    y = int(y.result.asDisplay()) - 1
    npc = npc.result.asDisplay()
    message_chain = anythings1.result
    if message_chain.has(Image):
        image_url = message_chain.getFirst(Image).url
    else:
        image_url = f"http://q1.qlogo.cn/g?b=qq&nk={member.id}&s=640"
    try:
        res = await join_map(x, y, gid, npc, image_url)
    except IndexError:
        return await safeSendGroupMessage(group, "坐标选择失败，请重新选择坐标~")
    except UnidentifiedImageError:
        return await safeSendGroupMessage(group, "图片获取失败~")
    await safeSendGroupMessage(group, f"NPC【{npc}】已成功移动到[{x+1}] [{y+1}]位置~")
    await safeSendGroupMessage(group, Image(data_bytes=res))
