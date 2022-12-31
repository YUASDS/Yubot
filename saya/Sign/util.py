#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
from pathlib import Path
from typing import Optional, Union

import httpx
import ujson
from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont
from pydantic import BaseModel

Ink = Union[str, int, tuple[int, int, int], tuple[int, int, int, int]]

path = Path(__file__).parent.joinpath("teller.txt")
# 读取json文件


addition_path = ujson.load(
    Path(__file__).parent.joinpath("刀.json").open(encoding="utf-8")
)["刀"]

with open(path, mode="r", encoding="utf-8") as s:
    teller = [line.replace("\\n", "\n") for line in s] + addition_path


async def get_qlogo(id: int) -> bytes:
    """获取QQ头像
    Args:
        id (int): QQ号
    Returns:
        bytes: 图片二进制数据
    """
    url = f"http://q1.qlogo.cn/g?b=qq&nk={id}&s=640"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url=url)
    return resp.content


async def get_hotokoto() -> str:
    # url = "https://api.dzzui.com/api/yiyan"
    # async with httpx.AsyncClient() as client:
    #     try:
    #         hotokoto = await client.get(url=url)
    #     except Exception as e:
    #         hotokoto = "一言获取失败"
    #         print(e)
    #     else:
    #         hotokoto = hotokoto.text
    return random.choice(teller)


def get_time() -> str:
    """获取格式化后的当前时间"""
    return time.strftime("%Y/%m/%d/ %p%I:%M:%S", time.localtime())


def cut_text(
    font: FreeTypeFont,
    origin: str,
    chars_per_line: int,
):
    """将单行超过指定长度的文本切割成多行
    Args:
        font (FreeTypeFont): 字体
        origin (str): 原始文本
        chars_per_line (int): 每行字符数（按全角字符算）
    """
    target = ""
    start_symbol = "[{<(【《（〈〖［〔“‘『「〝"
    end_symbol = ",.!?;:]}>)%~…，。！？；：】》）〉〗］〕”’～』」〞"
    line_width = chars_per_line * font.getlength("一")
    for i in origin.splitlines(False):
        if i == "":
            target += "\n"
            continue
        j = 0
        for ind, elem in enumerate(i):
            if i[j : ind + 1] == i[j:]:
                target += i[j : ind + 1] + "\n"
                continue
            elif font.getlength(i[j : ind + 1]) <= line_width:
                continue
            elif ind - j > 3:
                if i[ind] in end_symbol and i[ind - 1] != i[ind]:
                    target += i[j : ind + 1] + "\n"
                    j = ind + 1
                    continue
                elif i[ind] in start_symbol and i[ind - 1] != i[ind]:
                    target += i[j:ind] + "\n"
                    continue
            target += i[j:ind] + "\n"
            j = ind
    return target.rstrip()


def exp_bar(
    w: int, h: int, rato: float, bg: Ink = "black", fg: Ink = "white"
) -> Image.Image:
    """获取一个经验条的图片对象
    Args:
        w (int): 宽度
        h (int): 高度
        rato (float): 比例
        bg (_Ink): 背景颜色
        fg (_Ink): 前景颜色
    Returns:
        Image.Image: 图片对象
    """
    origin_w = w
    origin_h = h
    w *= 4
    h *= 4
    bar_canvase = Image.new("RGBA", (w, h), "#00000000")
    bar_draw = ImageDraw.Draw(bar_canvase)
    # draw background
    exp_bar_draw(bar_draw, h, bg, w)
    # draw exp bar
    n_w = w * rato if rato <= 1 else w
    exp_bar_draw(bar_draw, h, fg, n_w)
    return bar_canvase.resize((origin_w, origin_h), Image.LANCZOS)


def exp_bar_draw(bar_draw, h, fill, arg3):
    """
    draw exp
    """
    bar_draw.ellipse((0, 0, h, h), fill=fill)
    bar_draw.ellipse((arg3 - h, 0, arg3, h), fill=fill)
    bar_draw.rectangle((h // 2, 0, arg3 - h // 2, h), fill=fill)


class Reward(BaseModel):
    """奖励"""

    name: Optional[str] = None
    """奖励名称"""

    num: int
    """奖励数量"""

    ico: Optional[Union[str, Path]]
    """奖励图标"""
