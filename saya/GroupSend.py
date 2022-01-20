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

saya = Saya.current()
channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[
            Twilight({"keys": RegexMatch("【[\s\S]+】"), "anythings": WildcardMatch()})
        ],
        decorators=[Permission.require(), Rest.rest_control(), Interval.require()],
    )
)
async def main(group: Group, anythings: WildcardMatch, source: Source,keys:RegexMatch):

    if (
        yaml_data["Saya"]["GroupSend"]["Disabled"]
        and group.id != yaml_data["Basic"]["Permission"]["DebugGroup"]
    ):
        return
    # elif "Yinglish" in group_data[str(group.id)]["DisabledFunc"]:
    #     return
    if keys.matched:
        keys=keys.result.asDisplay()
        if keys in group_key:
            send_group=group_key[keys]
        else:
            await safeSendGroupMessage(group, MessageChain.create("密钥错误"))
        

    if anythings.matched:
        saying = anythings.result.asDisplay()
        if len(saying) < 200:
            await safeSendGroupMessage(
                group, MessageChain.create("已成功发送信息:\n",saying))
            await safeSendGroupMessage(
                send_group, MessageChain.create("收到信息:\n",saying))
        else:
            await safeSendGroupMessage(group, MessageChain.create("文字过长"))
    else:
        await safeSendGroupMessage(group, MessageChain.create("未输入文字"))


# if "get" in group_key:
#     print(group_key["get"])
# if __name__=="__main__":
#     print("yes")