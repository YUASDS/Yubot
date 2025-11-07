import ujson
import random
import re
from typing import Union
from pathlib import Path
from .greet import greet, greet_order
from .favor import normal_favor, get_affinity

FAVOR_PATH = Path(__file__).parent.joinpath("favor_chat_data.json")
favor_data: dict = ujson.loads(FAVOR_PATH.read_text(encoding="utf-8"))
other_data: dict = ujson.loads(
    Path(__file__).parent.joinpath("other.json").read_text(encoding="utf-8")
)
re_key_word = f'([\\s\\S])*({"|".join(list(favor_data))})([\\s\\S])*'

black_word = ["觉得", "怎么样"]


async def get_reply(msg: str, qq: int) -> tuple[bool, list[str]]:
    if msg == "亲和":
        return True, [get_affinity()]
    match = re.compile(re_key_word)
    matched = match.findall(msg)
    order = matched[0][1] if matched else None
    for word in black_word:
        if word in msg:
            return False, [""]
    if not msg:
        if random.random() > 0.5:
            return False, [""]
        return True, [random.choice(other_data["回复"])]
    if order is None:  # 如果这条回复不是指令
        return False, [""]
    if not favor_data.get(order):
        return False, [""]
    if order in greet_order:
        replay = await greet(order, qq)
        return (True, replay)
    return await normal_favor(order, qq)
