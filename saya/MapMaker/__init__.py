import os

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
from .LineMaker import line_maker, save_config, load_config, get_pet

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
                    "num" @ RegexMatch("[0-9]+", optional=True),
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
async def make(group: Group, anythings: RegexResult, num: RegexResult):
    if num.matched:
        num: str = num.result.asDisplay()
        num = int(num) if num.isdigit else 6
    else:
        num = 6
    if anythings.matched:
        message_chain = anythings.result
        if message_chain.has(Image):
            if len(message_chain.get(Image)) > 1:
                return await safeSendGroupMessage(
                    group, MessageChain.create("创建背景时只能携带一张图片哦！")
                )
            image_url = message_chain.getFirst(Image).url
            try:
                back = await get_pet(image_url=image_url)
            except:
                return await safeSendGroupMessage(
                    group, MessageChain.create("图片获取失败，换张图片吧~")
                )
            imgs = line_maker(back, part=num)
            img = imgs.map_pice(option=1)
        else:
            imgs = line_maker(bg, part=num)
            img = imgs.map_pice()
    else:
        imgs = line_maker(bg, part=num)
        img = imgs.map_pice()
    cell_size = imgs.cell_size
    gid = str(group.id)
    MAP[gid] = {"pet": {}}
    lis = [[0 for _ in range(imgs.rg1)] for _ in range(imgs.rg2)]
    MAP[gid]["array"] = lis
    MAP[gid]["bg"] = imgs.Img
    data = await load_config(CONFIG_FILE)
    data[gid] = cell_size
    await save_config(data, CONFIG_FILE)
    await safeSendGroupMessage(group, MessageChain.create("地图制作完成"))
    await safeSendGroupMessage(group, MessageChain.create(Image(data_bytes=img)))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ FullMatch("加入地图"),
                    "x"
                    @ RegexMatch(
                        "[0-9]+",
                    ),
                    "space" @ RegexMatch("\\D+"),
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
    if not x.matched and y.matched:
        return await safeSendGroupMessage(
            group, MessageChain.create("加入地图的时候需要带上两个位置哦~")
        )
    x = x.result.asDisplay()
    y = y.result.asDisplay()
    gid = str(group.id)
    mid = str(member.id)
    x = int(x) - 1
    y = int(y) - 1
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]

        if True in [mid in i for i in MAP[gid]["array"]]:
            return await safeSendGroupMessage(group, MessageChain.create("请使用移动"))
        MAP[gid]["array"][x][y] = mid

        maker = line_maker(file=file, cell_size=cell_size)
        if mid not in MAP[gid]["pet"]:
            pet = await get_pet(mid)
            MAP[gid]["pet"][mid] = pet

        img = maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])

        await safeSendGroupMessage(group, MessageChain.create("加入地图成功"))
        await safeSendGroupMessage(group, MessageChain.create(Image(data_bytes=img)))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ FullMatch("移动"),
                    "x" @ RegexMatch("[0-9]+"),
                    "space" @ RegexMatch("\\D+"),
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
async def change(group: Group, x: RegexResult, y: RegexResult, member: Member):
    if not x.matched and y.matched:
        return await safeSendGroupMessage(group, MessageChain.create("移动地图的时候需要带上位置哦~"))
    x: str = x.result.asDisplay()
    y: str = y.result.asDisplay()
    gid = str(group.id)
    mid = str(member.id)
    if not (x.isdigit() and y.isdigit()):
        return
    x = int(x) - 1
    y = int(y) - 1
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]

        if True not in [mid in i for i in MAP[gid]["array"]]:
            return await safeSendGroupMessage(group, MessageChain.create("请先加入地图"))
        for w, i in enumerate(MAP[gid]["array"]):
            h = 0
            for j in i:
                if j == mid:
                    try:
                        MAP[gid]["array"][x][y] = mid
                    except Exception:
                        return await safeSendGroupMessage(
                            group, MessageChain.create("当前的移动超出了地图范围哦~")
                        )
                    MAP[gid]["array"][w][h] = 0
                    # print(w, h)
                    # print(MAP[gid]["array"])
                h += 1
        maker = line_maker(file=file, cell_size=cell_size)
        if mid not in MAP[gid]["pet"]:
            pet = await get_pet(mid)
            MAP[gid]["pet"][mid] = pet

        img = maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])

        await safeSendGroupMessage(group, MessageChain.create("移动地图成功"))
        await safeSendGroupMessage(group, MessageChain.create(Image(data_bytes=img)))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("添加角色|增加角色|添加NPC"),
                    "space1" @ RegexMatch("[\\s]+", optional=True),
                    "npc" @ RegexMatch("[\\S]+"),
                    "space2" @ RegexMatch("[\\s]+", optional=True),
                    "x" @ RegexMatch("[0-9]+"),
                    "space" @ RegexMatch("\\D+"),
                    "y" @ RegexMatch("[0-9]+"),
                    "enter" @ FullMatch("\n", optional=True),
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
    x = x.result.asDisplay()
    y = y.result.asDisplay()
    npc = npc.result.asDisplay()
    x = int(x) - 1
    y = int(y) - 1
    message_chain = anythings1.result
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]
        MAP[gid]["array"][x][y] = npc

        maker = line_maker(file=file, cell_size=cell_size)
        if message_chain.has(Image):
            if len(message_chain.get(Image)) > 1:
                return await safeSendGroupMessage(
                    group, MessageChain.create("添加角色只能携带一张图片哦！")
                )
            image_url = message_chain.getFirst(Image).url
            pet = await get_pet(image_url=image_url)
        else:
            pet = await get_pet(member_id=str(member.id))
        if npc not in MAP[gid]["pet"]:
            MAP[gid]["pet"][npc] = pet
        else:
            return await safeSendGroupMessage(
                group, MessageChain.create(f"当前{npc}，已经加入了地图了,请使用移动~")
            )
        img = maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])

        await safeSendGroupMessage(group, MessageChain.create("添加NPC成功"))
        await safeSendGroupMessage(group, MessageChain.create(Image(data_bytes=img)))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("移动NPC|移动角色"),
                    "space1" @ RegexMatch("[\\s]+", optional=True),
                    "npc" @ RegexMatch("[\\S]+"),
                    "space2" @ RegexMatch("[\\s]+", optional=True),
                    "x" @ RegexMatch("[0-9]+"),
                    "space" @ RegexMatch("\\D+", optional=True),
                    "y" @ RegexMatch("[0-9]"),
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
async def change_npc(group: Group, x: RegexResult, y: RegexResult, npc: RegexResult):
    if not x.matched and y.matched:
        return await safeSendGroupMessage(group, MessageChain.create("移动角色的时候需要带上位置哦~"))
    if not npc.matched:
        return await safeSendGroupMessage(
            group, MessageChain.create("移动角色的时候需要带上角色名字哦~")
        )

    x = x.result.asDisplay()
    y = y.result.asDisplay()
    npc = npc.result.asDisplay()

    gid = str(group.id)
    x = int(x) - 1
    y = int(y) - 1
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]
        if True not in [npc in i for i in MAP[gid]["array"]]:
            return await safeSendGroupMessage(group, MessageChain.create("请先加入地图"))
        if npc not in MAP[gid]["pet"]:
            return await safeSendGroupMessage(
                group, MessageChain.create("请先将NPC加入地图再移动哦~")
            )
        for w, i in enumerate(MAP[gid]["array"]):
            for h, j in enumerate(i):
                if j == npc:
                    MAP[gid]["array"][w][h] = 0
                    MAP[gid]["array"][x][y] = npc
                    # print(w, h)
                    # print(MAP[gid]["array"])
        maker = line_maker(file=file, cell_size=cell_size)
        img = maker.post_array(pet_dict=MAP[gid]["pet"], bg_array=MAP[gid]["array"])
        await safeSendGroupMessage(group, MessageChain.create("移动地图成功"))
        await safeSendGroupMessage(group, MessageChain.create(Image(data_bytes=img)))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))
