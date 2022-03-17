import traceback

from loguru import logger
from io import StringIO
from graia.ariadne.event.mirai import BotOfflineEventDropped
from graia.ariadne.event.lifecycle import AdapterShutdowned
from graia.saya import Saya, Channel
from graia.ariadne import get_running
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.saya.builtins.broadcast.schema import ListenerSchema

# from graia.ariadne.event.mirai import BotOfflineEventDropped

from config import yaml_data
from util.TimeTool import date_today, time_now
from util.text2image import create_image
from util.web import post
from util.mail import Sample

saya = Saya.current()
channel = Channel.current()

headers = {"Content-type": "application/x-www-form-urlencoded"}
bot_qq = yaml_data["Basic"]["MAH"]["BotQQ"]
key = yaml_data["Basic"]["API"]["Server"]
address = f'{yaml_data["Basic"]["Permission"]["Master"]}@qq.com'
send = True


async def offline_handle(qq=bot_qq, error=""):
    global send
    if not send:
        return
    send = False
    data = {
        "title": f"BOT:{qq}已掉线",
        "desp": f"错误报告:\n"
        f"BOT:{qq}\n"
        f"时间:{date_today()}{time_now()}\n"
        f"错误:{error}",
    }
    api = f"https://sctapi.ftqq.com/{key}.send"
    logger.warning(f"BOT:{qq}已掉线")
    args = {
        "to_address": address,
        "subject": f"BOT:{qq}已掉线",
        "text_body": "".join(data["desp"]),
    }
    try:
        info = await Sample.main_async(**args)
        logger.warning(info)
    except:
        info = await post(url=api, headers=headers, data=data)
        logger.warning(info)


async def make_msg_for_unknow_exception(event: ExceptionThrowed):

    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()
    msg = str(
        f"异常事件：\n{str(event.event)}"
        f"\n异常类型：\n{type(event.exception)}"
        f"\n异常内容：\n{str(event.exception)}"
        f"\n异常追踪：\n{tb}"
    )
    image = await create_image(msg, 200)

    return MessageChain.create([Plain("发生未捕获的异常\n"), Image(data_bytes=image)])


@channel.use(ListenerSchema(listening_events=[ExceptionThrowed]))
async def except_handle(event: ExceptionThrowed):
    app = get_running()
    try:
        await app.sendFriendMessage(
            yaml_data["Basic"]["Permission"]["Master"],
            await make_msg_for_unknow_exception(event),
        )
        global send
        send = True
        return
    except:
        return await offline_handle(error="")


@channel.use(
    ListenerSchema(listening_events=[BotOfflineEventDropped, AdapterShutdowned])
)
async def offline_send():
    await offline_handle(error="")
