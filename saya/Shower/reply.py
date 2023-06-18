import time
import random
from typing import Union

import ujson
from pathlib import Path
from util.strings import changeCountL

BASEPATH = Path(__file__).parent
USER_PATH = BASEPATH.joinpath("user_data.json")
GROUP_PATH = BASEPATH.joinpath("group_data.json")
if not USER_PATH.exists():
    with open(USER_PATH, "w", encoding="utf-8") as f:
        f.write("{}")
if not GROUP_PATH.exists():
    with open(GROUP_PATH, "w", encoding="utf-8") as f:
        f.write("{}")
SHOWER_DATA: dict = ujson.loads(
    BASEPATH.joinpath("shower.json").read_text(encoding="utf-8")
)


GROUP_DATA: dict = ujson.loads(GROUP_PATH.read_text(encoding="utf-8"))
USER_DATA: dict = ujson.loads(USER_PATH.read_text(encoding="utf-8"))


class Bath:
    def __init__(self, bashName) -> None:
        self.bashName = bashName

    @staticmethod
    def get_end_reply(bashName) -> str:
        return random.choice(SHOWER_DATA[bashName]["结束回复"])

    @staticmethod
    def get_gift(bashName):
        total = sum(SHOWER_DATA[bashName]["礼物"][i] for i in SHOWER_DATA[bashName]["礼物"])
        res = random.randint(1, total)
        for i in SHOWER_DATA[bashName]["礼物"]:
            res -= SHOWER_DATA[bashName]["礼物"][i]
            if res <= 0:
                return i

    @staticmethod
    def get_des(bashName) -> str:
        return random.choice(SHOWER_DATA[bashName]["入浴回复"])

    @staticmethod
    def get_tem(bashName) -> str:
        return random.choice(SHOWER_DATA[bashName]["温度"])

    @staticmethod
    def get_brand(bashName) -> str:
        return random.choice(SHOWER_DATA[bashName]["浴牌"])

    @staticmethod
    def get_bash() -> str:
        return random.choice(list(SHOWER_DATA.keys()))


class ShowerGroup:
    def __init__(self, group: Union[int, str]) -> None:
        if isinstance(group, int):
            group = str(group)
        self.group = group
        if group not in GROUP_DATA:
            self.group_init(group)

    @staticmethod
    def group_init(group: str) -> None:
        GROUP_DATA[group] = {"bash": Bath.get_bash(), "user": []}
        return

    @staticmethod
    def shower_event():
        """
        {group:{uid:reply},{},{}}
        """
        reply_list = {}
        flag = False
        for group in GROUP_DATA:
            reply_list[group] = {}
            for user in GROUP_DATA[group]["user"].copy():
                interval = time.time() - USER_DATA[user]["time"]
                if interval > 3600:
                    flag = True
                    gift = Bath.get_gift(GROUP_DATA[group]["bash"])
                    User.add_gift(user, gift)
                    User.type_change(user)
                    end_reply = Bath.get_end_reply(USER_DATA[user]["shower"])

                    reply_list[group][
                        user
                    ] = f"\n{end_reply}\n你已经泡了1个小时，这是浴场主送来的礼盘,里面放着【{gift}】。"

                    GROUP_DATA[group]["user"].remove(user)
        return flag, reply_list

    def get_num(self, user) -> int:
        GROUP_DATA[self.group]["user"].append(user)
        return len(GROUP_DATA[self.group]["user"])

    def get_bash(self) -> str:
        return GROUP_DATA[self.group]["bash"]

    @staticmethod
    def set_bash(group, bashName) -> None:
        GROUP_DATA[group]["bash"] = bashName

    @staticmethod
    def reset() -> None:
        for i in GROUP_DATA:
            GROUP_DATA[i]["bash"] = Bath.get_bash()
            GROUP_DATA[i]["num"] = 0
            GROUP_DATA[i]["user"] = []


class User:
    def __init__(self, qq: int):
        if isinstance(qq, int):
            qq_str = str(qq)
        self.qq = qq_str

    @staticmethod
    def reset() -> None:
        for user in USER_DATA:
            user["today"] = 0
            user["type"] = 0

    @staticmethod
    def type_change(user: str) -> None:
        USER_DATA[user]["type"] = 0

    @staticmethod
    def add_today(user: str) -> None:
        USER_DATA[user]["today"] += 1

    @staticmethod
    def add_gift(qq: str, gift):
        if qq in USER_DATA:
            USER_DATA[qq]["gift"].append(gift)

    def finish(self) -> None:
        self.add_today(self.qq)
        self.type_change(self.qq)

    def check_time(self) -> bool:
        if self.qq not in USER_DATA:
            USER_DATA[self.qq] = {
                "type": 0,
                "time": time.time(),
                "today": 1,
                "gift": [],
            }
            return True
        else:
            interval = time.time() - USER_DATA[self.qq]["time"]
            if USER_DATA[self.qq]["type"] != 0:
                return False
            if interval > 7200 and USER_DATA[self.qq]["today"] <= 3:
                USER_DATA[self.qq]["time"] = time.time()
                return True
            return False

    def set_bash(self, bash) -> str:
        USER_DATA[self.qq]["shower"] = bash
        return bash

    def get_reply(self, group: Union[int, str]) -> str:
        self.finish()
        groupObj = ShowerGroup(group)
        bash = groupObj.get_bash()
        self.set_bash(bash)
        count = changeCountL(groupObj.get_num(self.qq))
        des = Bath.get_des(bash)
        brand = Bath.get_brand(bash)
        tempu = Bath.get_tem(bash)
        return f"你抵达了【{bash}】浴场,\n你的浴牌是【{brand}[{count}]】,\n当前温度为:【{tempu}】\n{des}"

    def get_reply_two(self, target, group: Union[int, str]):
        self.finish()
        target.finish()
        groupObj = ShowerGroup(group)
        bash = groupObj.get_bash()
        self.set_bash(bash)
        count = changeCountL(groupObj.get_num(self.qq))
        des = Bath.get_des(bash)
        brand = Bath.get_brand(bash)
        tempu = Bath.get_tem(bash)
        return f"你抵达了【{bash}】浴场,\n你的浴牌是【{brand}[{count}]】,\n当前温度为:【{tempu}】\n{des}"


def save_data() -> None:
    with USER_PATH.open("w", encoding="utf-8") as f:
        ujson.dump(USER_DATA, f, indent=2, ensure_ascii=False)
    with GROUP_PATH.open("w", encoding="utf-8") as f:
        ujson.dump(GROUP_DATA, f, indent=2, ensure_ascii=False)
    return
