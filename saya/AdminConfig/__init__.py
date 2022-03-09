import json

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, Image
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    RegexMatch,
    ArgumentMatch,
    WildcardMatch,
)

from util.text2image import create_image
from util.control import Permission, Interval
from util.sendMessage import safeSendGroupMessage
from config import save_config, yaml_data, group_data, COIN_NAME,change_config

saya = Saya.current()
channel = Channel.current()

data = json.loads(
    Path(__file__).parent.joinpath("func.json").read_text(
        encoding="utf-8").replace("$COIN_NAME", COIN_NAME))
funcList = data["funcList"]
funcHelp = data["funcHelp"]
configList = data["configList"]

DisabledFunc = []
for func in funcList:
    if func["default_disabled"]:
        DisabledFunc.append(func["key"])

groupInitData = {
    "DisabledFunc":
    DisabledFunc,
    "EventBroadcast": {
        "Enabled": True,
        "Message": None
    }}
    
Agreement={
    "Agreement":
    "0. 本协议是 骰娘白千音（下统称“千音”）默认服务协议。如果你看到了这句话，意味着你或你的群友应用默认协议，请注意。该协议仅会出现一次。\n"
    "1. 邀请千音、使用千音服务和在群内阅读此协议视为同意并承诺遵守此协议，否则请持有管理员或管理员以上权限的用户使用 .dismiss 移出千音。"
    "邀请千音入群请关闭群内每分钟消息发送限制的设置。\n"
    "2. 不允许禁言、踢出或刷屏等千音的不友善行为，这些行为将会提高千音被制裁的风险。开关千音功能请持有管理员或管理员以上权限的用户使用相应的指令来进行操作。"
    "如果发生禁言、踢出等行为，千音将拉黑该群。\n"
    "3. 千音默认邀请行为已事先得到群内同意，因而会自动同意群邀请。因擅自邀请而使千音遭遇不友善行为时，邀请者因未履行预见义务而将承担连带责任。\n"
    "4. 千音在运行时将对群内信息进行监听及记录，并将这些信息保存在服务器内，以便功能正常使用。\n"
    "5. 禁止将千音用于违法犯罪行为。\n"
    "6. 禁止使用千音提供的功能来上传或试图上传任何可能导致的资源污染的内容，包括但不限于色情、暴力、恐怖、政治、色情、赌博等内容。如果发生该类行为，千音将停止对该用户提供所有服务。\n"
    "6. 对于设置敏感昵称等无法预见但有可能招致言论审查的行为，千音可能会出于自我保护而拒绝提供服务。\n"
    "7. 由于技术以及资金原因，我们无法保证千音 100% 的时间稳定运行，可能不定时停机维护或遭遇冻结，对于该类情况恕不通知，敬请谅解。"
    "临时停机的千音不会有任何响应，故而不会影响群内活动，此状态下仍然禁止不友善行为。\n"
    "8. 对于违反协议的行为，千音将视情况终止对用户和所在群提供服务，并将不良记录共享给其他服务提供方。黑名单相关事宜可以与服务提供方协商，但最终裁定权在服务提供方。\n"
    "9. 本协议内容随时有可能改动。\n"
    "10. 千音提供的服务是完全免费的，欢迎通过其他渠道进行支持。\n"
    "11. 本服务最终解释权归服务提供方所有。"
}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight([FullMatch("功能")], {"func": WildcardMatch()})
        ],
        decorators=[Permission.require(),
                    Interval.require(5)],
    ))
