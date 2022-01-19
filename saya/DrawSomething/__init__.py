import json
import time
import secrets
import asyncio

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.broadcast.interrupt.waiter import Waiter
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Friend, Group, Member
from graia.broadcast.interrupt import InterruptControl
from graia.ariadne.message.element import Source, Plain, At
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.event.lifecycle import ApplicationShutdowned
from graia.ariadne.event.message import GroupMessage, FriendMessage
from graia.ariadne.message.parser.twilight import Twilight, FullMatch, WildcardMatch

from util.control import Permission, Interval
from util.sendMessage import safeSendGroupMessage
from config import yaml_data, group_data, COIN_NAME
from database.db import add_answer, reduce_gold, add_gold


saya = Saya.current()
channel = Channel.current()
bcc = saya.broadcast
inc = InterruptControl(bcc)

WORD = json.loads(Path(__file__).parent.joinpath("word.json").read_text("UTF-8"))
MEMBER_RUNING_LIST = []
GROUP_RUNING_LIST = []
GROUP_GAME_PROCESS = {}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": FullMatch("你画我猜")})],
        decorators=[Permission.require(), Interval.require(60)],
    )
)
async def main(app: Ariadne, group: Group, member: Member, source: Source):

    # 判断插件是否处于禁用状态
    if (
        yaml_data["Saya"]["DrawSomething"]["Disabled"]
        and group.id != yaml_data["Basic"]["Permission"]["DebugGroup"]
    ):
        return
    elif "DrawSomething" in group_data[str(group.id)]["DisabledFunc"]:
        return

    # 判断用户是否正在游戏中
    if member.id in MEMBER_RUNING_LIST:
        return
    else:
        MEMBER_RUNING_LIST.append(member.id)

    # 判断私信是否可用
    try:
        await app.sendFriendMessage(
            member.id,
            MessageChain.create([Plain(f"本消息仅用于测试私信是否可用，无需回复\n{time.time()}")]),
        )
    except Exception:
        await safeSendGroupMessage(
            group,
            MessageChain.create(
                [
                    Plain(
                        f"由于你未添加好友，暂时无法发起你画我猜，请自行添加 {yaml_data['Basic']['BotName']} 好友，用于发送题目"
                    )
                ]
            ),
        )
        MEMBER_RUNING_LIST.remove(member.id)
        return

    # 请求确认中断
    @Waiter.create_using_function(
        listening_events=[GroupMessage], using_decorators=[Permission.require()]
    )
    async def confirm(
        confirm_group: Group,
        confirm_member: Member,
        confirm_message: MessageChain,
        confirm_source: Source,
    ):
        if all([confirm_group.id == group.id, confirm_member.id == member.id]):
            saying = confirm_message.asDisplay()
            if saying == "是":
                return True
            elif saying == "否":
                return False
            else:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create([At(confirm_member.id), Plain("请发送是或否来进行确认")]),
                    quote=confirm_source,
                )

    # 等待答案中断
    @Waiter.create_using_function(
        listening_events=[GroupMessage], using_decorators=[Permission.require()]
    )
    async def start_game(
        submit_answer_group: Group,
        submit_answer_member: Member,
        submit_answer_message: MessageChain,
        submit_answer_source: Source,
    ):
        group_id = GROUP_GAME_PROCESS[group.id]
        owner = group_id["owner"]
        question = group_id["question"].upper()
        question_len = len(question)
        saying = submit_answer_message.asDisplay().upper()
        saying_len = len(saying)

        if all([submit_answer_member.id == owner, saying in ["终止", "取消", "结束"]]):
            return False

        if all(
            [
                submit_answer_group.id == group.id,
                submit_answer_member.id != owner,
                saying_len == question_len,
            ]
        ):
            if submit_answer_member.id not in group_id["player"]:
                GROUP_GAME_PROCESS[group.id]["player"][submit_answer_member.id] = 1
            if group_id["player"][submit_answer_member.id] < 9:
                talk_num = group_id["player"][submit_answer_member.id] + 1
                GROUP_GAME_PROCESS[group.id]["player"][
                    submit_answer_member.id
                ] = talk_num
                if saying == question:
                    return [submit_answer_member, submit_answer_source]
            elif group_id["player"][submit_answer_member.id] == 9:
                await safeSendGroupMessage(
                    group,
                    MessageChain.create(
                        [At(submit_answer_member.id), Plain("你的本回合答题机会已用尽")]
                    ),
                    quote=submit_answer_source,
                )

    # 如果当前群有一个正在进行中的游戏
    if group.id in GROUP_RUNING_LIST:
        if group.id not in GROUP_GAME_PROCESS:
            await safeSendGroupMessage(
                group,
                MessageChain.create([At(member.id), Plain(" 本群正在请求确认开启一场游戏，请稍候")]),
                quote=source.id,
            )
        else:
            owner = GROUP_GAME_PROCESS[group.id]["owner"]
            owner_name = (await app.getMember(group, owner)).name
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [
                        At(member.id),
                        Plain(" 本群存在一场已经开始的游戏，请等待当前游戏结束"),
                        Plain(f"\n发起者：{str(owner)} | {owner_name}"),
                    ]
                ),
                quote=source.id,
            )

    # 新游戏创建流程
    else:
        GROUP_RUNING_LIST.append(group.id)
        await safeSendGroupMessage(
            group,
            MessageChain.create([Plain(f"是否确认在本群开启一场你画我猜？这将消耗你 4 个{COIN_NAME}")]),
            quote=source.id,
        )
        try:
            # 新游戏创建完成，进入等待玩家阶段
            if await asyncio.wait_for(inc.wait(confirm), timeout=15):
                question = secrets.choice(WORD["word"])
                GROUP_GAME_PROCESS[group.id] = {
                    "question": question,
                    "owner": member.id,
                    "player": {},
                }
                if not await reduce_gold(str(member.id), 4):
                    GROUP_RUNING_LIST.remove(group.id)
                    del GROUP_GAME_PROCESS[group.id]
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create(
                            [At(member.id), Plain(f" 你的{COIN_NAME}不足，无法开始游戏")]
                        ),
                    )
                else:
                    question_len = len(question)
                    await safeSendGroupMessage(
                        group,
                        MessageChain.create(
                            [
                                Plain(f"本次题目为 {question_len} 个字，请等待 "),
                                At(member.id),
                                Plain(" 在群中绘图"),
                                Plain("\n创建者发送 <取消/终止/结束> 可结束本次游戏"),
                                Plain("\n每人每回合只有 8 次答题机会，请勿刷屏请勿抢答。"),
                            ]
                        ),
                        quote=source.id,
                    )
                    await asyncio.sleep(1)
                    await app.sendFriendMessage(
                        member.id,
                        MessageChain.create(
                            [
                                Plain(
                                    f"本次的题目为：{question}，请在一分钟内\n在群中\n在群中\n在群中\n发送涂鸦或其他形式等来表示该主题"
                                )
                            ]
                        ),
                    )

                    try:
                        result = await asyncio.wait_for(
                            inc.wait(start_game), timeout=180
                        )
                        if result:
                            owner = owner = str(GROUP_GAME_PROCESS[group.id]["owner"])
                            await add_gold(owner, 2)
                            await add_gold(str(result[0].id), 1)
                            await add_answer(str(result[0].id))
                            GROUP_RUNING_LIST.remove(group.id)
                            del GROUP_GAME_PROCESS[group.id]
                            await safeSendGroupMessage(
                                group.id,
                                MessageChain.create(
                                    [
                                        Plain("恭喜 "),
                                        At(result[0].id),
                                        Plain(
                                            f" 成功猜出本次答案，你和创建者分别获得 1 个和 2 个{COIN_NAME}，本次游戏结束"
                                        ),
                                    ]
                                ),
                                quote=result[1],
                            )
                        else:
                            owner = str(GROUP_GAME_PROCESS[group.id]["owner"])
                            await add_gold(owner, 1)
                            GROUP_RUNING_LIST.remove(group.id)
                            del GROUP_GAME_PROCESS[group.id]
                            await safeSendGroupMessage(
                                group,
                                MessageChain.create(
                                    [Plain(f"本次你画我猜已终止，将返还创建者 1 个{COIN_NAME}")]
                                ),
                            )
                    except asyncio.TimeoutError:
                        owner = str(GROUP_GAME_PROCESS[group.id]["owner"])
                        question = GROUP_GAME_PROCESS[group.id]["question"]
                        await add_gold(owner, 1)
                        GROUP_RUNING_LIST.remove(group.id)
                        del GROUP_GAME_PROCESS[group.id]
                        await safeSendGroupMessage(
                            group,
                            MessageChain.create(
                                [
                                    Plain(
                                        f"由于长时间没有人回答出正确答案，将返还创建者 1 个{COIN_NAME}，本次你画我猜已结束"
                                    ),
                                    Plain(f"\n本次的答案为：{question}"),
                                ]
                            ),
                        )

            # 终止创建流程
            else:
                GROUP_RUNING_LIST.remove(group.id)
                await safeSendGroupMessage(group, MessageChain.create([Plain("已取消")]))
        # 如果 15 秒内无响应
        except asyncio.TimeoutError:
            GROUP_RUNING_LIST.remove(group.id)
            await safeSendGroupMessage(group, MessageChain.create([Plain("确认超时")]))

    # 将用户移除正在游戏中
    MEMBER_RUNING_LIST.remove(member.id)


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("添加你画我猜词库"),
                    "anything": WildcardMatch(optional=True),
                }
            )
        ],
    )
)
async def add_word(app: Ariadne, friend: Friend, anything: WildcardMatch):
    if friend.id == yaml_data["Basic"]["Permission"]["Master"]:
        global WORD
        if anything.matched:
            say = anything.result.asDisplay()
            if say not in WORD["word"]:
                word_list = WORD["word"]
                word_list.append(say)
                WORD["word"] = word_list
                with open("./saya/DrawSomething/word.json", "w") as f:
                    json.dump(WORD, f, indent=2, ensure_ascii=False)
                await app.sendFriendMessage(
                    friend,
                    MessageChain.create(f"成功添加你画我猜词库：{say}"),
                )
            else:
                await app.sendFriendMessage(
                    friend,
                    MessageChain.create("词库内已存在该词"),
                )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        inline_dispatchers=[
            Twilight(
                {
                    "head": FullMatch("删除你画我猜词库"),
                    "anything": WildcardMatch(optional=True),
                }
            )
        ],
    )
)
async def remove_word(app: Ariadne, friend: Friend, anything: WildcardMatch):

    if friend.id == yaml_data["Basic"]["Permission"]["Master"]:
        global WORD
        if anything.matched:
            say = anything.result.asDisplay()
            if say in WORD["word"]:
                word_list = WORD["word"]
                word_list.remove(say)
                WORD["word"] = word_list
                with open("./saya/DrawSomething/word.json", "w") as f:
                    json.dump(WORD, f, indent=2, ensure_ascii=False)
                await app.sendFriendMessage(
                    friend,
                    MessageChain.create(f"成功删除你画我猜词库：{say}"),
                )
            else:
                await app.sendFriendMessage(
                    friend,
                    MessageChain.create(
                        "词库内未存在该词",
                    ),
                )


@channel.use(ListenerSchema(listening_events=[ApplicationShutdowned]))
async def groupDataInit():
    for game_group in GROUP_RUNING_LIST:
        if game_group in GROUP_GAME_PROCESS:
            await add_gold(str(GROUP_GAME_PROCESS[game_group]["owner"]), 4)
            await safeSendGroupMessage(
                game_group,
                MessageChain.create(
                    [
                        Plain(
                            f"由于 {yaml_data['Basic']['BotName']} 正在重启，本场你画我猜重置，已补偿4个{COIN_NAME}"
                        )
                    ]
                ),
            )
