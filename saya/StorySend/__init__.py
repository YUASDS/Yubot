import json

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch, WildcardMatch


from config import yaml_data,group_key
from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest


DATA_FILE = Path(__file__).parent.joinpath("scene.json")
DATA: dict = json.loads(DATA_FILE.read_text(encoding="utf-8"))

saya = Saya.current()
channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({"keys": RegexMatch("-[\s\S]+-")})
        ],
        decorators=[Permission.require(), Rest.rest_control(), Interval.require()],
    )
)
async def main(group: Group, source: Source,keys:RegexMatch):

    if (
        yaml_data["Saya"]["GroupSend"]["Disabled"]
        and group.id != yaml_data["Basic"]["Permission"]["DebugGroup"]
    ):
        return
    # elif "Yinglish" in group_data[str(group.id)]["DisabledFunc"]:
    #     return
    print("ok")
    if source.id != 1787569211:
        return
    print("ok1")
    if keys.matched:
        print("ok2")
        keys=keys.result.asDisplay()
        try:
            for key, value,contain in DATA.items():
                if key == keys:
                    print("ok3")
                    return await safeSendGroupMessage(group, 
                                                      MessageChain.create(contain)
                    )
    
        except IndexError:
            pass

# if "get" in group_key:
#     print(group_key["get"])
# if __name__=="__main__":
#     print("yes")