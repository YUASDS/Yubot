import asyncio

from graia.broadcast import Broadcast
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, MiraiSession
from pathlib import Path
import aiohttp


async def very_simple_example():
    ero_url = "https://api.ixiaowai.cn/api/api.php?return=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json()
        async with session.get(ret["imgurl"]) as r:
            pic = await r.read()

    # 将二进制数据储存在这里面
    Path("/Graiax/EroEroBot/eropic.jpg").read_bytes(pic)


asyncio.run(very_simple_example())
loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
        verify_key="ServiceVerifyKey",  # 填入 verifyKey
        account=959686587,  # 你的机器人的 qq 号
    ))


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: Ariadne, friend: Friend):
    await app.sendMessage(friend,
                          MessageChain.create([Plain("Hello, World!")]))
    # 实际上 MessageChain.create(...) 有没有 "[]" 都没关系


@bcc.receiver(GroupMessage)
async def setu(app: Ariadne, group: Group, message: MessageChain):
    await app.sendGroupMessage(
        group, MessageChain.create(f"不要说{message.asDisplay()}，来点涩图"))


# @bcc.receiver(GroupMessage)
@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.context_type == "group":
        await app.sendGroupMessage(event.group_id,
                                   MessageChain.create("别戳我，好痒"))
    else:
        await app.sendFriendMessage(event.friend_id,
                                    MessageChain.create("别戳我，好痒"))


...
loop.run_until_complete(app.lifecycle())
