import re
import time
import asyncio
import os
import json
from io import BytesIO


import numpy
import jieba.analyse
from pathlib import Path
from PIL import Image as IMG
from graia.saya import Saya, Channel
from graia.ariadne.model import Group, Member
from wordcloud import WordCloud, ImageColorGenerator
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain, Image
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval
from database.usertalk import get_user_talk, get_group_talk

func = os.path.dirname(__file__).split("\\")[-1]


saya = Saya.current()
channel = Channel.current()
channel.name(func)

FUNC = os.path.dirname(__file__).split("\\")[-1]
BASEPATH = Path(__file__).parent
MASK = numpy.array(IMG.open(BASEPATH.joinpath("bgg.jpg")))
FONT_PATH = Path("font").joinpath("sarasa-mono-sc-regular.ttf")
STOPWORDS = BASEPATH.joinpath("stopwords")
CHANGE_PATH = Path(__file__).parent.joinpath("change_words.json")
change_words: dict = json.loads(CHANGE_PATH.read_text(encoding="utf-8"))
RUNNING = 0
RUNNING_LIST = []


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight(["head" @ RegexMatch(r"^查看(个人|本群)词云")])],
        decorators=[
            Permission.restricter(FUNC),
            Permission.require(),
            Interval.require(30),
        ],
    )
)
async def wordcloud(group: Group, member: Member, message: MessageChain):

    global RUNNING, RUNNING_LIST
    pattern = re.compile(r"^查看(个人|本群)词云")
    if match := pattern.match(message.asDisplay()):
        if RUNNING < 5:
            RUNNING += 1
            RUNNING_LIST.append(member.id)
            mode = match.group(1)
            before_week = int(time.time() - 604800)
            if mode == "个人":
                talk_list = await get_user_talk(
                    str(member.id), str(group.id), before_week
                )
            elif mode == "本群":
                talk_list = await get_group_talk(str(group.id), before_week)
            if len(talk_list) < 10:
                await safeSendGroupMessage(
                    group, MessageChain.create([Plain("当前样本量太少了哦~等多一点再来吧~")])
                )
                RUNNING -= 1
                return RUNNING_LIST.remove(member.id)
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [At(member.id), Plain(f" 正在制作词云，一周内共 {len(talk_list)} 条记录")]
                ),
            )
            words = await get_frequencies(talk_list)
            image = await asyncio.to_thread(make_wordcloud, words)
            await safeSendGroupMessage(
                group,
                MessageChain.create(
                    [
                        At(member.id),
                        Plain(f" 前辈需要的{mode}词云已经做好了哦~"),
                        Image(data_bytes=image),
                    ]
                ),
            )
            RUNNING -= 1
            RUNNING_LIST.remove(member.id)
        else:
            await safeSendGroupMessage(
                group, MessageChain.create([Plain("呜....忙...忙不过来了....")])
            )


async def get_frequencies(msg_list):
    text = "\n".join(msg_list)
    words = jieba.analyse.extract_tags(text, topK=800, withWeight=True)
    words = dict(words)
    for key in change_words:
        if key in words and change_words[key] not in words:
            words[change_words[key]] = words.pop(key)
    return dict(words)


def make_wordcloud(words):

    wordcloud = WordCloud(
        font_path=str(FONT_PATH),
        background_color="white",
        mask=MASK,
        max_words=800,
        scale=2,
    )
    wordcloud.generate_from_frequencies(words)
    image_colors = ImageColorGenerator(MASK, default_color=(255, 255, 255))
    wordcloud.recolor(color_func=image_colors)
    # pyplot.imshow(wordcloud.recolor(color_func=image_colors), interpolation="bilinear")
    # pyplot.axis("off")
    image = wordcloud.to_image()
    imageio = BytesIO()
    image.save(imageio, format="JPEG", quality=98)
    return imageio.getvalue()