async def funchelp(group: Group, func: WildcardMatch):
    # sourcery skip: use-fstring-for-concatenation
    if func.matched:
        num = func.result.asDisplay().strip()
        if num.isdigit():
            func_id = int(num) - 1
            if func_id >= len(funcList):
                return await safeSendGroupMessage(
                    group,
                    MessageChain.create("没有这个功能，请输入菜单查看所有功能"),
                )
        elif num in funcHelp:
            func_id = [*funcHelp].index(num)
        else:
            return await safeSendGroupMessage(
                group, MessageChain.create([Plain("功能编号仅可为数字或其对应的功能名")]))
        sayfunc = funcList[func_id]["name"]
        funckey = funcList[func_id]["key"]
        funcGlobalDisabled = yaml_data["Saya"][funckey]["Disabled"]
        funcGroupDisabledList = funckey in group_data[str(
            group.id)]["DisabledFunc"]
        if funcGlobalDisabled or funcGroupDisabledList:
            return await safeSendGroupMessage(
                group, MessageChain.create([Plain("该功能暂不开启")]))
        help = str(sayfunc + f"\n\n{funcHelp[sayfunc]['instruction']}" +
                   "\n \n>>> 用法 >>>\n" + funcHelp[sayfunc]["usage"] +
                   "\n \n>>> 注意事项 >>>\n" + funcHelp[sayfunc]["options"] +
                   "\n \n>>> 示例 >>>\n" + funcHelp[sayfunc]["example"])
        image = await create_image(help)
        await safeSendGroupMessage(
            group, MessageChain.create([Image(data_bytes=image)]))
    else:
        await safeSendGroupMessage(group,
                                   MessageChain.create([Plain("请输入功能编号")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({"head": RegexMatch(r"^[。\./]?help$|^帮助$|^菜单$")})
        ],
        decorators=[Permission.require(),
                    Interval.require()],
    ))
async def help(group: Group):
    msg = (
        f"{yaml_data['Basic']['BotName']} 群菜单 / {str(group.id)}\n{group.name}\n"
        + "========================================================")
    for i, func in enumerate(funcList, start=1):
        funcname = func["name"]
        funckey = func["key"]
        if funckey not in yaml_data["Saya"]:
            yaml_data["Saya"][funckey] = {"Disabled": False}
            change_config(yaml_data)
        funcGlobalDisabled = yaml_data["Saya"][funckey]["Disabled"]
        funcGroupDisabledList = func["key"] in group_data[str(
            group.id)]["DisabledFunc"]
        if funcGlobalDisabled:
            statu = "【全局关闭】"
        elif funcGroupDisabledList:
            statu = "【  关闭  】"
        else:
            statu = "            "
        si = f" {str(i)}" if i < 10 else str(i)
        msg += f"\n{si}  {statu}  {funcname}"
    msg += str(
        "\n========================================================" +
        "\n详细查看功能使用方法请发送 功能 <id>，例如：功能 1" + "\n管理员可发送 开启功能/关闭功能 <功能id> " +
        "\n所有功能均无需@" +
        f"\n更多功能待开发，如有特殊需求可以向 {yaml_data['Basic']['Permission']['Master']} 询问")
    image = await create_image(msg, 80)
    await safeSendGroupMessage(group,
                               MessageChain.create([Image(data_bytes=image)]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head":
                FullMatch("开启功能"),
                "all":
                ArgumentMatch(
                    "-all",
                    action="store_true",
                    optional=True,
                ),
                "func":
                WildcardMatch(optional=True),
            })
        ],
        decorators=[
            Permission.require(Permission.GROUP_ADMIN),
            Interval.require(5)
        ],
    ))
