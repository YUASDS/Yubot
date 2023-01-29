import re
import os
import time

from graia.saya import Saya, Channel
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.parser.twilight import RegexResult

from loguru import logger

from .model import (
    ArcLight,
    MessageAnalysis,
    PlayerRequestData,
    ResponseData,
    GetApplicationData,
)

from util.sendMessage import autoSendMessage, autoForwMessage, get_name
from util.text2image import create_image
from util.SchemaManager import Schema

func = os.path.dirname(__file__).split("\\")[-1]
saya = Saya.current()
channel = Channel.current()
channel.name(func)
schema = Schema(channel)

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
    "鸽笼开团": "add",
    "鸽笼查询": "search",
    "当前鸽笼": "search",
    "我的鸽笼": "search",
    "鸽笼修改": "update",
    "鸽笼删除": "delete",
    "鸽笼申请": "join",
    "邀请玩家": "invite",
    "退出鸽笼": "quit",
}


async def get_data_list(response_data: list[ResponseData]):
    msg_list = []
    logger.debug(response_data)
    for da in response_data:
        data = dict(da)
        # response_today = Response(**data)
        # logger.info(response_today)
        msg = f"""ID:{data["id"]}
团名:{data["title"]}
主持人昵称:{data["kp_name"]}
主持人QQ:{data["kp_qq"]}
开始时间:{data["start_time"]}
持续时间:{data["last_time"]}
最小人数:{data["minper"]}
最大人数:{data["maxper"]}
标签:{data["tags"]}
介绍:{data['des']}"""
        total = len(msg)
        if total > 2000:
            img = await create_image(msg)
            msg_list.append(Image(data_bytes=img))
        else:
            msg_list.append(msg)
        if da.players:
            for play in da.players:
                msg_list.append(
                    f"""
本团参与PL:
昵称:{play.nick}
QQ:{play.qq}"""
                )

    return msg_list


async def get_player_data(response_data: list[PlayerRequestData]):
    msg_list = []
    logger.debug(response_data)
    for data_part in response_data:
        data = dict(data_part)
        msg = f"""ID:{data["id"]}
团名:{data["title"]}
主持人QQ:{data["kp_qq"]}
申请人QQ:{data["qq"]}
昵称:{data["nick"]}
申请介绍:{data['msg']}"""
        total = len(data["msg"])
        if total > 500:
            img = await create_image(msg)
            msg_list.append(Image(data_bytes=img))
        else:
            msg_list.append(msg)
    return msg_list


async def get_appication_data(response_data: list[GetApplicationData]):
    msg_list = []
    logger.debug(response_data)
    for data_part in response_data:
        data = dict(data_part)
        if data_part.timestamp:
            time_local = time.localtime(data_part.timestamp / 1000)
            # 转换成新的时间格式(精确到秒)
            dt = time.strftime("%Y年%m月%d日 %H时%M分%S秒", time_local)
        else:
            dt = "暂未通过"
        msg = f"""ID:{data["id"]}
团名:{data["title"]}
主持人QQ:{data["kp_qq"]}
申请人QQ:{data["qq"]}
状态:{"通过"if data["status"]==1 else "拒绝" if data["status"]==2 else "待处理"}
处理时间:{dt}"""
        msg_list.append(msg)
    return msg_list


@schema.use(("/", {"head": "鸽笼添加|鸽笼开团"}, ["anythings"]))
async def add_trpg(
    head: RegexResult,
    anythings: RegexResult,
    event: MessageEvent,
):
    sender_name = get_name(event.sender)  # type: ignore
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("add")
    data["kp_qq"] = event.sender.id
    data["kp_name"] = sender_name  # type: ignore
    arclight = ArcLight(data)
    res = await arclight.add()
    if res.succ:
        return await autoSendMessage(event.sender, f"添加成功,id为{str(res.data)}")
    else:
        return await autoSendMessage(event.sender, res.err_msg)  # type: ignore


@schema.use(("/", {"head": "当前鸽笼|我的鸽笼"}))
async def search_trpg_self(
    head: RegexResult,
    event: MessageEvent,
):
    sender_name = get_name(event.sender)  # type: ignore
    head_get = head.result.asDisplay()  # type: ignore
    type_get = action_dict[head.result.asDisplay()]  # type: ignore
    sender_qq = event.sender.id
    data = {"maxnum": 25, "all": "true", "kp_qq": sender_qq}
    arclight = ArcLight(data)
    res = await arclight.search()
    if res.err_msg:
        return await autoSendMessage(event.sender, res.err_msg)
    if not (data_get := res.data):
        return await autoSendMessage(event.sender, "唔，千音没有找到相关信息。。。")
    msg_list = await get_data_list(data_get)
    return await autoForwMessage(event.sender, msg_list, sender_name)  # type: ignore


@schema.use(("/", {"head": "鸽笼查询|查询鸽笼"}, ["anythings"]))
async def search_tpg(
    head: RegexResult,
    anythings: RegexResult,
    event: MessageEvent,
):
    sender_name = get_name(event.sender)  # type: ignore
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("search")
    arclight = ArcLight(data)
    res = await arclight.search()
    if res.err_msg:
        return await autoSendMessage(event.sender, res.err_msg)
    if not (data_get := res.data):
        return await autoSendMessage(event.sender, "唔，千音没有找到相关信息。。。")
    msg_list = await get_data_list(data_get)
    return await autoForwMessage(event.sender, msg_list, sender_name)  # type: ignore


