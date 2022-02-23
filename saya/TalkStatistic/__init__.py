import asyncio
import aiohttp
import datetime

from pathlib import Path
from loguru import logger
from graiax import silkcoder
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch
from graia.ariadne.message.element import (
    Image,
    Plain,
    Voice,
    FlashImage,
    MultimediaElement,
)

from util.control import Permission
from database.db import add_talk as add_talk_db
from util.sendMessage import safeSendGroupMessage
from database.usertalk import get_message_analysis, add_talk, archive_exists

from .mapping import get_mapping

# silkcoder.set_ffmpeg_path("saya\\TalkStatistic\\ffmpeg.exe")
saya = Saya.current()
channel = Channel.current()
data_path = Path("archive")

if not data_path.exists():
    logger.warning("存档目录不存在，正在创建")
    data_path.mkdir()
    image = data_path.joinpath("image").mkdir()
    flashimage = data_path.joinpath("flashimage").mkdir()
    voice = data_path.joinpath("voice").mkdir()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight({"head": RegexMatch(r"查看(信|消)息量统计")})],
        decorators=[Permission.require(Permission.MASTER)],
    )
)
async def get_image(group: Group):

    talk_num, time = await get_message_analysis()
    talk_num.reverse()
    time.reverse()
    image = await get_mapping(talk_num, time)

    await safeSendGroupMessage(group, MessageChain.create([Image(data_bytes=image)]))


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def add_talk_word(group: Group, member: Member, message: MessageChain):
    await add_talk_db(str(member.id))
    if message.has(Plain):
        plain_list = message.get(Plain)
        plain = MessageChain.create(plain_list).asDisplay()
        await add_talk(str(member.id), str(group.id), 1, plain)
    elif message.has(Image):
        image_list = message.get(Image)
        for image in image_list:
            image_name = image.id
            await download(image, image_name, "image", 2)
            await add_talk(str(member.id), str(group.id), 2, image_name, image.url)
    elif message.has(FlashImage):
        flash_image = message.getFirst(FlashImage)
        image_name = flash_image.id
        await download(flash_image, image_name, "flashimage", 3)
        await add_talk(str(member.id), str(group.id), 3, image_name, flash_image.url)
    elif message.has(Voice):
        voice = message.getFirst(Voice)
        voice_id = voice.id
        await download(voice, voice_id, "voice", 4)
        await add_talk(str(member.id), str(group.id), 4, voice_id, voice.url)


async def download(element: MultimediaElement, name, path, type):
    if type == 2:
        now_path = data_path.joinpath(path, name[1:4])
    else:
        now_time = datetime.datetime.now()
        now_path = data_path.joinpath(
            path, str(now_time.year), str(now_time.month), str(now_time.day)
        )
    now_path.mkdir(0o755, True, True)
    if not await archive_exists(name, type):
        for _ in range(5):
            try:
                r = await element.get_bytes()
                break
            except aiohttp.ClientResponseError as e:
                logger.warning(f"{name} 下载失败：{str(e)}，正在重试")
                await asyncio.sleep(1)
        else:
            logger.warning(f"{name} 下载失败，已达到最大重试次数")
            return

        if type == 4:
            try:
                now_path.joinpath(f"{name}.mp3").write_bytes(
                    await silkcoder.decode(r, audio_format="mp3")
                )
            except silkcoder.CoderError:
                now_path.joinpath(f"{name}.silk").write_bytes(r)
        else:
            now_path.joinpath(name).write_bytes(r)
    else:
        logger.info(f"已存在的文件 - {name}")
