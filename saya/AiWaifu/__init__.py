import os
import random
from io import BytesIO

import httpx
from graia.saya import Saya, Channel
from graia.ariadne.model import Group
from graia.ariadne.message.element import Image
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest

func = os.path.dirname(__file__).split("\\")[-1]

saya = Saya.current()
channel = Channel.current()

http_proxy = {"http://127.0.0.1:33210"}


async def get_pic(pic_id) -> bytes:

    url = f"https://www.thiswaifudoesnotexist.net/example-{pic_id}.jpg"
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(url=url)
    byt = BytesIO(resp.content)
    return byt.getvalue()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({"head": RegexMatch("Waifu|头像生成|获取头像|随机头像")})
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def main(group: Group):
    print("1")
    ran = random.randint(1, 100000)
    img = await get_pic(ran)
    await safeSendGroupMessage(
        group, MessageChain.create("你需要的头像已经生成好了哦~", Image(data_bytes=img)))
    pass