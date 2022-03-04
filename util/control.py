# coding=utf-8
"""
Xenon 管理 https://github.com/McZoo/Xenon/blob/master/lib/control.py
"""

import time
import random

from asyncio import Lock
from graia.saya import Channel
from collections import defaultdict
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group
from graia.scheduler.timers import crontabify
from typing import DefaultDict, Set, Tuple, Union
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import MessageEvent,GroupMessage
from graia.broadcast.builtin.decorators import Depend
from graia.scheduler.saya.schema import SchedulerSchema
from graia.ariadne.message.element import Plain, Source
from graia.ariadne.model import Friend, Member, MemberPerm

from config import (user_black_list, 
                    yaml_data,
                    group_data,
                    group_black_list,
                    change_config)
from database.db import all_sign_num,reset_sign,reset_favor_data

from .sendMessage import safeSendGroupMessage

channel = Channel.current()


SLEEP = 0


# @channel.use(SchedulerSchema(crontabify("30 7 * * *")))
# async def work_scheduled(app: Ariadne):
#     Rest.set_sleep(0)
#     await app.sendFriendMessage(
#         yaml_data["Basic"]["Permission"]["Master"],
#         MessageChain.create([Plain("已退出休息时间")]),
#     )


@channel.use(SchedulerSchema(crontabify("0 4 * * *")))
async def rest_scheduled(app: Ariadne):
    Rest.set_sleep(1)
    sign=await all_sign_num()
    await reset_favor_data()
    await reset_sign()
    await app.sendFriendMessage(
        yaml_data["Basic"]["Permission"]["Master"],
        MessageChain.create([Plain(f"已完成签到重置，签到统计{sign[0]}/{sign[1]}")]),
    )



class Rest:
    """
    用于控制睡眠的类，不应被实例化
    """

    def set_sleep(set):
        global SLEEP
        SLEEP = set

    def rest_control(zzzz: bool = True):
        async def sleep(event: GroupMessage):
            if (
                SLEEP
                and yaml_data["Basic"]["Permission"]["Rest"]
                and event.sender.group.id
                != yaml_data["Basic"]["Permission"]["DebugGroup"]
            ):
                if zzzz:
                    await safeSendGroupMessage(
                        event.sender.group,
                        MessageChain.create(
                            f"Z{'z'*random.randint(3,8)}{'.'*random.randint(2,6)}"
                        ),
                        quote=event.messageChain.getFirst(Source).id,
                    )
                raise ExecutionStop()

        return Depend(sleep)


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
    def get(cls, member: Union[Member,Friend,int]) -> int:
        """
        获取用户的权限

        :param user: 用户实例或QQ号
        :return: 等级，整数
        """

        if isinstance(member, Member):
            user = member.id
            user_permission = member.permission
        elif isinstance(member, int):
            user = member
            user_permission = cls.DEFAULT
        elif isinstance(member, Friend):
            user = member.id
            user_permission = cls.DEFAULT
        else:
            raise ExecutionStop()
        

        if user in yaml_data["Basic"]["Permission"]["Admin"]:
            res = cls.MASTER
        elif user in user_black_list:
            res = cls.BANNED
        elif user_permission in [MemberPerm.Administrator, MemberPerm.Owner]:
            res = cls.GROUP_ADMIN
        else:
            res = cls.DEFAULT
        return res

    @classmethod
    def require(cls, level: int = DEFAULT) -> Depend:
        """
        指示需要 `level` 以上等级才能触发，默认为至少 USER 权限

        :param level: 限制等级
        """

        def perm_check(event: MessageEvent):
            member_level = cls.get(event.sender)
            if member_level == cls.MASTER:
                pass
            elif member_level < level:
                raise ExecutionStop()
            elif yaml_data["Basic"]["Permission"]["Debug"]:
                if isinstance(event.sender,Member):
                    if (
                        event.sender.group.id
                        != yaml_data["Basic"]["Permission"]["DebugGroup"]
                    ):
                        raise ExecutionStop()

        return Depend(perm_check)

    @classmethod
    def manual(cls, member: Union[Member, Friend, int], level: int = DEFAULT) -> Depend:

        if isinstance(member, Member):
            member_id = member.id
        if isinstance(member, Friend):
            member_id = member.id
        if isinstance(member, int):
            member_id = member

        member_level = cls.get(member_id)

        if member_level == cls.MASTER:
            pass
        elif member_level < level:
            raise ExecutionStop()
        elif yaml_data["Basic"]["Permission"]["Debug"]:
            if member.group.id != yaml_data["Basic"]["Permission"]["DebugGroup"]:
                raise ExecutionStop()

    @classmethod
    def restricter(cls,func:str)->Depend: 
        """func 当前模块名字"""
        def res(event: MessageEvent):
            member_level = cls.get(event.sender.id)
            if member_level == cls.MASTER  : # master直接通过,
                return
            
            if isinstance(event.sender,Member):
                 # 允许私聊触发的功能除全局禁用外不做限制，但是仅限于好友
                group=event.sender.group
            elif isinstance(event.sender,Friend):
                if yaml_data["Saya"][func]["Disabled"]:
                    raise ExecutionStop()
                return   
                # 正常的群聊限制
            if group.id == yaml_data["Basic"]["Permission"]["DebugGroup"]:
                return
            
            # if group.id != yaml_data["Basic"]["Permission"]["DebugGroup"]:# 本处用于测试
            #     raise ExecutionStop()
            if func not in yaml_data["Saya"]:
                yaml_data["Saya"][func]={}
                yaml_data["Saya"][func]["Disabled"]=False
                change_config(yaml_data)
            if (str(group.id) in group_black_list # 黑名单群聊
                or func in group_data[str(group.id)]["DisabledFunc"]):# 群组禁用
                raise ExecutionStop()
            if str(group.id) not in group_data:
                pass

            
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
        suspend_time: float = 10,
        max_exec: int = 1,
        override_level: int = Permission.MASTER,
        silent: bool = False
    ):
        """
        指示用户每执行 `max_exec` 次后需要至少相隔 `suspend_time` 秒才能再次触发功能

        等级在 `override_level` 以上的可以无视限制

        :param suspend_time: 冷却时间
        :param max_exec: 在再次冷却前可使用次数
        :param override_level: 可超越限制的最小等级
        """

        async def cd_check(event: MessageEvent):
            eid=str(event.sender.id)
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
                        if isinstance(event.sender,Member):
                            await safeSendGroupMessage(
                            event.sender.group,
                            MessageChain.create(
                            f"前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）"
                            ),
                            quote=event.messageChain.getFirst(Source).id
                        )
                        elif isinstance(event.sender,Friend):
                            app:Ariadne=Ariadne.get_running()
                            await app.sendFriendMessage(
                                event.sender,MessageChain.create(
                            f"前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）" 
                            ),
                            quote=event.messageChain.getFirst(Source).id,
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
        async with cls.lock:
            last = cls.last_exec[member]
            if current - cls.last_exec[member][1] >= suspend_time:
                cls.last_exec[member] = (1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            elif last[0] < max_exec:
                cls.last_exec[member] = (last[0] + 1, current)
                if member in cls.sent_alert:
                    cls.sent_alert.remove(member)
                return
            if member not in cls.sent_alert:
                cls.sent_alert.add(member)
            raise ExecutionStop()

