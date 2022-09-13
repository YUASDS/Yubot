# coding=utf-8
"""
Xenon 管理 https://github.com/McZoo/Xenon/blob/master/lib/control.py
"""

import time

from asyncio import Lock, create_task
from graia.saya import Channel
from collections import defaultdict
from graia.ariadne.app import Ariadne
from graia.scheduler.timers import crontabify
from typing import DefaultDict, Set, Tuple, Union
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import MessageEvent
from graia.broadcast.builtin.decorators import Depend
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.message.element import Plain, Source
from graia.ariadne.model import Friend, Member, MemberPerm

from config import (
    user_list,
    yaml_data,
    group_data,
    group_data,
    change_config,
)
from database.db import all_sign_num, reset_sign, reset_favor_data
from database.funcdb import add_count, limit_today, limit_add_count, clear_limit
from .sendMessage import autoSendMessage

channel = Channel.current()


DebugGroup = yaml_data["Basic"]["Permission"]["DebugGroup"]
Master = yaml_data["Basic"]["Permission"]["Master"]
Admin = yaml_data["Basic"]["Permission"]["Admin"]


def check_sender(event: MessageEvent):
    """
    如果不是群成员或者好友，则不执行
    Args:
        event (MessageEvent):

    Raises:
        ExecutionStop: _description_
    """
    if not isinstance(event.sender, (Member, Friend)):
        raise ExecutionStop()
    else:
        return event.sender


class Permission:
    """
    用于管理权限的类，不应被实例化
    """

    MASTER = 30
    GROUP_ADMIN = 20
    USER = 10
    BANNED = 0
    DEFAULT = USER

    @classmethod
    def get(cls, member: Union[Member, Friend, int]) -> int:
        """
        获取用户的权限

        :param user: 用户群成员或QQ号
        :return: 等级，整数
        """

        if isinstance(member, Member):
            user = member.id
            user_permission = member.permission
        else:
            user = member.id if isinstance(member, Friend) else member
            user_permission = cls.DEFAULT

        if user in Admin:
            return cls.MASTER
        elif user in user_list["black"]:
            return cls.BANNED
        elif user_permission in [MemberPerm.Administrator, MemberPerm.Owner]:
            return cls.GROUP_ADMIN
        else:
            return cls.DEFAULT

    @classmethod
    def require(cls, level: int = DEFAULT) -> Depend:
        """
        指示需要 `level` 以上等级才能触发，默认为至少 USER 权限

        :param level: 限制等级
        """

        async def perm_check(event: MessageEvent):
            sender = check_sender(event)
            member_level = cls.get(sender)
            if member_level == cls.MASTER:
                return
            elif member_level < level:
                if isinstance(sender, Member) and (sender.group.id == DebugGroup):
                    return
                raise ExecutionStop()

        return Depend(perm_check)

    @classmethod
    def manual(cls, sender: Union[Friend, Member], level: int = DEFAULT):
        member_level = cls.get(sender)
        if member_level == cls.MASTER:
            pass
        elif member_level < level:
            if isinstance(sender, Member) and (sender.group.id == DebugGroup):
                return
            raise ExecutionStop()

    @classmethod
    def restricter(cls, func: str) -> Depend:
        """func 当前模块名字"""

        def res(event: MessageEvent):
            create_task(add_count(func))
            if not isinstance(event.sender, (Member, Friend)):
                raise ExecutionStop()
            member_level = cls.get(event.sender)
            if member_level == cls.MASTER:  # master直接通过,
                return
            if isinstance(event.sender, Friend):
                if yaml_data["Saya"][func]["Disabled"]:
                    raise ExecutionStop()
                return
            elif isinstance(event.sender, Member):
                # 允许私聊触发的功能除全局禁用外不做限制，但是仅限于好友
                group = event.sender.group
                # 正常的群聊限制
                if group.id == DebugGroup:
                    return

                # if group.id != DebugGroup:# 本处用于测试
                #     raise ExecutionStop()
                if func not in yaml_data["Saya"]:
                    yaml_data["Saya"][func] = {"Disabled": False}
                    change_config(yaml_data)
                if (
                    str(group.id) in group_data["black"]  # 黑名单群聊
                    or func in group_data[str(group.id)]["DisabledFunc"]
                    or yaml_data["Saya"][func]["Disabled"]
                ):  # 群组禁用
                    raise ExecutionStop()
            else:
                raise ExecutionStop()

        return Depend(res)


