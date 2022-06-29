import re
import os
import time

from graia.saya import Saya, Channel
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    RegexMatch,
    WildcardMatch,
    RegexResult,
)
from loguru import logger

from .core import search, change
from .analysis import Analysis

from util.sendMessage import autoSendMessage, autoForwMessage
from util.control import Permission, Interval
from util.text2image import create_image

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)

"""
鸽笼注册 <密码>（返回key，没有密码返回空值）
鸽笼查询（再按查询参数细分，但总体会是这个指令）
鸽笼开团 <名字> （将默认填入发送者的用户名和QQ作为KP信息，提供一系列默认数据并交由发送者进一步修改）
鸽笼修改 <参数编号或参数名> <内容>（会尽量把可能的报错扼杀在萌芽中）
鸽笼删除 <id>
我的鸽笼
"""
action_dict = {
    "鸽笼添加": "add",
    "鸽笼查询": "search",
    "鸽笼开团": "add",
    "鸽笼修改": "update",
    "鸽笼删除": "delete",
    "当前鸽笼": "search",
    "我的鸽笼": "search",
}


async def get_data_list(response_data: list):
    msg_list = []
    for data in response_data:
        if not isinstance(data, dict):
            msg_list.append(data)
            continue
        data["start_time"] = time.strftime(
            "%Y年%m月%d日", time.strptime(data["start_time"], "%Y-%m-%d")
        )
        msg = f"""ID: {data["id"]}
团名-{data["title"]}
主持人昵称-{data["kp_name"]}
主持人QQ-{data["kp_qq"]}
开始时间-{data["start_time"]}
持续时间-{data["last_time"]}
最小人数-{data["minper"]}
最大人数-{data["maxper"]}
标签-{data["tags"]}
介绍-{data['des']}"""
        # await autoSendMessage(event.sender, data)
        total = len(data["des"])
        if total > 500:
            img = await create_image(msg)
            msg_list.append(Image(data_bytes=img))
        else:
            msg_list.append(msg)
    return msg_list


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    RegexMatch("/"),
                    "head" @ RegexMatch("鸽笼添加|鸽笼开团|鸽笼修改|鸽笼删除|鸽笼查询|我的鸽笼|当前鸽笼"),
                    "anythings" @ WildcardMatch().flags(re.DOTALL),
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
async def main(
    head: RegexResult,
    anythings: RegexResult,
    event: MessageEvent,
):
    if isinstance(event, GroupMessage):
        sender_name = event.sender.name
    else:  # FriendMessage
        sender_name = event.sender.nickname  # type: ignore
    head_get = head.result.asDisplay()  # type: ignore
    mode = action_dict[head_get]
    sender_qq = event.sender.id
    if head_get == "我的鸽笼":
        text = f"主持人QQ-{sender_qq}"
    elif anythings.result:
        text = anythings.result.asDisplay()
    elif head_get == "当前鸽笼":
        text = "20"
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    ana = Analysis(mode)
    data = ana.analyze(text)
    logger.debug(data)
    if mode == "search":
        try:
            num = int(text)
        except Exception:
            num = 25
        if head_get == "当前鸽笼":
            data = {"maxnum": num, "all": "true"}
        response = await search(data)
        if not response.get("succ"):
            return await autoSendMessage(event.sender, response["err_msg"])
        if not (data_get := response["data"]):
            return await autoSendMessage(event.sender, "没有找到相关信息")
        msg_list = await get_data_list(response["data"])
        return await autoForwMessage(event.sender, msg_list, sender_name)  # type: ignore
    data["kp_qq"] = event.sender.id
    if mode == "add":
        data["kp_name"] = sender_name  # type: ignore
        response = await change(mode, data)
        if response.get("succ"):
            return await autoSendMessage(event.sender, "鸽笼添加成功~")
        return await autoSendMessage(event.sender, response["err_msg"])
    elif mode == "delete":
        new_data = {"id": data["id"], "qq": event.sender.id}
        response = await change(mode, new_data)
        if response.get("succ"):
            return await autoSendMessage(event.sender, "鸽笼删除成功~")
        return await autoSendMessage(event.sender, response["err_msg"])
    elif mode == "update":
        data["kp_name"] = sender_name  # type: ignore
        response = await change(mode, data)
        if not response.get("succ"):
            return await autoSendMessage(event.sender, response["err_msg"])
        data_get = response["data"]
        new_list = ["修改前团本信息", data_get[0], "修改后团本信息", data_get[1]]
        msg_list = await get_data_list(new_list)
        return await autoForwMessage(event.sender, msg_list, sender_name)  # type: ignore
