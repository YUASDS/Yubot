import time
import random
import asyncio

from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.exception import UnknownTarget
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, MemberInfo, Group
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.element import Plain, Source, Quote, At, Image
from graia.ariadne.message.parser.twilight import (
    Twilight,
    FullMatch,
    ElementMatch,
    WildcardMatch,
)

from .AdminConfig import Agreement
from util.text2image import create_image
from util.control import Rest, Permission
from database.db import add_gold, give_all_gold
from util.sendMessage import safeSendGroupMessage
from config import (
    COIN_NAME,
    yaml_data,
    group_list,
    save_config,
    user_black_list,
    group_black_list,
)

from .AdminConfig import funcList

bot_qq=yaml_data["Basic"]["MAH"]["BotQQ"]


saya = Saya.current()
channel = Channel.current()
funcList = funcList


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("1")])],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def get_botQueue(app: Ariadne, message: MessageChain, source: Source):
    if message.has(Quote):
        messageid = message.getFirst(Quote).id
        try:
            await app.recallMessage(messageid)
            await app.recallMessage(source)
        except PermissionError:
            pass


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("全员充值"),
                "anything": WildcardMatch(optional=True)
            })
        ],
    ))
async def all_recharge(app: Ariadne, friend: Friend, anything: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if anything.matched:
        say = anything.result.asDisplay()
        await give_all_gold(int(say))
        await app.sendFriendMessage(
            friend, MessageChain.create(f"已向所有人充值 {say} 个{COIN_NAME}"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("请输入充值数量"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("充值"),
                "anything": WildcardMatch(optional=True)
            })
        ],
    ))
async def echarge(app: Ariadne, friend: Friend, anything: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if anything.matched:
        saying = anything.result.asDisplay().split()
        if len(saying) == 2:
            await add_gold(saying[0], int(saying[1]))
            await app.sendFriendMessage(
                friend,
                MessageChain.create(
                    f"已向 {saying[0]} 充值 {saying[1]} 个{COIN_NAME}"),
            )
        else:
            await app.sendFriendMessage(friend,
                                        MessageChain.create("缺少充值对象或充值数量"))
    else:
        await app.sendFriendMessage(friend,
                                    MessageChain.create("请输入充值对象和充值数量"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("公告"),
                "anything": WildcardMatch(optional=True)
            })
        ],
    ))
async def Announcement(app: Ariadne, friend: Friend, anything: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    ft = time.time()
    if anything.matched:
        saying = anything.result.asDisplay()
        image = await create_image(saying)
        groupList = ([
            await app.getGroup(yaml_data["Basic"]["Permission"]["DebugGroup"])
        ] if yaml_data["Basic"]["Permission"]["Debug"] else await
                     app.getGroupList())
        await app.sendFriendMessage(
            friend,
            MessageChain.create([
                Plain(f"正在开始发送公告，共有{len(groupList)}个群"),
                Image(data_bytes=image)
            ]),
        )
        for group in groupList:
            if group.id not in [754494359, 871115054]:
                try:
                    await safeSendGroupMessage(
                        group.id,
                        MessageChain.create([
                            Plain(f"公告：{str(group.name)}\n"),
                            Image(data_bytes=image)
                        ]),
                    )
                except Exception as err:
                    await app.sendFriendMessage(
                        yaml_data["Basic"]["Permission"]["Master"],
                        MessageChain.create(
                            [Plain(f"{group.id} 的公告发送失败\n{err}")]),
                    )
                await asyncio.sleep(random.uniform(2, 4))
        tt = time.time()
        times = str(tt - ft)
        await app.sendFriendMessage(
            friend, MessageChain.create([Plain(f"群发已完成，耗时 {times} 秒")]))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("请输入公告内容"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("添加群白名单"),
                    "groupid": WildcardMatch(optional=True)
                }, )
        ],
    ))
async def add_white_group(app: Ariadne, friend: Friend,
                          groupid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if groupid.matched:
        say = groupid.result.asDisplay()
        if say.isdigit():
            if int(say) in group_list["white"]:
                await app.sendFriendMessage(friend,
                                            MessageChain.create("该群已在白名单中"))
            else:
                group_list["white"].append(int(say))
                save_config()
                await app.sendFriendMessage(friend,
                                            MessageChain.create("成功将该群加入白名单"))
        else:
            await app.sendFriendMessage(friend, MessageChain.create("群号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入群号"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("移出群白名单"),
                    "groupid": WildcardMatch(optional=True)
                }, )
        ],
    ))
