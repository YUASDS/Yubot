import os
import re

import numpy as np
from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Source, Image
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (Twilight, FullMatch,
                                                   RegexMatch, WildcardMatch)

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest
from .LineMaker import (line_maker, save_config, load_config, get_pet)

func = os.path.dirname(__file__).split("\\")[-1]
bg = os.path.join(os.path.dirname(__file__), 'bg.jpg')
CONFIG_FILE = Path(__file__).parent.joinpath("config.json")
MAP = {}

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
            Twilight({
                "head": FullMatch("制作地图"),
                "anythings": WildcardMatch(flags=re.DOTALL)
            })
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def main(group: Group, anythings: RegexMatch, source: Source):
    imgs = line_maker(bg)
    img = await imgs.map_pice()
    cell_size = imgs.cell_size
    gid = str(group.id)
    MAP[gid] = {}
    MAP[gid]["pet"] = {}
    lis=[[0 for i in range(imgs.part)] for i in range(imgs.part)]
    MAP[gid]["array"] = lis
    MAP[gid]["bg"] = imgs.Img
    data = await load_config(CONFIG_FILE)
    data[gid] = cell_size
    await save_config(data, CONFIG_FILE)
    await safeSendGroupMessage(group, MessageChain.create("地图制作完成"))
    await safeSendGroupMessage(group,
                               MessageChain.create(Image(data_bytes=img)))
    pass


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("加入地图"),
                "x": RegexMatch("[a-z]|[A-Z]", optional=True),
                "y": RegexMatch("[0-9]", optional=True)
            })
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def join(group: Group, x: RegexMatch, y: RegexMatch, member: Member):
    x = x.result.asDisplay()
    y = y.result.asDisplay()
    gid = str(group.id)
    mid = str(member.id)
    x = ord(x.upper()) - 65
    y = int(y)
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]
        True in [mid in i for i in MAP[gid]["array"]]
        
        if True in [mid in i for i in MAP[gid]["array"]]:
            return await safeSendGroupMessage(group,
                                              MessageChain.create("请使用移动"))
        MAP[gid]["array"][x][y] = mid


        maker = line_maker(file=file, cell_size=cell_size)
        if mid not in MAP[gid]["pet"]:
            pet = await get_pet(mid)
            MAP[gid]["pet"][mid] = pet

        img = maker.post_array(pet_dict=MAP[gid]["pet"],
                               bg_array=MAP[gid]["array"])

        await safeSendGroupMessage(group, MessageChain.create("加入地图成功"))
        await safeSendGroupMessage(group,
                                   MessageChain.create(Image(data_bytes=img)))
        pass
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("移动"),
                "x": RegexMatch("[a-z]|[A-Z]", optional=True),
                "y": RegexMatch("[0-9]", optional=True)
            })
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def change(group: Group, x: RegexMatch, y: RegexMatch, member: Member):
    x = x.result.asDisplay()
    y = y.result.asDisplay()
    gid = str(group.id)
    mid = str(member.id)
    x = ord(x.upper()) - 65
    y = int(y)
    config = await load_config(CONFIG_FILE)
    if gid in MAP:
        file = MAP[gid]["bg"].copy()
        cell_size = config[gid]
        w = 0
        if not True in [mid in i for i in MAP[gid]["array"]]:

            return await safeSendGroupMessage(group, MessageChain.create("请先加入地图"))
        for i in MAP[gid]["array"]:
            h = 0
            for j in i:
                if j == mid:
                    MAP[gid]["array"][w][h] = 0
                    MAP[gid]["array"][x][y] = mid
                    # print(w, h)
                    # print(MAP[gid]["array"])
                h = h + 1
            w = w + 1
        maker = line_maker(file=file, cell_size=cell_size)
        if mid not in MAP[gid]["pet"]:
            pet = await get_pet(mid)
            MAP[gid]["pet"][mid] = pet

        img = maker.post_array(pet_dict=MAP[gid]["pet"],
                               bg_array=MAP[gid]["array"])

        await safeSendGroupMessage(group, MessageChain.create("移动地图成功"))
        await safeSendGroupMessage(group,
                                   MessageChain.create(Image(data_bytes=img)))
        pass
    else:
        await safeSendGroupMessage(group, MessageChain.create("请先创建地图"))