async def on_func(group: Group, func: WildcardMatch, all: ArgumentMatch):
    if func.matched:
        say = func.result.asDisplay().strip()
        if say.isdigit():
            sayfunc = int(say) - 1
            try:
                func = funcList[sayfunc]
            except IndexError:
                await safeSendGroupMessage(
                    group, MessageChain.create([Plain("该功能编号不存在")]))
            else:
                funcname = func["name"]
                funckey = func["key"]
                funcGlobalDisabled = yaml_data["Saya"][funckey]["Disabled"]
                funcGroupDisabled = (func["key"] in group_data[str(
                    group.id)]["DisabledFunc"])
                funcDisabledList = group_data[str(group.id)]["DisabledFunc"]
                if funcGlobalDisabled:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{funcname} 当前处于全局禁用状态")]))
                elif funcGroupDisabled:
                    funcDisabledList.remove(funckey)
                    group_data[str(
                        group.id)]["DisabledFunc"] = funcDisabledList
                    save_config()
                    await safeSendGroupMessage(
                        group, MessageChain.create(f"{funcname} 已开启"))
                else:
                    await safeSendGroupMessage(
                        group, MessageChain.create(f"{funcname} 已处于开启状态"))
        else:
            await safeSendGroupMessage(group, MessageChain.create("功能编号仅可为数字"))
    elif all.matched:
        i = 0
        funcDisabledList = group_data[str(group.id)]["DisabledFunc"]
        for func in funcList:
            funcname = func["name"]
            funckey = func["key"]
            funcGlobalDisabled = yaml_data["Saya"][funckey]["Disabled"]
            funcGroupDisabled = func["key"] in group_data[str(
                group.id)]["DisabledFunc"]
            if not funcGlobalDisabled and funcGroupDisabled:
                funcDisabledList.remove(funckey)
                i += 1
        group_data[str(group.id)]["DisabledFunc"] = funcDisabledList
        save_config()
        await safeSendGroupMessage(group,
                                   MessageChain.create(f"已一键开启 {i} 个功能"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请输入功能编号"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head":
                FullMatch("关闭功能"),
                "all":
                ArgumentMatch(
                    "-all",
                    action="store_true",
                    optional=True,
                ),
                "func":
                WildcardMatch(optional=True),
            })
        ],
        decorators=[
            Permission.require(Permission.GROUP_ADMIN),
            Interval.require(5)
        ],
    ))
async def off_func(group: Group, func: WildcardMatch, all: ArgumentMatch):
    if func.matched:
        say = func.result.asDisplay().strip()
        if say.isdigit():
            sayfunc = int(say) - 1
            try:
                func = funcList[sayfunc]
            except IndexError:
                await safeSendGroupMessage(
                    group, MessageChain.create([Plain("该功能编号不存在")]))
            else:
                funcname = func["name"]
                funckey = func["key"]
                funcCanDisabled = func["can_disabled"]
                funcDisabledList = group_data[str(group.id)]["DisabledFunc"]
                funcGroupDisabled = func["key"] in funcDisabledList
                if not funcCanDisabled:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{funcname} 无法被关闭")]))
                elif not funcGroupDisabled:
                    funcDisabledList.append(funckey)
                    group_data[str(
                        group.id)]["DisabledFunc"] = funcDisabledList
                    save_config()
                    await safeSendGroupMessage(
                        group, MessageChain.create([Plain(f"{funcname} 已关闭")]))
                else:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{funcname} 已处于关闭状态")]))
        else:
            await safeSendGroupMessage(group, MessageChain.create("功能编号仅可为数字"))
    elif all.matched:
        i = 0
        funcDisabledList = group_data[str(group.id)]["DisabledFunc"]
        for func in funcList:
            funcname = func["name"]
            funckey = func["key"]
            funcCanDisabled = func["can_disabled"]
            funcGroupDisabled = func["key"] in funcDisabledList
            if funcCanDisabled and not funcGroupDisabled:
                funcDisabledList.append(funckey)
                i += 1
        group_data[str(group.id)]["DisabledFunc"] = funcDisabledList
        save_config()
        await safeSendGroupMessage(group,
                                   MessageChain.create(f"已一键关闭 {i} 个功能"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请输入功能编号"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                [FullMatch("群功能")],
                {
                    "reg1":
                    RegexMatch("修改|查看|关闭|开启", optional=True),
                    "reg2":
                    RegexMatch("|".join(x["name"] for x in configList),
                               optional=True),
                    "reg3":
                    WildcardMatch(optional=True),
                },
            )
        ],
        decorators=[
            Permission.require(Permission.GROUP_ADMIN),
            Interval.require(5)
        ],
    ))