async def remove_white_group(app: Ariadne, friend: Friend,
                             groupid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if groupid.matched:
        say = groupid.result.asDisplay()
        if say.isdigit():
            if int(say) not in group_list["white"]:
                try:
                    await app.quitGroup(int(say))
                    await app.sendFriendMessage(
                        friend, MessageChain.create("该群未在白名单中，但成功退出"))
                except Exception:
                    await app.sendFriendMessage(
                        friend, MessageChain.create("该群未在白名单中，且退出失败"))
            else:
                group_list["white"].remove(int(say))
                save_config()
                try:
                    await safeSendGroupMessage(
                        int(say), MessageChain.create("该群已被移出白名单，将在3秒后退出"))
                    await asyncio.sleep(3)
                    await app.quitGroup(int(say))
                except UnknownTarget:
                    pass
                await app.sendFriendMessage(friend,
                                            MessageChain.create("成功将该群移出白名单"))
        else:
            await app.sendFriendMessage(friend, MessageChain.create("群号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入群号"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("拉黑用户"),
                    "userid": WildcardMatch(optional=True)
                }, )
        ],
    ))
async def fadd_black_user(app: Ariadne, friend: Friend, userid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if userid.matched:
        say = userid.result.asDisplay()
        if say.isdigit():
            if int(say) in user_black_list:
                await app.sendFriendMessage(
                    friend, MessageChain.create([Plain("该用户已在黑名单中")]))
            else:
                user_black_list.append(int(say))
                save_config()
                await app.sendFriendMessage(
                    friend, MessageChain.create([Plain("成功将该用户加入黑名单")]))
                try:
                    await app.deleteFriend(int(say))
                    await app.sendFriendMessage(
                        friend, MessageChain.create([Plain("已删除该好友")]))
                except Exception as e:
                    await app.sendFriendMessage(
                        friend,
                        MessageChain.create([Plain(f"删除好友失败 {type(e)}")]))
        else:
            await app.sendFriendMessage(friend,
                                        MessageChain.create("用户号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入qq号"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("取消拉黑用户"),
                    "userid": WildcardMatch(optional=True)
                }, )
        ],
    ))
async def fremove_block_user(app: Ariadne, friend: Friend,
                             userid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if userid.matched:
        say = userid.result.asDisplay()
        if say.isdigit():
            if int(say) not in user_black_list:
                await app.sendFriendMessage(friend,
                                            MessageChain.create("该用户未在黑名单中"))
            else:
                user_black_list.remove(int(say))
                save_config()
                await app.sendFriendMessage(friend,
                                            MessageChain.create("成功将该用户移出白名单"))
        else:
            await app.sendFriendMessage(friend,
                                        MessageChain.create("用户号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入qq号"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("拉黑群"),
                "groupid": WildcardMatch(optional=True),
            })
        ],
    ))
async def fadd_group_black(app: Ariadne, friend: Friend,
                           groupid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if groupid.matched:
        say = groupid.result.asDisplay()
        if say.isdigit():
            if int(say) in group_black_list:
                await app.sendFriendMessage(friend,
                                            MessageChain.create("该群已在黑名单中"))
            else:
                group_black_list.append(int(say))
                save_config()
                await app.sendFriendMessage(friend,
                                            MessageChain.create("成功将该群加入黑名单"))
                try:
                    await app.quitGroup(int(say))
                    await app.sendFriendMessage(friend,
                                                MessageChain.create("已退出该群"))
                except Exception as e:
                    await app.sendFriendMessage(
                        friend, MessageChain.create(f"退出群失败 {type(e)}"))
        else:
            await app.sendFriendMessage(friend, MessageChain.create("群号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入群号"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("取消拉黑群"),
                "groupid": WildcardMatch(optional=True)
            })
        ],
    ))
