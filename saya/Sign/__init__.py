import os
from random import randint

from graia.saya import Saya, Channel
from graia.ariadne.message.element import Member, Image, Friend
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch

from util.sendMessage import autoSendMessage
from util.text2image import font_file
from util.control import Permission, Interval, Rest
from database.db import favor, get_info, add_favor, add_gold, is_sign
from .util import Reward
from .sign import get_signin_img

path = os.path.dirname(__file__)

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(["head" @ FullMatch("签到")])],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(event: MessageEvent):
    mid = event.sender.id
    target = event.sender
    if not await is_sign(str(mid)):
        return await autoSendMessage(target, MessageChain.create("前辈今天已经签到过了哦，等明天再来吧~"))
    favor_add = 1
    gold_add = randint(1, 15)
    add_gold(qq=str(mid), num=gold_add)
    await add_favor(qq=str(mid), num=favor_add)
    info = await get_info(str(mid))  # 获取信息
    uid = info.id
    favors = info.favor
    fav = favor(favors)  # 获取好感度相关数据
    exp = [fav.res, fav.next]
    mahojin_path = os.path.join(path, "imgs", "mahojin.png")
    rewards = [
        Reward(name="乌帕", num=gold_add, ico=os.path.join(path, "imgs", "蓝2.png")),
        Reward(name="好感度", num=favor_add, ico=os.path.join(path, "imgs", "纠缠之缘.png")),
    ]  # 奖励信息
    if isinstance(target, Friend):
        name = target.nickname
    elif isinstance(target, Member):
        name = target.name
    pic = await get_signin_img(
        qq=mid,
        name=name,
        uuid=uid,
        level=fav.level,
        exp=exp,
        total_days=info.sign_num,
        rewards=rewards,
        font_path=font_file,
        mahojin_path=mahojin_path,
    )
    await autoSendMessage(target, MessageChain.create(Image(data_bytes=pic)))