async def group_func(group: Group, reg1: RegexMatch, reg2: RegexMatch,
                     reg3: WildcardMatch):

    if reg1.matched:
        ctrl = reg1.result.getFirst(Plain).text
        if ctrl == "修改":
            if reg2.matched:
                configname = reg2.result.getFirst(Plain).text
                for config in configList:
                    if config["name"] == configname:
                        if config["can_edit"]:
                            if reg3.matched:
                                config_Message = reg3.result.getFirst(
                                    Plain).text
                                group_data[str(group.id)][
                                    config["key"]]["Message"] = config_Message
                                save_config()
                                return await safeSendGroupMessage(
                                    group,
                                    MessageChain.create([
                                        Plain(
                                            f"{configname} 已修改为 {config_Message}"
                                        )
                                    ]),
                                )
                            else:
                                return await safeSendGroupMessage(
                                    group,
                                    MessageChain.create([Plain("请输入修改后的值")]))
                        else:
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 不可修改")]),
                            )
                else:
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{configname} 不存在")]))
            else:
                return await safeSendGroupMessage(
                    group, MessageChain.create([Plain("请输入需要修改的配置名称")]))
        elif ctrl == "查看":
            if reg2.matched:
                configname = reg2.result.getFirst(Plain).text
                for config in configList:
                    if config["name"] == configname:
                        config_Message = group_data[str(
                            group.id)][config["key"]]["Message"]
                        if config_Message:
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create([
                                    Plain(
                                        f"{configname} 当前值为 {config_Message}")
                                ]),
                            )
                        else:
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 当前值为 空")]),
                            )
                else:
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{configname} 不存在")]))
            else:
                return await safeSendGroupMessage(
                    group, MessageChain.create([Plain("请输入需要查看的配置名称")]))
        elif ctrl == "关闭":
            if reg2.matched:
                configname = reg2.result.getFirst(Plain).text
                for config in configList:
                    if config["name"] == configname:
                        configkey = config["key"]
                        if group_data[str(group.id)][configkey]["Enabled"]:
                            group_data[str(
                                group.id)][configkey]["Enabled"] = False
                            save_config()
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 已关闭")]))
                        else:
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 已处于关闭状态")]),
                            )
                else:
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{configname} 不存在")]))
            else:
                return await safeSendGroupMessage(
                    group, MessageChain.create([Plain("请输入需要关闭的配置名称")]))
        elif ctrl == "开启":
            if reg2.matched:
                configname = reg2.result.getFirst(Plain).text
                for config in configList:
                    if config["name"] == configname:
                        configkey = config["key"]
                        if not group_data[str(group.id)][configkey]["Enabled"]:
                            group_data[str(
                                group.id)][configkey]["Enabled"] = True
                            save_config()
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 已开启")]))
                        else:
                            return await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"{configname} 已处于开启状态")]),
                            )
                else:
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(f"{configname} 不存在")]))
            else:
                return await safeSendGroupMessage(
                    group, MessageChain.create([Plain("请输入需要开启的配置名称")]))
        else:
            return await safeSendGroupMessage(
                group, MessageChain.create([Plain("请输入修改|查看|关闭|开启")]))
    else:
        msg = "当前可调整的群功能有："

        for config in configList:
            configname = config["name"]
            configkey = config["key"]
            configstatus = group_data[str(group.id)][configkey]["Enabled"]
            configstatus_str = "已开启" if configstatus else "已关闭"

            msg += f"\n{configname}    {configstatus_str}"

        msg += "\n如需修改请发送 群功能 <操作> <功能名>，例如：群功能 关闭 入群欢迎\n可用操作：修改、查看、关闭、开启"

        image = await create_image(msg, cut=80)
        return await safeSendGroupMessage(
            group, MessageChain.create([Image(data_bytes=image)]))
