import json
import asyncio
import os
from loguru import logger

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch


from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest,restrict

DATA_FILE = Path(__file__).parent.joinpath("scene.json")
DATA: dict = json.loads(DATA_FILE.read_text(encoding="utf-8"))

saya = Saya.current()
channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"keys": RegexMatch("-[\s\S]+-")})],
        decorators=[
            Permission.require(),
            Rest.rest_control(),
            Interval.require()
        ],
    ))
async def main(group: Group, member: Member, keys: RegexMatch):

    func=os.path.dirname(__file__).split("\\")[-1]
    if not restrict(func=func,group=group):
        logger.info(f"{func}在{group.id}群不可用")
        return
    if keys.matched:

        keys = keys.result.asDisplay()
        try:
            for key, contain in DATA.items():
                if key == keys:

                    s = contain
                    for SCkey in s:
                        await asyncio.sleep(0.5)
                        await safeSendGroupMessage(
                            group, MessageChain.create(s[SCkey]))

        except IndexError:
            pass


# if "get" in group_key:
#     print(group_key["get"])
# if __name__=="__main__":
#      print(DATA["-市中心-"]["1"])