class Interval:
    """
    用于冷却管理的类，不应被实例化
    """

    last_exec: DefaultDict[str, Tuple[int, float]] = defaultdict(lambda: (1, 0.0))
    sent_alert: Set[str] = set()
    lock: Lock = Lock()

    @classmethod
    def require(
        cls,
        suspend_time: float = 3,
        max_exec: int = 1,
        override_level: int = Permission.MASTER,
        silent: bool = False,
    ):
        """
        指示用户每执行 `max_exec` 次后需要至少相隔 `suspend_time` 秒才能再次触发功能

        等级在 `override_level` 以上的可以无视限制

        :param suspend_time: 冷却时间
        :param max_exec: 在再次冷却前可使用次数
        :param override_level: 可超越限制的最小等级
        """

        async def cd_check(event: MessageEvent):
            eid = str(event.sender.id)
            if Permission.get(int(eid)) >= override_level:
                return
            current = time.time()
            async with cls.lock:
                last = cls.last_exec[eid]
                if current - cls.last_exec[eid][1] >= suspend_time:
                    cls.last_exec[eid] = (1, current)
                    if eid in cls.sent_alert:
                        cls.sent_alert.remove(eid)
                    return
                elif last[0] < max_exec:
                    cls.last_exec[eid] = (last[0] + 1, current)
                    if eid in cls.sent_alert:
                        cls.sent_alert.remove(eid)
                    return
                if eid not in cls.sent_alert:
                    if not silent:
                        await autoSendMessage(
                            event.sender,
                            "前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）",
                            event.messageChain.getFirst(Source).id,
                        )

                    cls.sent_alert.add(eid)
                raise ExecutionStop()

        return Depend(cd_check)

    @classmethod
    async def manual(
        cls,
        member: Union[Member, int],
        suspend_time: float = 10,
        max_exec: int = 1,
        override_level: int = Permission.MASTER,
    ):
        if Permission.get(member) >= override_level:
            return
        current = time.time()
        member_str = str(member.id) if isinstance(member, Member) else str(member)
        async with cls.lock:
            last = cls.last_exec[member_str]
            if current - cls.last_exec[member_str][1] >= suspend_time:
                cls.last_exec[member_str] = (1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            elif last[0] < max_exec:
                cls.last_exec[member_str] = (last[0] + 1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            if member not in cls.sent_alert:
                cls.sent_alert.add(member_str)
            raise ExecutionStop()


class DaylyLimit:
    limit_dict: dict[str, dict[str, int]] = {}

    @classmethod
    async def day_check(cls, func: str, qq: str, dat_limit: int = 3):
        if qq not in cls.limit_dict:
            cls.limit_dict[qq] = limit_today(qq)
        func_limit = cls.limit_dict[qq].get(func, 0)
        if func_limit >= dat_limit:
            return False
        cls.limit_dict[qq][func] = func_limit + 1
        limit_add_count(qq, func)
        return True

    @classmethod
    def DayCheck(cls, func: str, dat_limit: int = 3):
        async def check(event: MessageEvent):
            if await cls.day_check(func, str(event.sender.id), dat_limit):
                return
            await autoSendMessage(
                event.sender,
                " 今天已经到了上限次数了，前辈可不能贪心哦~",
                event.messageChain.getFirst(Source).id,
            )
            raise ExecutionStop()

        return Depend(check)


@channel.use(SchedulerSchema(crontabify("0 4 * * *")))
async def rest_scheduled(app: Ariadne):
    sign = await all_sign_num()
    await reset_favor_data()
    await reset_sign()
    clear_limit()
    await app.sendFriendMessage(
        yaml_data["Basic"]["Permission"]["Master"],
        MessageChain.create([Plain(f"已完成签到重置，签到统计{sign[0]}/{sign[1]}")]),
    )
    DaylyLimit.limit_dict = {}
