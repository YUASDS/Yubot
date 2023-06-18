import random
from pathlib import Path

import ujson

from database.db import favor, get_info, add_favor, reduce_favor

FAVOR_PATH = Path(__file__).parent.joinpath("favor_chat_data.json")
COUNT_PATH = Path(__file__).parent.joinpath("count.txt")
if not COUNT_PATH.exists():
    with open(COUNT_PATH, "w", encoding="utf-8") as f:
        f.write("0")
favor_data: dict = ujson.loads(FAVOR_PATH.read_text(encoding="utf-8"))


def get_level(favors: int) -> int:  # 当前等级
    level = 1
    while 2**level < favors or 2**level == favors:
        favors -= 2**level
        level += 1
    return level


def get_favor_full(level: int) -> int:
    return sum(2**i for i in range(level + 1))


def get_affinity():
    with open(file=COUNT_PATH, mode="r", encoding="utf-8") as c:
        count: int = int(c.read())
    return f"唔.....千音的当前亲和度有{count}这么多~"


async def normal_favor(order: str, qq: int) -> tuple[bool, list[str]]:
    pun = 0
    bon = 0
    with open(file=COUNT_PATH, mode="r", encoding="utf-8") as c:
        count: int = int(c.read())
    info = await get_info(str(qq))
    info_favor = favor(info.favor)
    level_min = favor_data[order]["min"]
    level_max = favor_data[order]["max"]
    reply = []
    if info_favor.level >= level_min:  # 如果满足最低好感度回复
        succ_rate = favor_data[order]["成功率"]
        rate_get = random.randint(1, 100)
        if rate_get < succ_rate:
            if info_favor.res < 5:  # 当好感度刚升级未超过5更容易触发本等级的回复
                if info_favor.level > level_max:  # 如果超过最高好感度回复等级
                    favor_choice = random.randint(2**level_min, 2**level_max)
                else:
                    favor_choice = random.randint(
                        2**level_min, get_favor_full(info_favor.level)
                    )
                level_choice = get_level(favor_choice)  # 获取到触发回复的等级
            elif info_favor.level > level_max:  # 如果超过没有最高好感度回复等级
                level_choice = random.randint(level_min, level_max)
            else:
                level_choice = random.randint(level_min, info_favor.level)
            bon = random.randint(1, favor_data[order]["奖励"])  # 获取奖励
            reply.append(
                random.choice(favor_data[order][str(level_choice)])
            )  # 获取一条随机的回复
        else:
            reply.append(random.choice(favor_data[order]["失败"]))
            if "惩罚" in favor_data[order]:
                pun: int = random.randint(1, favor_data[order]["惩罚"])
    else:
        reply.append(random.choice(favor_data[order]["失败"]))
        if "惩罚" in favor_data[order]:
            pun: int = favor_data[order]["惩罚"]
    if bon > 0:
        count += 1
        if count < 100:
            with open(file=COUNT_PATH, mode="w", encoding="utf-8") as c:
                c.write(str(count))
            await add_favor(str(qq), num=bon)
        else:
            with open(file=COUNT_PATH, mode="w", encoding="utf-8") as c:
                c.write("1")
            bon = random.randint(10, 20)
            reply = ["千音完美亲和触发", random.choice(favor_data[order]["大成功"])]
            await add_favor(str(qq), num=bon, force=True)
    elif pun > 0:
        await reduce_favor(str(qq), num=pun)
    return True, reply
