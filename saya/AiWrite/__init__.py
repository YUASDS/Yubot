import os

from graia.saya import Saya, Channel
from graia.ariadne.model import Member
from graia.ariadne.message.element import Source
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.parser.twilight import RegexResult

from util.sendMessage import autoForwMessage, autoSendMessage
from util.SchemaManager import Schema
from .novel_data import CaiyunAi, model_list
from .config import get_key, set_key

func = os.path.dirname(__file__).split("\\")[-1]

saya = Saya.current()
channel = Channel.current()
channel.name(func)
schema = Schema(channel)

sv_help = """基于彩云小梦的小说续写功能
[/续写(续写内容)] 彩云小梦续写小说
[/剧情选择(数字)] 选择剧情分支
[/设置续写模型(模型名)] 修改本群默认续写彩云小梦模型，默认为小梦0号
[/设置续写apikey] 设置本群apikey，具体指南请发送该命令查看
[/结束续写] 结束本次续写"""
templete = {"iter": 3, "model": "小梦0号", "token": ""}

caiyun_dict: dict[str, CaiyunAi] = {}


@schema.use(("/续写", ["text"]))
async def main(event: MessageEvent, text: RegexResult):
    sender = event.sender
    if not text.result:
        return await autoSendMessage(sender, sv_help)
    if isinstance(sender, Member):
        ai_apikey = get_key("group", sender.group.id)
        num = str(sender.group.id)
    else:
        num = str(sender.id)
        ai_apikey = get_key("friend", sender.id)
    if ai_apikey is None:
        return await autoSendMessage(
            sender, "前辈还没有设置apikey哦~请使用'/设置续写apikey'来设置apikey吧~"
        )
    caiyun = CaiyunAi(ai_apikey)

    caiyun.content = text.result.asDisplay()
    await caiyun.next()
    caiyun_dict[num] = caiyun
    new_list = [
        "当前续写结果：",
        caiyun.content,
        "请选择接下来的剧情分支哦~(使用/剧情选择+数字)",
    ] + caiyun.contents
    await autoForwMessage(sender, new_list, caiyun.model)  # type:ignore


@schema.use(("/剧情选择", {"choose": "\\d+"}))
async def choose(event: MessageEvent, choose: RegexResult, source: Source):
    sender = event.sender
    text = choose.result.asDisplay()  # type:ignore
    res = int(text)
    sender = event.sender
    sender_id = str(sender.group.id) if isinstance(sender, Member) else str(sender.id)
    caiyun = caiyun_dict.get(sender_id, None)
    if caiyun is None:
        return await autoSendMessage(sender, "请先开始续写哦~", source)
    if res > len(caiyun.contents):
        return await autoSendMessage(sender, "选择错误×\n没有这个选项哦~", source)
    caiyun.select(res - 1)
    await caiyun.next()
    new_list = [
        "当前续写结果：",
        caiyun.content,
        "请选择接下来的剧情分支哦~(使用/剧情选择+数字)",
    ] + caiyun.contents
    await autoForwMessage(sender, new_list, caiyun.model)  # type:ignore


@schema.use(("/设置续写apikey", ["text"]))
async def set_apikey(event: MessageEvent, text: RegexResult, source: Source):
    sender = event.sender
    if text.result:
        apikey = text.result.asDisplay()
        try:
            if len(apikey) != 24:
                raise
            int(apikey, base=16)
        except Exception:
            return await autoSendMessage(sender, "apikey不对哦~", source)
        sender_id = (
            str(sender.group.id) if isinstance(sender, Member) else str(sender.id)
        )
        if isinstance(sender, Member):
            set_key("group", sender_id, apikey)
        else:
            set_key("friend", sender_id, apikey)
        await autoSendMessage(sender, "apikey已设置！", source)
    else:
        await autoSendMessage(
            sender,
            "要设置apikey请在此命令后加上key！\n\napikey获取教程：\n1、前往 http://if.caiyunai.com/dream 注册彩云小梦用户；\n2、注册完成后，在 chrome 浏览器地址栏输入(或者按下F12在控制台输入) javascript:alert(localStorage.cy_dream_user)，（前缀javascript也需要复制），弹出窗口中的uid即为apikey",
            source,
        )


@schema.use(("/结束续写"))
async def cancel(event: MessageEvent, source: Source):
    sender = event.sender
    sender_id = str(sender.group.id) if isinstance(sender, Member) else str(sender.id)
    del caiyun_dict[sender_id]
    await autoSendMessage(
        sender,
        "本次续写已经成功结束了哦~",
        source,
    )


@schema.use(("/设置续写模型", ["model"]))
async def set_model(event: MessageEvent, model: RegexResult, source: Source):
    sender = event.sender
    name = model.result.asDisplay()  # type:ignore
    sender_id = str(sender.group.id) if isinstance(sender, Member) else str(sender.id)

    caiyun = caiyun_dict.get(sender_id, None)
    if caiyun is None:
        return await autoSendMessage(sender, "请先开始续写哦~", source)
    if model_list.get(name, None) is None:
        return await autoSendMessage(sender, "模型不存在哦~", source)
    caiyun.model = name
    return await autoSendMessage(sender, f"模型已切换为{name}", source)
