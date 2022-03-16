import json
import httpx
import random
import asyncio
import os

from pathlib import Path
from loguru import logger
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.scheduler.timers import crontabify
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.scheduler.saya.schema import SchedulerSchema
from graia.saya.builtins.broadcast.schema import ListenerSchema

from config import yaml_data

from util.control import Permission, Interval
from util.sendMessage import safeSendGroupMessage

saya = Saya.current()
channel = Channel.current()

DATA_FILE = Path(__file__).parent.joinpath("chat_data.json")
DATA: dict = json.loads(DATA_FILE.read_text(encoding="utf-8"))
func = os.path.dirname(__file__).split("\\")[-1]


async def update_data():
    global DATA
    logger.info("正在更新词库")
    root = httpx.get(
        "https://raw.fastgit.org/Kyomotoi/AnimeThesaurus/main/data.json",
        verify=False,
    ).json()
    DATA_FILE.write_text(
        json.dumps(root, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    DATA = root


if not yaml_data["Saya"]["ChatMS"]["Disabled"] and not DATA_FILE.exists():
    logger.info("正在初始化词库")
    asyncio.run(update_data())


@channel.use(SchedulerSchema(crontabify("0 0 * * *")))
async def updateDict():
    if not yaml_data["Saya"]["ChatMS"]["Disabled"]:
        await update_data()
        logger.info(f"已更新完成聊天词库，共计：{len(DATA)}条")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[Permission.require(), Permission.restricter(func)],
    )
)
async def main(group: Group, member: Member, message: MessageChain):

    if (
        message.has(At)
        and message.getFirst(At).target == yaml_data["Basic"]["MAH"]["BotQQ"]
    ):
        try:
            saying = message.getFirst(Plain).text
            for key, value in DATA.items():
                if key in saying:
                    await Interval.manual(member.id)
                    return await safeSendGroupMessage(
                        group,
                        MessageChain.create([Plain(random.choice(value))]),
                    )

        except IndexError:
            pass
