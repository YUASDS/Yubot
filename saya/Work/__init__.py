# import os

# import ujson
# from pathlib import Path
# from graia.saya import Saya, Channel
# from graia.ariadne.message.element import Source
# from graia.ariadne.event.message import GroupMessage, MessageEvent, FriendMessage
# from graia.saya.builtins.broadcast.schema import ListenerSchema
# from graia.ariadne.message.parser.twilight import (
#     Twilight,
#     FullMatch,
#     WildcardMatch,
# )

# from util.sendMessage import autoSendMessage
# from util.DaylyRecord import add_data, DATA
# from util.control import Permission
# from database.db import add_favor, get_info, favor

# func = os.path.dirname(__file__).split("\\")[-1]


# saya = Saya.current()
# channel = Channel.current()
# reply = [
#     "千音已经听到前辈的祝福了哦~",
#     "前辈明年也不能忘记千音哦~",
#     "很高兴能和前辈一起度过这一天哦~",
#     "好啦~千音听到了哦~前辈之后也不能忘记哦~",
#     "如果明年的时候，如果前辈忘了千音，千音可是会生气的哦~",
#     "好啦~前辈不用再说了哦，千音已经听到了，明年的时候，前辈也请不要忘记了哦~",
# ]


# @channel.use(
#     ListenerSchema(
#         listening_events=[GroupMessage, FriendMessage],
#         priority=15,
#         inline_dispatchers=[
#             Twilight(
#                 [
#                     "head" @ FullMatch("千音生日快乐"),
#                     "anythings" @ WildcardMatch(),
#                 ]
#             )
#         ],
#         decorators=[
#             Permission.restricter(func),
#         ],
#     )
# )
# async def main(source: Source, event: MessageEvent):
#     qid = str(event.sender.id)
#     if DATA.get(qid) is None or DATA[qid].get("birthday") is None:
#         add_data(qid, "birthday", 0)
#         await add_favor(qid, 15, True)

#         await autoSendMessage(
#             event.sender,
#             "“好的~感谢前辈的祝福哦~和之前一样，以后前辈也会陪着千音的，对吧？”少女笑着说道，随后拉起你的手“走吧一起去吃蛋糕吧~”",
#         )
#     else:
#         times = DATA[qid].get("birthday")
#         user_info = await get_info(qid)
#         favor_level = favor(user_info.favor).level
#         if len(reply) > times > 3 and favor_level > 4:
#             await autoSendMessage(event.sender, reply[times])
#         else:
#             await autoSendMessage(event.sender, reply[-1])
#     """"""
