import os

from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.scheduler.timers import every_custom_minutes
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.event.lifecycle import ApplicationLaunched
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, FullMatch

from config import COIN_NAME
from util.text2image import create_image
from database.db import get_ranking, get_info,favor
from util.control import Permission, Interval
from util.sendMessage import safeSendGroupMessage

saya = Saya.current()
channel = Channel.current()

RANK_LIST = None
FUNC = os.path.dirname(__file__).split("\\")[-1]

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": FullMatch("查看排行榜")})],
        decorators=[Permission.restricter(FUNC),Permission.require(), Interval.require()],
    )
)
async def main(group: Group):
    await safeSendGroupMessage(
        group, MessageChain.create([Image(data_bytes=RANK_LIST)])
    )


@channel.use(SchedulerSchema(every_custom_minutes(10)))
async def something_scheduled():
    global RANK_LIST
    msg = await get_ranking()
    RANK_LIST = await create_image(msg, 100)
    logger.info("排行榜已生成完毕")


@channel.use(ListenerSchema(listening_events=[ApplicationLaunched]))
async def bot_Launched():

    global RANK_LIST
    msg = await get_ranking()
    RANK_LIST = await create_image(msg, 100)
    logger.info("排行榜已生成完毕")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": FullMatch("查看个人信息")})],
        decorators=[Permission.require(), Interval.require()],
    )
)
async def get_user_info(group: Group, member: Member):
    user_info = await get_info(str(member.id))
    # user_favor=favor(favors)
    await safeSendGroupMessage(
        group,
        MessageChain.create(
            [
                Plain(f"UID：{user_info.id}"),
                Plain(f"\n你已累计签到 {user_info.sign_num} 天"),
                Plain(f"\n当前共有 {user_info.gold} 个{COIN_NAME}"),
                Plain(f"\n从有记录以来你共有 {user_info.talk_num} 次发言")
            ]
        ),
    )
