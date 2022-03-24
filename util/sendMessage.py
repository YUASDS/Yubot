from typing import Optional, Union, Iterable
from graia.ariadne import get_running
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.model import BotMessage, Group, Member, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Source, Element


async def safeSendGroupMessage(
    target: Union[Group, int],
    message: Union[MessageChain, Iterable[Element], Element, str],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:  # sourcery skip: assign-if-exp
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    app = get_running()
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
    target: Union[
        Member,
        Friend,
        Group,
        str,
        int,
    ],
    message: Union[MessageChain, Iterable[Element], Element, str],
    quote: Optional[Union[Source, int]] = None,
) -> BotMessage:
    """根据输入的目标类型自动选取发送好友信息或是群组信息"""
    app = get_running()
    if isinstance(target, str):
        target = int(target)
    if not isinstance(message, MessageChain):
        message = MessageChain.create(message)
    if isinstance(target, (Member, Group)):
        return await app.sendGroupMessage(target, message, quote=quote)
    elif isinstance(target, (Friend, int)):
        return await app.sendFriendMessage(target, message, quote=quote)


def get_name(taget: Union[Member, Friend, Group]) -> str:
    return taget.nickname if isinstance(taget, Friend) else taget.name
