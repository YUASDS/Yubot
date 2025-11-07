from datetime import datetime
from random import randint

from graia.ariadne import Ariadne
from typing import Optional, Union, Iterable
from graia.ariadne import get_running
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.model import BotMessage, Group, Member, Friend, Client, Stranger
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    At,
    Plain,
    Source,
    Element,
    ForwardNode,
    Forward,
)

# from loguru import logger


async def safeSendGroupMessage(
    target: Union[Group, int],
    message: Union[MessageChain, Iterable[Element], Element, str],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:  # sourcery skip: assign-if-exp
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    app: Ariadne = get_running()
    try:
        return await app.sendGroupMessage(target, message, quote=quote)
    except UnknownTarget:
        msg = []
        for element in message.__root__:
            if isinstance(element, At):
                member = await app.getMember(target, element.target)
                if member:
                    name = member.name
                else:
                    name = str(element.target)
                msg.append(Plain(name))
                continue
            msg.append(element)
        try:
            return await app.sendGroupMessage(
                target, MessageChain.create(msg), quote=quote
            )
        except UnknownTarget:
            return await app.sendGroupMessage(target, MessageChain.create(msg))


async def autoSendMessage(
    target: Union[Member, Friend, Group, str, int, Client, Stranger],
    message: Union[MessageChain, Iterable[Element], Element, str, list, tuple],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:  # type: ignore
    """根据输入的目标类型自动选取发送好友信息或是群组信息"""
    app: Ariadne = get_running()
    if isinstance(target, str):
        target = int(target)
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    if isinstance(target, (Member, Group)):
        return await app.sendGroupMessage(target, message, quote=quote)
    elif isinstance(target, (Friend, int)):
        return await app.sendFriendMessage(target, message, quote=quote)


async def autoForwMessage(
    target: Union[
        Member,
        Friend,
        Group,
        str,
        int,
    ],
    message: Union[Iterable[Element], Element, str, list],
    name: str,
):
    """_summary_
    Args:
        target (Union[ Member, Friend, Group, str, int, ]): _description_
        message (Union[Iterable[Element], Element, str]): _description_
        quote (Optional[Union[Source, int]], optional): _description_. Defaults to None.
    Returns:
        _type_: _description_
    """
    if isinstance(target, str):
        target = int(target)
    if isinstance(target, Group):
        target = randint(999999, 2147483647)
    if isinstance(message, (str, Element, MessageChain)):
        message = [
            message,
        ]
    message = [i for i in message if i]
    fwd_nodeList = [
        (
            ForwardNode(
                target=target,
                time=datetime.now(),
                message=i,
                name=name,
            )
            if isinstance(i, MessageChain)
            else ForwardNode(
                target=target,
                time=datetime.now(),
                message=MessageChain.create(i),
                name=name,
            )
        )
        for i in message
    ]
    finish_message = MessageChain.create(Forward(nodeList=fwd_nodeList))
    return await autoSendMessage(target, finish_message)


def get_name(taget: Union[Member, Friend, Group]) -> str:
    return taget.nickname if isinstance(taget, Friend) else taget.name


async def get_friend_by_id(id: int) -> Optional[Friend]:
    app: Ariadne = get_running()
    return await app.getFriend(id)


def get_group_user_id(event: MessageEvent) -> str:
    return (
        str(event.sender.group.id)
        if isinstance(event.sender, Member)
        else str(event.sender.id)
    )