@schema.use(("/", {"head": "鸽笼修改|修改鸽笼"}, ["anythings"]))
async def updata_tpg(
    head: RegexResult,
    anythings: RegexResult,
    event: MessageEvent,
):
    sender_name = get_name(event.sender)  # type: ignore
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("add")
    data["kp_qq"] = event.sender.id
    data["kp_name"] = sender_name  # type: ignore
    arclight = ArcLight(data)
    res = await arclight.update()
    if res.err_msg:
        return await autoSendMessage(event.sender, res.err_msg)
    msg_list = await get_data_list(res.data)
    new_list = ["这是前辈修改前团本信息哦~", msg_list[0], "这里是前辈修改后团本信息~", msg_list[1]]
    return await autoForwMessage(event.sender, new_list, sender_name)  # type: ignore


@schema.use(("/", {"head": "鸽笼删除|删除鸽笼"}, ["anythings"]))
async def delete_trpg(
    anythings: RegexResult,
    event: MessageEvent,
):
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("add")
    if not data.get("id"):
        return await autoSendMessage(event.sender, "请通过id来删除鸽笼哦~")
    arclight = ArcLight(data)
    res = await arclight.delete()
    if res.succ:
        return await autoSendMessage(event.sender, "删除成功~")
    else:
        return await autoSendMessage(event.sender, res.err_msg)  # type: ignore


@schema.use(("/", {"head": "鸽笼申请|退出鸽笼|申请鸽笼|鸽笼退出"}, ["anythings"]))
async def join_quit_trpg(
    head: RegexResult,
    anythings: RegexResult,
    event: MessageEvent,
):
    head_get = head.result.asDisplay()  # type: ignore
    sender_name = get_name(event.sender)  # type: ignore
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    res = msg_get.split("\n")
    data = {}
    for line in res:
        res_get = line.split(":")
        if len(res_get) == 2:
            if res_get[0] in ["ID", "id"]:
                data["ids"] = [
                    res_get[1],
                ]
        else:
            data["msg"] = line
    data["player"] = {"nick": sender_name, "qq": event.sender.id}
    data["qq"] = event.sender.id
    arclight = ArcLight(data)
    if head_get in {"鸽笼申请", "申请鸽笼"}:
        res = await arclight.join()
        if res.succ:
            return await autoSendMessage(event.sender, "申请成功~")
    else:
        res = await arclight.quit()
        if res.succ:
            return await autoSendMessage(event.sender, "退出鸽笼成功~")

    return await autoSendMessage(event.sender, res.err_msg)  # type: ignore


@schema.use(("/", {"head": "删除玩家"}, ["anythings"]))
async def remove_trpg(
    anythings: RegexResult,
    event: MessageEvent,
):
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("remove")
    data["kp_qq"] = event.sender.id
    if not data.get("id"):
        return await autoSendMessage(event.sender, "请通过id来删除鸽笼哦~")
    arclight = ArcLight(data)
    res = await arclight.remove()
    if res.succ:
        return await autoSendMessage(event.sender, "删除成功~")
    else:
        return await autoSendMessage(event.sender, res.err_msg)  # type: ignore


@schema.use(("/", {"head": "申请列表"}, ["anythings"]))
async def get_approval_trpg(
    anythings: RegexResult,
    event: MessageEvent,
):
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("search")
    if not data.get("id"):
        return await autoSendMessage(event.sender, "请通过id来查询鸽笼哦~")
    data["kp_qq"] = event.sender.id
    arclight = ArcLight(data)
    res = await arclight.get_approval()
    if not res.succ:
        return await autoSendMessage(event.sender, res.err_msg)  # type: ignore
    if not res.data:
        return await autoSendMessage(event.sender, "当前该鸽笼还没有申请哦~")
    msg = await get_player_data(res.data)
    return await autoForwMessage(event.sender, msg, "申请列表")  # type: ignore


@schema.use(("/", {"head": "我的申请"}))
async def get_application_trpg(
    event: MessageEvent,
):

    data = {"qq": event.sender.id}
    arclight = ArcLight(data)
    res = await arclight.get_application()
    msg = await get_appication_data(res.data)
    if not res.succ:
        return await autoSendMessage(event.sender, res.err_msg)  # type: ignore
    return await autoForwMessage(event.sender, msg, "申请列表")  # type: ignore


@schema.use(("/", {"head": "同意申请|拒绝申请"}, ["anythings"]))
async def accept_trpg(
    head: RegexResult,
    event: MessageEvent,
    anythings: RegexResult,
):

    head_get = head.result.asDisplay()  # type: ignore
    sender_name = get_name(event.sender)  # type: ignore
    if anythings.result:
        msg_get = anythings.result.asDisplay()
    else:
        return await autoSendMessage(
            event.sender,
            "关于跑团公示板，请前往\nhttps://yuasds.gitbook.io/yin_book/functions/graia/pao-tuan-gong-shi-ban\n查看详情哦",
        )
    an = MessageAnalysis(msg_get)
    data = an.analysis("search")
    data["kp_qq"] = event.sender.id
    arclight = ArcLight(data)
    if head_get == "同意申请":
        res = await arclight.accept()
        if res.succ:
            return await autoSendMessage(event.sender, "同意成功~")
    else:
        res = await arclight.refuse()
        if res.succ:
            return await autoSendMessage(event.sender, "已成功拒绝申请了哦~")
    return await autoSendMessage(event.sender, res.err_msg)  # type: ignore
