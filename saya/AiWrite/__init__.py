import os
import re

from graia.saya import Saya, Channel
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Plain, At
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    WildcardMatch,
    RegexResult,
)

from util.control import Permission, Interval, Rest
from util.sendMessage import safeSendGroupMessage
from config import COIN_NAME
from database.db import reduce_gold
from .novel_data import get_cont_continuation, load_config, save_config

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)

bcc = saya.broadcast
inc = InterruptControl(bcc)

config_path = os.path.join(os.path.dirname(__file__), "naconfig.json")

if not os.path.exists(config_path):
    with open(config_path, "w", encoding="utf8") as f:
        f.write("{}")
config = load_config(config_path)

sv_help = """
基于彩云小梦的小说续写功能
[/续写 标题(可选)|续写内容] 彩云小梦续写小说
[/默认续写迭代 (迭代次数)] 修改本群默认续写迭代次数，默认为3
[/默认续写模型 (模型名)] 修改本群默认续写模型，默认为小梦0号
[/设置续写apikey] 设置本群apikey，具体指南请发送该命令查看
""".strip()

model_list = {
    "小梦0号": "60094a2a9661080dc490f75a",
    "小梦1号": "601ac4c9bd931db756e22da6",
    "纯爱小梦": "601f92f60c9aaf5f28a6f908",
    "言情小梦": "601f936f0c9aaf5f28a6f90a",
    "玄幻小梦": "60211134902769d45689bf75",
}
# default_key="602c8c0826a17bcd889faca7"    #already banned

templete = {"iter": 3, "model": "小梦0号", "token": ""}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [
                    FullMatch("/续写"),
                    "text" @ WildcardMatch().flags(re.DOTALL),
                ]
            )
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def main(group: Group, member: Member, text: RegexResult):

    gid = str(group.id)
    if gid not in config:
        config[gid] = templete
        save_config(config, config_path)
    if text.matched:
        if not config[gid]["token"]:
            return await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [At(member.id), Plain("本群续写apikey未设置！请使用‘设置续写apikey’指令设置本群apikey！")]
                ),
            )

        mid = model_list[config[gid]["model"]]
        iter = config[gid]["iter"]
        token = config[gid]["token"]
        text = text.result.asDisplay()
        title = ""
        if "|" in text:
            title = text.split("|")[0]
            text = text.split("|")[1]
        if not await reduce_gold(str(member.id), 5):
            await safeSendGroupMessage(
                group,
                MessageChain.create([At(member.id), Plain(f" 前辈似乎没有足够的{COIN_NAME}哦。")]),
            )
        else:
            try:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id), Plain("\n稍等片刻，千音这就开始哦~")]),
                )
                res = await get_cont_continuation(
                    text, token, title=title, iter=iter, mid=mid
                )
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id), Plain("\n" + res)]),
                )
            except Exception as e:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(member.id), f"\n发生错误：{e}"]),
                )
    else:
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id), f"\n{sv_help}"]),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("/设置续写apikey"), "text" @ WildcardMatch()])
        ],
        decorators=[
            Permission.restricter(func),
            Permission.require(),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def APIKEY(group: Group, member: Member, text: RegexResult):

    if text.matched:
        gid = str(group.id)
        if gid not in config:
            config[gid] = templete
            save_config(config, config_path)
        text = text.result.asDisplay()

        try:
            if len(text) != 24:
                raise
            int(text, base=16)
        except Exception:
            return await safeSendGroupMessage(
                group,
                MessageChain.create([At(member.id), Plain("\napikey格式有误!")]),
            )
        config[gid]["token"] = str(text)
        save_config(config, config_path)
        await safeSendGroupMessage(
            group,
            MessageChain.create([At(member.id), "\n本群apikey已设置！"]),
        )
    else:
        await safeSendGroupMessage(
            group,
            MessageChain.create(
                [
                    At(member.id),
                    "要设置apikey请在此命令后加上key！\n\napikey获取教程：\n"
                    "1、前往 http://if.caiyunai.com/dream "
                    "注册彩云小梦用户；\n"
                    "2、注册完成后，在 chrome 浏览器地址栏输入(或者按下F12在控制台输入) "
                    "javascript:alert(localStorage.cy_dream_user)，（前缀javascript需单独复制），"
                    "弹出窗口中的uid即为apikey\n\n"
                    "或查看https://yuasds.gitbook.io/yin_book/functions/graia/xu-xie",
                ]
            ),
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("/默认续写迭代"), "text" @ WildcardMatch()])],
        decorators=[
            Permission.restricter(func),
            Permission.require(Permission.GROUP_ADMIN),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def novel_iteration(group: Group, member: Member, text: RegexResult):
    gid = str(group.id)
    if text.matched:
        if gid not in config:
            config[gid] = templete
            save_config(config, config_path)
        text = text.result.asDisplay().strip()
        if text.isdigit():
            if int(text) > 5:
                await safeSendGroupMessage(
                    group, MessageChain.create([At(member.id), "\n最高只能迭代5次~"])
                )
                text = 5
            if int(text) < 1:
                await safeSendGroupMessage(
                    group, MessageChain.create([At(member.id), "\n最少迭代1次~"])
                )
                text = 1
            config[gid]["iter"] = int(text)
            save_config(config, config_path)
            await safeSendGroupMessage(
                group, MessageChain.create([At(member.id), f"\n本群默认续写迭代次数已修改为{text}次！"])
            )
        else:
            await safeSendGroupMessage(
                group, MessageChain.create([At(member.id), "\n迭代次数仅接受纯数字，请重新输入！"])
            )
    else:
        await safeSendGroupMessage(
            group,
            MessageChain.create(
                [At(member.id), f'\n请输入默认续写迭代次数！当前默认迭代次数：{config[gid]["iter"]}']
            ),
        )

    return


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("/默认续写模型"), "text" @ WildcardMatch()])],
        decorators=[
            Permission.restricter(func),
            Permission.require(Permission.GROUP_ADMIN),
            Rest.rest_control(),
            Interval.require(),
        ],
    )
)
async def on_prefix(group: Group, member: Member, text: RegexResult):

    gid = str(group.id)
    if text.matched:

        if gid not in config:
            config[gid] = templete
            save_config(config, config_path)
        text = text.result.asDisplay().strip()
        if text in model_list:
            config[gid]["model"] = text
            save_config(config, config_path)
            await safeSendGroupMessage(
                group, MessageChain.create([At(member.id), f"\n本群默认续写模型已修改为{text}！"])
            )
        else:
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [
                        At(member.id),
                        f"\n未找到该模型，请重新输入！\n 可用模型：{','.join(model_list.keys())}",
                    ]
                ),
            )
    else:
        mods = config[gid]["model"]
        await safeSendGroupMessage(
            group,
            MessageChain.create(
                [
                    At(member.id),
                    f"\n请选择默认续写模型！当前模型：{mods}\n 可用模型：{','.join(model_list.keys())}",
                ]
            ),
        )

    return
