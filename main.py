import asyncio
from cgitb import text
from graia.ariadne.message.element import Image

from graia.broadcast import Broadcast
from graia.ariadne.message.parser.pattern import FullMatch
from graia.ariadne.message.parser.twilight import Sparkle, Twilight

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group, MiraiSession
# from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import NudgeEvent
from yinlish import opens,chs2yin
...
loop = asyncio.new_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host="http://localhost:8080",
        verify_key="ServiceVerifyKey",
        account=959686587,
        # 此处的内容请按照你的 MAH 配置来填写
    ),
)


# @bcc.receiver(GroupMessage)
@bcc.receiver(NudgeEvent)
async def getup(app: Ariadne, event: NudgeEvent):
    if event.target == 959686587:
        if event.context_type == "group":
            await app.sendGroupMessage(event.group_id,
                                       MessageChain.create("别戳我，好痒~"))
        else:
            await app.sendFriendMessage(
                event.friend_id,
                MessageChain.create("别戳我，好痒", 
                                    Image(path="D:\\img\\preview.jpg")))



@bcc.receiver(FriendMessage)
async def setu(friend: Friend, Message: MessageChain):
    s=await opens(Message.asDisplay())
    await app.sendFriendMessage(
        friend, MessageChain.create(f"不要说{Message.asDisplay()}，{s}"))



@bcc.receiver(GroupMessage,
              dispatchers=[Twilight(Sparkle([FullMatch("涩图来")]))])
async def test1(app: Ariadne, group: Group, Message: MessageChain):
    await app.sendGroupMessage(
        group, Message.create(Image(path="D:\\img\\preview.jpg")))


@bcc.receiver(FriendMessage,
              dispatchers=[Twilight(Sparkle([FullMatch("涩图来")]))])
async def test(app: Ariadne, friend: Friend, Message: MessageChain):
    await app.sendFriendMessage(
        friend, Message.create(Image(path="D:\\img\\preview.jpg")))


@bcc.receiver(FriendMessage,
              dispatchers=[Twilight(Sparkle([FullMatch("涩图来")]))])
async def test(app: Ariadne, friend: Friend, Message: MessageChain):
    await app.sendFriendMessage(
        friend, Message.create(Image(path="D:\\img\\preview.jpg")))
# app.launch_blocking()


@bcc.receiver(GroupMessage)
async def setu(app: Ariadne, group: Group, message: MessageChain,event: GroupMessage):
    print("触发")
    if event.sender.id==1787569211:
        print("触发2")
        tx=await chs2yin(message.asDisplay())
        await app.sendGroupMessage(group, MessageChain.create(
            f"{tx}，hso"
        ))

loop.run_until_complete(app.lifecycle())
