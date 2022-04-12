import random
from pathlib import Path
import ujson

base_path = Path(__file__).parent

event_data = ujson.loads(base_path.joinpath("event.json").read_text(encoding="utf-8"))

reduce_event = event_data["reduce"]
add_event = event_data["add"]
normal_event = event_data["normal"]
special_event = event_data["special"]


def reduce(gold):
    change = random.randint(0, gold // 2)
    res = max(gold - change, 1)
    replay = random.choice(reduce_event).format(gold=res).format(change=change)
    return replay, res


def normal(gold):

    replay = random.choice(normal_event).format(gold=gold)
    return replay, gold


def add(gold):
    change = random.randint(0, gold // 2)
    res = gold + change
    replay = random.choice(add_event).format(gold=res).format(change=change)
    return replay, res


def special(gold):
    change = random.randint(0, 200)
    res = gold + change
    replay = random.choice(special_event).format(gold=res).format(change=change)
    return replay, res


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
    if gold < 30:
        des = "【干瘪】"
    elif gold < 50:
        des = "【有些干瘪】"
    elif gold < 100:
        des = "【包装不错】"
    elif gold < 200:
        des = "【有着精致包装】"
    else:
        des = "【精致包装】"
    return f"你怀揣着激动的心情将抽奖卷放入扭蛋机中，叮咚！\n从扭蛋机中掉落了一个：{des}的乌帕礼盒。"


def change_event(gold) -> tuple[str, int]:
    if random.random() < 0.01:
        return special(gold)
    return random.choice(event_list)(gold)