async def fremove_group_black(app: Ariadne, friend: Friend,
                              groupid: WildcardMatch):
    Permission.manual(friend, Permission.MASTER)
    if groupid.matched:
        say = groupid.result.asDisplay()
        if say.isdigit():
            if int(say) not in group_black_list:
                await app.sendFriendMessage(friend,
                                            MessageChain.create("该群未在黑名单中"))
            else:
                group_black_list.remove(int(say))
                save_config()
                await app.sendFriendMessage(friend,
                                            MessageChain.create("成功将该群移出黑名单"))
        else:
            await app.sendFriendMessage(friend, MessageChain.create("群号仅可为数字"))
    else:
        await app.sendFriendMessage(friend, MessageChain.create("未输入群号"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("拉黑用户"),
                    "at": ElementMatch(At, optional=True)
                }, )
        ],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gadd_black_user(app: Ariadne, group: Group, at: ElementMatch):
    if at.matched:
        user = at.result.target
        if user in user_black_list:
            await safeSendGroupMessage(
                group, MessageChain.create([At(user),
                                            Plain(" 已在黑名单中")]))
        else:
            user_black_list.append(user)
            save_config()
            await safeSendGroupMessage(
                group,
                MessageChain.create([Plain("成功将 "),
                                     At(user),
                                     Plain(" 加入黑名单")]))
            try:
                await app.deleteFriend(user)
                await safeSendGroupMessage(group,
                                           MessageChain.create("已删除该好友"))
            except Exception as e:
                await safeSendGroupMessage(
                    group, MessageChain.create(f"删除好友失败 {type(e)}"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("未输入qq号"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("取消拉黑用户"),
                    "at": ElementMatch(At, optional=True)
                }, )
        ],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gremove_block_user(group: Group, at: ElementMatch):
    if at.matched:
        user = at.result.target
        if user not in user_black_list:
            await safeSendGroupMessage(group,
                                       MessageChain.create(f"{user} 未在黑名单中"))
        else:
            user_black_list.remove(user)
            save_config()
            await safeSendGroupMessage(
                group,
                MessageChain.create([Plain("成功将 "),
                                     At(user),
                                     Plain(" 移出黑名单")]))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请at要操作的用户"))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("休息")])],
    ))
async def fset_work(app: Ariadne, friend: Friend):
    Permission.manual(friend, Permission.MASTER)
    Rest.set_sleep(1)
    await app.sendFriendMessage(friend, MessageChain.create([Plain("已进入休息")]))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("工作")])],
    ))
async def fset_rest(app: Ariadne, friend: Friend):
    Permission.manual(friend, Permission.MASTER)
    Rest.set_sleep(0)
    await app.sendFriendMessage(friend, MessageChain.create([Plain("已开始工作")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("休息")])],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gset_work(group: Group):
    Rest.set_sleep(1)
    await safeSendGroupMessage(group, MessageChain.create([Plain("已进入休息")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([FullMatch("工作")])],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gset_rest(group: Group):
    Rest.set_sleep(0)
    await safeSendGroupMessage(group, MessageChain.create([Plain("已开始工作")]))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("群名片修正")])],
    ))
async def group_card_fix(app: Ariadne, friend: Friend):
    Permission.manual(friend, Permission.MASTER)
    grouplits = await app.getGroupList()
    i = 0
    for group in grouplits:
        opt = await app.modifyMemberInfo(
            member=yaml_data["Basic"]["MAH"]["BotQQ"],
            info=MemberInfo(name=yaml_data["Basic"]["BotName"]),
            group=group.id,
        )
        if opt is None:
            i += 1
        else:
            await app.sendFriendMessage(
                friend,
                MessageChain.create(
                    [Plain(f"群 {group.name}（{group.id}）名片修改失败，请检查后重试")]),
            )
            await asyncio.sleep(0.5)
            break
    await app.sendFriendMessage(
        friend, MessageChain.create([Plain(f"共完成 {i} 个群的名片修改。")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("全局关闭"),
                "func": WildcardMatch(optional=True)
            })
        ],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gset_close(group: Group, func: WildcardMatch):

    func_List = funcList.copy()

    if func.matched:
        say = func.result.asDisplay()
        if say.isdigit():
            try:
                sayfunc = func_List[int(say) - 1]
            except IndexError:
                await safeSendGroupMessage(group,
                                           MessageChain.create(f"{say} 不存在"))
            else:
                if yaml_data["Saya"][sayfunc["key"]]["Disabled"]:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create(f"{sayfunc['name']} 已处于全局关闭状态"))
                else:
                    yaml_data["Saya"][sayfunc["key"]]["Disabled"] = True
                    save_config()
                    await safeSendGroupMessage(
                        group, MessageChain.create(f"{sayfunc['name']} 已全局关闭"))
        else:
            await safeSendGroupMessage(group, MessageChain.create("功能编号仅可为数字"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请输入功能编号"))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head": FullMatch("全局开启"),
                "func": WildcardMatch(optional=True)
            })
        ],
        decorators=[Permission.require(Permission.MASTER)],
    ))
