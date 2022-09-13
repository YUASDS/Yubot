import os

from graia.saya import Saya, Channel
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.parser.twilight import RegexResult, RegexMatch

from util.control import Permission
from util.sendMessage import autoSendMessage
from util.SchemaManager import Schema
from database.funcdb import get_data

func = os.path.dirname(__file__).split("\\")[-1]

saya = Saya.current()
channel = Channel.current()
channel.name(func)
schema = Schema(channel)

commond = "date" @ RegexMatch("(\\d+)年(\\d+)月(\\d+)日", True)


@schema.use(("/state", commond), permission=Permission.MASTER)
async def func_log(date: RegexResult, event: MessageEvent):
    func_data = get_data(date.result.asDisplay()) if date.result else get_data()
    res = "千音功能当日统计结果为：\n"
    total = 0
    for key in func_data:
        res += f"{key}:{func_data[key]}\n"
        total += func_data[key]
    res += f"总计：{total}"
    await autoSendMessage(event.sender, res)
