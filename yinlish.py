import os
import asyncio
from unittest import async_case
import random
import jieba
import jieba.posseg as pseg
jieba.setLogLevel(20)


async def _词转换(x, y, 淫乱度):
    if random.random() > 淫乱度:
        return x
    if x in {'，', '。'}:
        return '……'
    if x in {'!', '！'}:
        return '❤'
    if len(x) > 1 and random.random() < 0.5:
        return f'{x[0]}……{x}'
    else:
        if y == 'n' and random.random() < 0.5:
            x = '〇' * len(x)
        return f'……{x}'


async def chs2yin(s, 淫乱度=0.5):
    return ''.join([await _词转换(x, y, 淫乱度) for x, y in pseg.cut(s)])


if __name__ == '__main__':
    print(chs2yin('不行，那里不行。'))
    
async def opens (contain):# a test for read and write
    with open ("new.txt",mode="a",encoding="utf-8") as new:
        new.write(contain)
    with open ("new.txt",mode="r",encoding="utf-8") as new2:
        read=new2.read()
    return read
        