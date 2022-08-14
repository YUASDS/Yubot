import random
import itertools
from io import BytesIO
from pathlib import Path


import ujson
from loguru import logger
from PIL import Image, ImageDraw, ImageFont
from util.strings import changeCountL, getCutStr, cut_text

DATA: dict = ujson.loads(
    Path(__file__).parent.joinpath("Tarot.json").read_text(encoding="utf-8")
)
CARD_LIST = [
    "愚者",
    "魔术师",
    "女祭司",
    "女皇",
    "皇帝",
    "教皇",
    "恋人",
    "战车",
    "力量",
    "隐者",
    "命运之轮",
    "正义",
    "倒吊人",
    "死神",
    "节制",
    "恶魔",
    "塔",
    "星星",
    "月亮",
    "太阳",
    "审判",
    "世界",
]

TAROT_DATA = {
    i: Image.open(Path(__file__).parent.joinpath(f"./images/{i}.jpg")).resize(
        (120, 240)
    )
    for i in list(DATA)
}

FONT = ImageFont.truetype("font/FZDBSJW.TTF", size=36)


BG = Image.open(Path(__file__).parent.joinpath("./images/背景.png")).resize((2000, 1000))
TAROT_DATA["背面"] = Image.open(Path(__file__).parent.joinpath("./images/背面.png")).resize(
    (120, 240)
)
CANVAS = Image.new("RGB", (2000, 1000), "#FFFFFF")
CANVAS.paste(BG)


def draw_tarot(list_tarot: list[str]):
    """list_tarot用于存储塔罗牌名称"""

    canvas = CANVAS.copy()
    draw = ImageDraw.Draw(canvas)
    a = 0
    for j, i in itertools.product(range(2), range(7)):

        card = TAROT_DATA[list_tarot[a]]
        a += 1
        sr = changeCountL(a)
        canvas.paste(card, (70 + i * 200, 40 + j * 320))
        start = 95 if len(sr) > 1 else 110
        draw.text(
            (start + (i) * 200, (j + 1) * 320 - 30),
            sr,
            font=FONT,
            color="#3F4C60",
        )
    for i in range(8):
        card = TAROT_DATA[list_tarot[a]]
        a += 1
        sr = changeCountL(a)
        canvas.paste(card, (40 + i * 180, 680))
        start = 50 if len(sr) > 2 else 65
        draw.text(
            (start + i * 180, 920),
            sr,
            font=FONT,
            color="#3F4C60",
        )
    return canvas


def last_draw(list_tarot: list[str]):
    canvas = CANVAS.copy()
    draw = ImageDraw.Draw(canvas)
    count = 0
    for card_name in list_tarot:
        if card_name != "背面":
            offset = 210 if len(card_name) > 4 else 240
            card = TAROT_DATA[card_name]
            canvas.paste(card.resize((300, 600)), (150 + count * 580, 100))
            draw.text(
                (offset + count * 580, 710),
                card_name,
                font=FONT,
                color="#3F4C60",
            )
            draw.text(
                (70 + count * 580, 760),
                cut_text(FONT, getCutStr(DATA[card_name], 100), 13),
                font=FONT,
                color="#3F4C60",
            )
            count += 1
    return canvas


class Tarot:
    def __init__(self, qq: str):
        self.list_tarot = ["背面" for _ in range(22)]
        self.qq = qq
        self.tarot_data: list[dict[str, int]] = [
            {key: random.randint(0, 1)} for key in CARD_LIST
        ]
        random.shuffle(self.tarot_data)
        self.result: list[str] = []
        logger.debug(self.tarot_data)

    def choose(self, num: int):
        key = list(self.tarot_data[num - 1])[0]
        Ty = self.tarot_data[num - 1][key]
        key_result = f"{key}逆位" if Ty else f"{key}正位"
        self.result.append(key_result)
        if key_result not in self.list_tarot:
            self.list_tarot[num - 1] = key_result
        else:
            return
        return key_result, DATA[key_result]


def get_bytes(canvas):
    byte_io = BytesIO()
    canvas.save(
        byte_io,
        format="JPEG",
        quality=90,
        optimize=True,
        progressive=True,
        subsampling=2,
        qtables="web_high",
    )
    return byte_io.getvalue()


if __name__ == "__main__":
    lis = ["魔术师正位", "世界正位", "太阳正位"]
    Tarot("13")
    try:
        res = last_draw(lis)
        res.show()
    except Exception as e:
        logger.exception(e)

    # tar = Tarot("1787")
    # res = draw_tarot(tar.list_tarot)
    # res.show()
    # print(tar.choose(1))
    # res = draw_tarot(tar.list_tarot)
    # res.show()
    # print(tar.choose(5))
    # res = draw_tarot(tar.list_tarot)
    # res.show()
    # print(tar.choose(6))
    # res = draw_tarot(tar.list_tarot)
    # res.show()
# new.save
