from asyncio.log import logger
import re
from typing import Union, Iterable, Callable, Any, Type
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, Match


from util.control import Permission, Interval, DaylyLimit


class Schema:
    def __init__(self, channel: Channel) -> None:
        self.channel = channel

    def use(
        self,
        commond: Iterable[Union[str, dict[str, str], Iterable[str], Match]],
        dayly_limit: Union[int, None] = None,
        priority: int = 16,
        permission: int = Permission.DEFAULT,
        interval: float = 3,
    ):
        """_summary_

        Args:
            commond (Union[Iterable[Union[str, dict[str, str], list[str]]], list, Twilight]): 正则表达式组合
            dayly_limit (Union[int, None], optional): 每日上限. Defaults to None.
            priority (int, optional): 优先级. Defaults to 16.
            permission (int, optional): 最低权限（默认用户）. Defaults to Permission.DEFAULT.
            interval (float, optional): 冷却. Defaults to 3.
        """
        warpped = self.channel.use(
            get_schema(
                func=self.channel.meta["name"],
                commond=commond,
                priority=priority,
                dayly_limit=dayly_limit,
                permission=permission,
                interval=interval,
            )
        )

        def warp(target: Union[Type, Callable, Any]):
            return warpped(target)

        return warp


def match_analyzer(
    commond: Iterable[Union[str, dict[str, str], Iterable[str], Match]],
):  # sourcery skip: instance-method-first-arg-name
    """_summary_

    Args:
        commond (Union[Iterable[Union[str, dict[str, str], list[str]]], list]):
        多种形式正则表达式匹配
        [{"":""},"",match]
    Returns:
        _type_: _description_
    """
    match_res = []
    for i in commond:
        if isinstance(i, Match):
            logger.debug(f"Match: {i}")
            match_res.append(i)
        elif isinstance(i, str):
            match_res.append(RegexMatch(i))
        elif isinstance(i, list):
            match_res.append(i[0] @ RegexMatch(".*").flags(re.DOTALL))
        elif isinstance(i, dict):
            for key, value in i.items():
                expressin = value or ".*"
                match_res.append(key @ RegexMatch(expressin).flags(re.DOTALL))

    return match_res


def waiter_scheme(
    commond: Iterable[Union[str, dict[str, str], Iterable[str], Match]],
    priority: int = 15,
):
    if isinstance(commond, Twilight):
        match = commond
    else:
        match = Twilight(match_analyzer(commond))
    return {
        "listening_events": [GroupMessage, FriendMessage],
        "inline_dispatchers": [match],
        "priority": priority,
    }


def get_schema(
    func: str,
    commond: Iterable[Union[str, dict[str, str], Iterable[str], Match]],
    dayly_limit: Union[int, None] = None,
    priority: int = 16,
    permission: int = Permission.DEFAULT,
    interval: float = 3,
):
    """_summary_

    Args:
        func (str): 功能名称，用于每日上限，次数统计等一系列功能
        twilight (Union[list, tuple]): _description_
        dayly_limit (Union[int, None], optional): _description_. Defaults to None.
        permission (int, optional): _description_. Defaults to Permission.DEFAULT.
        interval (float, optional): _description_. Defaults to 3.

    Returns:
        ListenerSchema: _description_
    """
    if isinstance(commond, Twilight):
        match = commond
    else:
        match = Twilight(match_analyzer(commond))
    if dayly_limit:
        return ListenerSchema(
            listening_events=[GroupMessage, FriendMessage],
            inline_dispatchers=[match],
            priority=priority,
            decorators=[
                Permission.restricter(func),
                Permission.require(permission),
                Interval.require(interval),
                DaylyLimit.DayCheck(func, dayly_limit),
            ],
        )

    else:
        return ListenerSchema(
            listening_events=[GroupMessage, FriendMessage],
            inline_dispatchers=[match],
            priority=priority,
            decorators=[
                Permission.restricter(func),
                Permission.require(permission),
                Interval.require(interval),
            ],
        )
