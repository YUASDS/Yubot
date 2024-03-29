import os
import asyncio

from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.model import Member
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast.interrupt import InterruptControl
from graia.scheduler.timers import crontabify
from graia.ariadne.message.element import Source, At
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    ElementResult,
    RegexMatch,
    RegexResult,
)


from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval
from .reply import ShowerGroup, User, save_data

"""[qq][date][conten]
"""

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)
bcc = saya.broadcast
inc = InterruptControl(bcc)


@channel.use(SchedulerSchema(crontabify("1 0 * * *")))
async def shower_reset():
    """"""
    User.reset()
    ShowerGroup.reset()
    save_data()


@channel.use(SchedulerSchema(crontabify("* * * * *")))
async def shower_scheduled():
    """"""
    flag, group_lis = ShowerGroup.shower_event()
    if flag:
        logger.info(group_lis)
        for group in group_lis:
            for user in group_lis[group]:
                await safeSendGroupMessage(
                    int(group), (At(int(user)), group_lis[group][user])
                )
        save_data()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/"),
                    "head" @ RegexMatch("入浴|申请入浴|邀请共浴|共浴|共浴邀请"),
                    "at" @ ElementMatch(At, optional=True),
                    "target" @ RegexMatch("[0-9]+", optional=True),
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
    member: Member,
    head: RegexResult,
    target: RegexResult,
    source: Source,
    at: ElementResult,
):
    head = head.result.asDisplay()
    shower = User(member.id)
    gid = member.group.id
    if not shower.check_time():
        return await safeSendGroupMessage(member, "前辈已经入浴，或是超过最大入浴次数了哦~", source)

    if head in ["入浴", "申请入浴"]:
        reply = shower.get_reply(gid)
        save_data()
        return await safeSendGroupMessage(member, reply, source)
    if at.matched:
        targetqq = at.result.target
    else:
        targetqq = int(target.result.asDisplay())
    await safeSendGroupMessage(member, (At(targetqq), "\n你已经被邀请了~"))

    @Waiter.create_using_function(
        listening_events=[GroupMessage],
        priority=16,
        using_dispatchers=[
            Twilight([FullMatch("/"), "choose" @ RegexMatch("接受邀请|拒绝邀请")])
        ],
    )
    async def reply_ling(
        water_member: Member, water_source: Source, choose: RegexResult
    ):
        if water_member.id != targetqq or water_member.group.id != member.group.id:
            return
        if choose.result.asDisplay() == "接受邀请":
            await safeSendGroupMessage(member, "你接受了对方的邀请", water_source)
            return True
        else:
            await safeSendGroupMessage(member, "对方拒绝了你的邀请", source)
            return False

    try:
        res = await asyncio.wait_for(inc.wait(reply_ling), 60)
    except asyncio.TimeoutError:
        return
    if res:
        shower2 = User(targetqq)
        await safeSendGroupMessage(member, shower.get_reply_two(shower2, gid))

    """"""