async def gset_open(group: Group, func: WildcardMatch):

    func_List = funcList.copy()

    if func.matched:
        say = func.result.asDisplay()
        if say.isdigit():
            try:
                sayfunc = func_List[int(say) - 1]
            except IndexError:
                await safeSendGroupMessage(group,
                                           MessageChain.create(f"{say} 不存在"))
            else:
                if not yaml_data["Saya"][sayfunc["key"]]["Disabled"]:
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create(
                            [Plain(f"{sayfunc['name']} 已处于全局开启状态")]),
                    )
                yaml_data["Saya"][sayfunc["key"]]["Disabled"] = False
                save_config()
                return await safeSendGroupMessage(
                    group,
                    MessageChain.create(
                        [Plain(f"{sayfunc['name']} 已全局开启")]))
        else:
            await safeSendGroupMessage(group, MessageChain.create("功能编号仅可为数字"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("请输入功能编号"))


# @channel.use(
#     ListenerSchema(
#         listening_events=[GroupMessage],
#         inline_dispatchers=[Twilight({"head": FullMatch(".dismiss")})],
#         decorators=[Permission.require(Permission.GROUP_ADMIN)],
#     )
# )
# async def quit_group(app: Ariadne, group: Group):
#     await app.quitGroup(group.id)
#     await app.sendFriendMessage(
#         yaml_data["Basic"]["MAH"]["Friend"],
#         MessageChain.create(f"主动退出群聊 {group.name}({group.id})"),
#     )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("发送协议")])],
    ))
async def user_agreement(app: Ariadne, friend: Friend):
    Permission.manual(friend, Permission.MASTER)
    image = await create_image(Agreement["Agreement"])
    groupList = ([
        await app.getGroup(yaml_data["Basic"]["Permission"]["DebugGroup"])
    ] if yaml_data["Basic"]["Permission"]["Debug"] else await
                 app.getGroupList())
    await app.sendFriendMessage(
        friend,
        MessageChain.create(
            [Plain(f"正在开始发送公告，共有{len(groupList)}个群"),
             Image(data_bytes=image)]),
    )
    for group in groupList:
        if group.id not in [754494359, 871115054]:
            try:
                await safeSendGroupMessage(
                    group.id,
                    MessageChain.create([
                        Plain(f"公告：{str(group.name)}\n"),
                        Image(data_bytes=image)
                    ]),
                )
            except Exception as err:
                await app.sendFriendMessage(
                    yaml_data["Basic"]["Permission"]["Master"],
                    MessageChain.create([Plain(f"{group.id} 的公告发送失败\n{err}")]),
                )
            await asyncio.sleep(random.uniform(2, 4))


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[Twilight([FullMatch("清理小群")])],
    ))
async def clean_group(app: Ariadne, friend: Friend):
    Permission.manual(friend, Permission.MASTER)
    group_list = await app.getGroupList()
    i = 0
    for group in group_list:
        member_count = len(await app.getMemberList(group))
        if member_count < 15:
            if group.id not in group_list["white"]:
                try:
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create(
                            f'{yaml_data["Basic"]["BotName"]} 当前暂不加入群人数低于 15 的群，正在退出'
                        ),
                    )
                    await app.quitGroup(group)
                except Exception as e:
                    await app.sendFriendMessage(
                        yaml_data["Basic"]["Permission"]["Master"],
                        MessageChain.create(
                            f"群 {group.name}({group.id}) 退出失败\n{e}"),
                    )
                else:
                    await app.sendFriendMessage(
                        yaml_data["Basic"]["Permission"]["Master"],
                        MessageChain.create(
                            f"群 {group.name}({group.id}) 退出成功\n当前群人数 {member_count}"
                        ),
                    )
                i += 1
                await asyncio.sleep(0.3)
    await app.sendFriendMessage(
        yaml_data["Basic"]["Permission"]["Master"],
        MessageChain.create(f"本次共清理了 {i}/{len(group_list)} 个群"),
    )