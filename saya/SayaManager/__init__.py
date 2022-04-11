import os
from typing import List, Dict, Optional, Union
from graia.saya import Saya, Channel
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.event.message import (
    GroupMessage,
    MessageEvent,
    FriendMessage,
)

from graia.ariadne.message.element import Source
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
    RegexResult,
    RegexMatch,
)


from util.sendMessage import autoSendMessage
from util.control import Permission, Interval, Rest

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)


channel.author("SAGIRI-kawaii")
channel.description(
    "插件管理插件"
    "发送 `已加载插件` 查看已加载插件\n"
    "发送 `插件详情 [编号|名称]` 可查看插件详情\n"
    "发送 `[加载|重载|卸载|打开|关闭]插件 [编号|名称]` 可加载/重载/卸载/打开/关闭插件"
)

bcc = saya.broadcast
inc = InterruptControl(bcc)


class SayaManager:
    __name__ = "SayaManager"
    __description__ = "插件管理"
    __usage__ = (
        "发送 `已加载插件` 查看已加载插件\n"
        "发送 `插件详情 [编号|名称]` 可查看插件详情\n"
        "发送 `[加载|重载|卸载|打开|关闭]插件 [编号|名称]` 可加载/重载/卸载/打开/关闭插件"
    )

    @staticmethod
    def unload_reload_channels(target: str, load_type: str):
        """重载或者卸载插件

        Args:
            name (str): 插件序号/名称
            load_type (str): 卸载/重载

        Returns:
            str: 操作结果
        """
        target = target.strip()
        loaded_channels = SayaManager.get_loaded_channels()
        keys = sorted(loaded_channels.keys())
        if target.isdigit():
            if not 0 <= int(target) - 1 < len(keys):
                return "错误的编号！请检查后再发送！"
            channel = loaded_channels[keys[int(target) - 1]]
            channel_path = keys[int(target) - 1]
        else:
            for lchannel in loaded_channels.keys():
                if loaded_channels[lchannel]._name == target:
                    channel = loaded_channels[lchannel]
                    channel_path = lchannel
                    break
            else:
                return "错误的名称！请检查后再发送！"
        result = (
            SayaManager.unload_channel(channel_path)
            if load_type == "卸载"
            else SayaManager.reload_channel(channel_path)
        )
        return (
            f"发生错误：{result[channel_path]}"
            if result
            else f"{channel._name}{load_type}成功"
        )

    @staticmethod
    def loaded_channels(target: str):
        """加载插件

        Args:
            name (str): 插件序号/名称

        Returns:
            str: 操作结果
        """
        target = target.strip()
        unloaded_channels = SayaManager.get_unloaded_channels()
        if target.isdigit():
            unloaded_channels.sort()
            if not 0 <= int(target) - 1 < len(unloaded_channels):
                return "错误的编号！请检查后再发送！"
            channel = unloaded_channels[int(target) - 1]
        else:

            for ulchannel in unloaded_channels:
                if ulchannel == target:
                    channel = ulchannel
                    break
            else:
                return "错误的名称！请检查后再发送！"
        if result := SayaManager.load_channel(channel):
            return f"发生错误：{result[channel]}"
        else:
            return f"插件{channel}加载成功"

    @staticmethod
    def get_loaded_channels() -> Dict[str, Channel]:
        return saya.channels

    @staticmethod
    def get_all_channels() -> List[str]:
        ignore = ["__init__.py", "__pycache__"]
        dirs = ["saya"]
        modules = []
        for path in dirs:
            for module in os.listdir(path):
                if module in ignore:
                    continue
                if os.path.isdir(module):
                    modules.append(f"{path.replace('/', '.')}.{module}")
                else:
                    modules.append(f"{path.replace('/', '.')}.{module.split('.')[0]}")
        return modules

    @staticmethod
    def get_unloaded_channels() -> List[str]:
        loaded_channels = SayaManager.get_loaded_channels()
        all_channels = SayaManager.get_all_channels()
        return [channel for channel in all_channels if channel not in loaded_channels]

    @staticmethod
    def get_channel(name: str) -> Optional[Channel]:
        return SayaManager.get_loaded_channels().get(name)

    @staticmethod
    def load_channel(modules: Union[str, List[str]]) -> Dict[str, Exception]:
        ignore = ["__init__.py", "__pycache__"]
        exceptions = {}
        if isinstance(modules, str):
            modules = [modules]
        with saya.module_context():
            for module in modules:
                if module in ignore:
                    continue
                try:
                    saya.require(module)
                except Exception as e:
                    exceptions[module] = e
        return exceptions

    @staticmethod
    def unload_channel(modules: Union[str, List[str]]) -> Dict[str, Exception]:
        exceptions = {}
        if isinstance(modules, str):
            modules = [modules]
        loaded_channels = SayaManager.get_loaded_channels()
        channels_to_unload = {
            module: loaded_channels[module]
            for module in modules
            if module in loaded_channels
        }
        with saya.module_context():
            for channel in channels_to_unload:
                try:
                    saya.uninstall_channel(channels_to_unload[channel])
                except Exception as e:
                    exceptions[channel] = e
        return exceptions

    @staticmethod
    def reload_channel(modules: Union[str, List[str]]) -> Dict[str, Exception]:
        exceptions = {}
        if isinstance(modules, str):
            modules = [modules]
        loaded_channels = SayaManager.get_loaded_channels()
        channels_to_reload = {
            module: loaded_channels[module]
            for module in modules
            if module in loaded_channels
        }
        with saya.module_context():
            for channel in channels_to_reload:
                try:
                    saya.reload_channel(channels_to_reload[channel])
                except Exception as e:
                    exceptions[channel] = e
        return exceptions


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight(
                [
                    "head" @ RegexMatch("加载|卸载|重载"),
                    FullMatch("插件"),
                    "target" @ WildcardMatch(),
                ]
            )
        ],
        decorators=[
            Permission.require(Permission.MASTER),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def Saya_Manager(
    head: RegexResult, target: RegexResult, source: Source, event: MessageEvent
):
    order = head.result.asDisplay().strip()
    name = target.result.asDisplay().strip()
    if order == "加载":
        res = SayaManager.loaded_channels(name)
    else:
        res = SayaManager.unload_reload_channels(name, order)
    return await autoSendMessage(event.sender, res, source)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[Twilight(["head" @ RegexMatch("已加载插件|未加载插件|插件列表")])],
        decorators=[
            Permission.require(Permission.MASTER),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def Saya_List(head: RegexResult, event: MessageEvent):
    order = head.result.asDisplay()
    if order in ["已加载插件", "插件列表"]:
        loaded_channels = SayaManager.get_loaded_channels()
        keys = sorted(loaded_channels.keys())
        return await autoSendMessage(
            event.sender,
            MessageChain.create(
                "目前加载插件：\n",
                [
                    f"{i + 1}. {loaded_channels[keys[i]]._name}\n"
                    for i in range(len(keys))
                ],
                "发送 `插件详情 [编号|名称]` 可查看插件详情~~",
            )
            # QuoteSource()
        )
    elif order == "未加载插件":
        unloaded_channels = SayaManager.get_unloaded_channels()
        unloaded_channels.sort()
        return await autoSendMessage(
            event.sender,
            MessageChain.create(
                [Plain(text="目前未加载插件：\n")],
                [
                    Plain(text=f"{i + 1}. {unloaded_channels[i]}\n")
                    for i in range(len(unloaded_channels))
                ],
                [Plain(text="发送 `[加载|卸载|重载]插件 [编号|名称]` 可加载/卸载/重载插件\n")],
            ),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage, FriendMessage],
        inline_dispatchers=[
            Twilight([RegexMatch("插件详情"), "anything" @ WildcardMatch()])
        ],
        decorators=[
            Permission.require(Permission.MASTER),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def Saya_Des(anything: RegexResult, source: Source, event: MessageEvent):
    target = anything.result.asDisplay().strip()
    loaded_channels = SayaManager.get_loaded_channels()
    keys = list(loaded_channels.keys())
    if target.isdigit():
        keys.sort()
        if not 0 <= int(target) - 1 < len(keys):
            return autoSendMessage(
                event.sender,
                MessageChain.create([Plain(text="错误的编号！请检查后再发送！")]),
                source,
            )
        channel = loaded_channels[keys[int(target) - 1]]
        channel_path = keys[int(target) - 1]
    else:
        for lchannel in loaded_channels.keys():
            if loaded_channels[lchannel]._name == target:
                channel = loaded_channels[lchannel]
                channel_path = lchannel
                break
        else:
            return await autoSendMessage(event.sender, "错误的名称！请检查后再发送！", source)

    return await autoSendMessage(
        event.sender,
        MessageChain.create(
            [
                Plain(text=f"插件名称：{channel._name}\n"),
                Plain(text=f"插件作者：{'、'.join(channel._author)}\n"),
                Plain(text=f"插件描述：{channel._description}\n"),
                Plain(text=f"插件包名：{channel_path}"),
            ]
        ),
    )
