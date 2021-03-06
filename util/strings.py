import re
import string
from PIL.ImageFont import FreeTypeFont

正 = ["一", "丄", "上", "止", "正"]
L = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"]


def numf(num: int):
    if num < 10000:
        return str(num)
    elif num < 100000000:
        return ("%.2f" % (num / 10000)) + "万"
    else:
        return ("%.2f" % (num / 100000000)) + "亿"


def get_cut_str(str: str, cut: int) -> list[str]:
    """
    自动断行，用于 Pillow 等不会自动换行的场景
    """
    punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
    si = 0
    i = 0
    next_str = str
    str_list = []

    while re.search(r"\n\n\n\n\n", next_str):
        next_str = re.sub(r"\n\n\n\n\n", "\n", next_str)
    for s in next_str:
        si += 1 if s in string.printable else 2
        i += 1
        if next_str == "":
            break
        elif next_str[0] == "\n":
            next_str = next_str[1:]
        elif s == "\n":
            str_list.append(next_str[: i - 1])
            next_str = next_str[i - 1 :]
            si = 0
            i = 0
            continue
        if si > cut:
            try:
                if next_str[i] in punc:
                    i += 1
            except IndexError:
                str_list.append(next_str)
                return str_list
            str_list.append(next_str[:i])
            next_str = next_str[i:]
            si = 0
            i = 0
    str_list.append(next_str)
    i = 0
    non_wrap_str = []
    for p in str_list:
        if p == "":
            break
        elif p[-1] == "\n":
            p = p[:-1]
        non_wrap_str.append(p)
        i += 1
    return non_wrap_str


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


def getCutStr(str, cut):
    si = 0
    i = 0
    cutStr = ""
    for s in str:
        si += 2 if "\u4e00" <= s <= "\u9fff" else 1
        i += 1
        if si > cut:
            cutStr = f"{str[:i]}...."
            break
        else:
            cutStr = str

    return cutStr


def changeCount(num: int):

    res = ""
    while num >= 5:
        num -= 5
        res += 正[4]
    if num > 0:
        res += 正[num - 1]
    return res


def changeCountL(num: int):
    res = ""
    while num >= 10:
        num -= 10
        res += L[9]
    if num > 0:
        res += L[num - 1]
    return res
