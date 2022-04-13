import random

from pathlib import Path
import ujson

base_path = Path(__file__).parent

event_data = ujson.loads(base_path.joinpath("event.json").read_text(encoding="utf-8"))

reduce_event = event_data["reduce"]
add_event = event_data["add"]
normal_event = event_data["normal"]
special_event = event_data["special"]
clear_event = event_data["clear"]


def reduce(gold):
    change = random.randint(0, gold // 2)
    res = max(gold - change, 1)
    replay = random.choice(reduce_event).format(gold=res, change=change)
    return replay, res


def normal(gold):

    replay = random.choice(normal_event).format(gold=gold)
    return replay, gold


def add(gold):
    change = random.randint(0, gold // 2)
    res = gold + change
    replay = random.choice(add_event).format(gold=res, change=change)
    return replay, res


def special(gold):
    change = random.randint(0, 100)
    res = gold + change
    event = random.choice(special_event)
    replay = event.format(gold=res, change=change)
    return replay, res


def clear(gold):
    replay = random.choice(clear_event)
    return replay, 0


special_list = [special, clear]
event_list = [reduce, add, normal]


def get_reword(gold):
    if gold < 0:
        return "【老旧奖券】"
    elif gold < 3:
        return "【普通奖券】"
    elif gold <= 6:
        return "【精品奖券】"
    elif gold <= 12:
        return "【精致奖券】"
    else:
        return "【华丽奖券】"


def get_reply(gold):
    if gold < 8:
        des = "【干瘪】"
    elif gold < 10:
        des = "【有些干瘪】"
    elif gold < 15:
        des = "【包装不错】"
    elif gold < 35:
        des = "【有着精致包装】"
    else:
        des = "【精致包装】"
    return f"你怀揣着激动的心情将抽奖卷放入扭蛋机中，叮咚！\n从扭蛋机中掉落了一个：{des}的乌帕礼盒。"


def change_event(gold) -> tuple[str, int]:
    if random.random() < 0.01:
        return random.choice(special_list)(gold)
    return random.choice(event_list)(gold)
