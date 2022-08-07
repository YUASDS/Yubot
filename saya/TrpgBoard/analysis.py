import contextlib
from datetime import date, datetime
import time
from typing import Union
from pydantic import BaseModel


class Response(BaseModel):
    id: int
    title: str
    kp_qq: str
    kp_name: str
    start_time: Union[datetime, date]
    last_time: str
    minper: int
    maxper: int
    tags: str
    des: str
    players: list[int] = []


trance_dict = {
    "ID": "id",
    "团名": "title",
    "主持人QQ": "kp_qq",
    "主持人昵称": "kp_name",
    "开始时间": "start_time",
    "持续时间": "last_time",
    "最少人数": "minper",
    "最多人数": "maxper",
    "标签": "tags",
    "介绍": "des",
}


def time_format(a: str):
    try:
        res = time.strftime("%Y-%m-%d", time.strptime(a, "%Y年%m月%d日"))
    except ValueError:
        time_get = time.strptime(a, "%m月%d日")
        res1 = time.strftime("%m-%d", time_get)
        if time_get >= time.localtime():
            year = time.localtime().tm_year
        else:
            year = time.localtime().tm_year + 1
        res = f"{year}-{res1}"
    return res


def line_split(text: str) -> dict[str, Union[str, int]]:
    lines = text.split("\n")
    data = {}
    for line in lines:
        res = line.split("-")
        key = trance_dict.get(res[0].replace(" ", ""))
        if key is None:
            try:
                data["介绍"] += f"\n{res[0]}"
            except KeyError:
                continue
        else:
            data[key] = res[1].replace(" ", "")
    if data.get("last_time"):
        data["last_time"] = (
            data["last_time"].replace("日", "d").replace("天", "d").replace("时", "h")
        )
    if data.get("start_time"):
        time_format_res = time_format(data["start_time"])
        if time_format_res[0]:
            data["start_time"] = time_format_res
    if data.get("minper"):
        with contextlib.suppress(ValueError):
            data["minper"] = int(data["minper"])
    if data.get("maxper"):
        with contextlib.suppress(ValueError):
            data["maxper"] = int(data["maxper"])
    return data


class Analysis:
    def __init__(self, mode: str):
        self.mode = mode

    def analyze(self, text: str):
        self.text = text
        self.data = line_split(text)
        if self.mode in ["search", "update"]:
            return self.data
        elif self.mode == "delete":
            return self.delete()
        elif self.mode == "add":
            return self.add()
        else:
            raise KeyError("mode is not correct")

    def add(self):
        return self.add_analysis()

    def add_analysis(self):
        data = self.data
        if data.get("minper") is None:
            data["minper"] = 1
        if data.get("maxper") is None:
            data["maxper"] = 4
        if len(data) < 7:
            raise KeyError("data is not complete")
        return data

    def delete(self):
        line = self.text.split("-")
        target = int(line[1]) if len(line) > 1 else int(line[0])
        return {"id": target}
