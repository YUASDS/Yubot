import ujson
import aiohttp
import asyncio
import contextlib
from loguru import logger
from typing import Union, Optional
from pydantic import BaseModel, error_wrappers
from pathlib import Path


SETTING_PATH = Path(__file__).parent.joinpath("settings.json")
SETTING_DATA: dict = ujson.loads(SETTING_PATH.read_text(encoding="utf-8"))


APIKEY = SETTING_DATA.get("api_key")
BASE_URL = "http://arclight.space:45445"


class Player(BaseModel, extra="ignore"):
    nick: str
    qq: str


class BaseData(BaseModel, extra="ignore"):
    title: str
    kp_qq: str
    kp_name: str
    groups: list[str] = []
    start_time: str
    last_time: str
    minper: int
    maxper: int
    isfull: bool = False
    ob: bool = False
    tags: str
    skills: Union[str, None] = ""
    tips: Union[str, None] = ""
    des: str


class ResponseData(BaseData, extra="ignore"):
    id: int
    players: list[Player] = []
    last_timeh: str


class ResponseHead(BaseModel, extra="ignore"):
    succ: bool
    err_msg: Union[str, None] = ""


class DeleteRequest(BaseModel, extra="ignore"):
    ids: list[int]
    kp_qq: str


class DeleteResponse(ResponseHead):
    data: None


class SearchRequest(BaseModel, extra="ignore"):
    group: Optional[Union[str, int]]
    id: Optional[Union[int, list[int]]]
    title: Optional[str]
    kp_qq: Optional[str]
    last_time: Optional[str]
    minper: Optional[int]
    maxper: Optional[int]
    isfull: bool = False
    ob: bool = False
    tags: Optional[str]


class SearchResponse(ResponseHead):
    data: Union[list[ResponseData], None]


class AddResponse(ResponseHead):
    data: Union[int, None]


class UpdataResponse(ResponseHead, extra="ignore"):
    data: list[ResponseData]


class JoinRequest(BaseModel):
    ids: list[int]
    player: Player
    msg: str


class JoinResponse(ResponseHead):
    data: list[bool]


class QuitRequest(BaseModel):
    ids: list[int]
    qq: str


class QuitResponse(ResponseHead):
    data: list[bool]


class RemoveRequest(BaseModel):
    id: int
    kp_qq: str
    qqs: list[str]


class RemoveResponse(ResponseHead):
    data: None


class GetApprovalRequest(BaseModel):
    id: int
    kp_qq: str


class PlayerRequestData(BaseModel):
    id: int
    qq: str
    title: str
    kp_qq: str
    nick: str
    msg: Union[str, None]


class GetApprovalResponse(ResponseHead):
    data: list[PlayerRequestData]


class GetApplicationRequest(BaseModel, extra="ignore"):
    qq: str


class GetApplicationData(BaseModel):
    id: int
    title: str
    qq: str
    kp_qq: str
    status: int  # 申请状态。0：待处理；1：申请通 过；2：申请被拒绝
    timestamp: Union[int, None]  # 主持人处理的时间戳，status为 0 时为空值


class GetApplicationResponse(ResponseHead):
    data: list[GetApplicationData]


class ApplicationRequest(BaseModel):
    id: int
    kp_qq: str
    qqs: list[str]


class ApplicationResponse(ResponseHead):
    data: list[bool]


async def get(type: str, params: dict) -> dict:
    for key in params:
        if params[key] is False:
            params[key] = 0
        if params[key] is True:
            params[key] = 1
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/{type}?api_key={APIKEY}"
        async with session.get(url, params=params) as resp:
            res = await resp.json()
    logger.debug(res)
    return res


async def post(type: str, data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        url = f"{BASE_URL}/{type}?api_key={APIKEY}"
        async with session.post(url, json=data) as resp:
            res = await resp.json()
    logger.debug(res)
    return res


def miss_key(func):
    async def init(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except error_wrappers.ValidationError as e:
            logger.debug(e.errors())
            return ResponseHead(
                succ=False, err_msg=f'缺少参数：{e.errors()[0]["loc"]}'.replace("qqs", "qq")
            )

    return init


class ArcLight:
    def __init__(self, data: dict):
        self.data = data

    @miss_key
    async def search(self):
        search_data = SearchRequest(**self.data)
        res = await get("search", search_data.dict(exclude_unset=True))
        return SearchResponse(**res)

    @miss_key
    async def add(self):
        add_data = BaseData(**self.data)
        res = await post("add", add_data.dict())
        return AddResponse(**res)

    @miss_key
    async def update(self):
        res = await post("update", self.data)
        return UpdataResponse(**res)

    @miss_key
    async def delete(self):
        delete_data = DeleteRequest(**self.data)
        res = await post("delete", delete_data.dict())
        return DeleteResponse(**res)

    @miss_key
    async def join(self):
        join_data = JoinRequest(**self.data)
        res = await post("join", join_data.dict())
        return JoinResponse(**res)

    @miss_key
    async def quit(self):
        quit_data = QuitRequest(**self.data)
        res = await post("quit", quit_data.dict())
        return QuitResponse(**res)

    @miss_key
    async def remove(self):
        remove_data = RemoveRequest(**self.data)
        res = await post("remove", remove_data.dict())
        return RemoveResponse(**res)

    @miss_key
    async def get_approval(self):
        approval_data = GetApprovalRequest(**self.data)
        logger.debug(approval_data.dict())
        res = await get("getApproval", approval_data.dict())
        return GetApprovalResponse(**res)

    @miss_key
    async def get_application(self):
        application_data = GetApplicationRequest(**self.data)
        res = await get("getApplication", application_data.dict())
        return GetApplicationResponse(**res)

    @miss_key
    async def accept(self):
        accept_data = ApplicationRequest(**self.data)
        res = await post("accept", accept_data.dict())
        return ApplicationResponse(**res)

    @miss_key
    async def refuse(self):
        refuse_data = ApplicationRequest(**self.data)
        res = await post("refuse", refuse_data.dict())
        return ApplicationResponse(**res)


TRANSFORM_DICT = {
    "ID": "id",
    "id": "id",
    "团名": "title",
    "主持人QQ": "kp_qq",
    "主持人昵称": "kp_name",
    "开始时间": "start_time",
    "持续时间": "last_time",
    "最少人数": "minper",
    "最多人数": "maxper",
    "是否满员": "isfull",
    "允许ob": "ob",
    "推荐技能": "skills",
    "tips": "tips",
    "标签": "tags",
    "介绍": "des",
    "qq": "qq",
    "QQ": "qq",
}


def line_split(text: str) -> dict[str, Union[str, int]]:
    lines = text.split("\n")
    data = {}
    for line in lines:
        logger.debug(line)
        res = line.split(":")
        key = TRANSFORM_DICT.get(res[0].replace(" ", ""))
        if key is None:
            try:
                data["des"] += f"\n{line}"
            except KeyError:
                continue
        else:
            data[key] = res[1].replace(" ", "")
    if data.get("last_time"):
        data["last_time"] = (
            data["last_time"].replace("日", "d").replace("天", "d").replace("时", "h")
        )
    if data.get("minper"):
        with contextlib.suppress(ValueError):
            data["minper"] = int(data["minper"])
    if data.get("maxper"):
        with contextlib.suppress(ValueError):
            data["maxper"] = int(data["maxper"])
    return data


class MessageAnalysis:
    def __init__(self, text: str):
        self.text = text

    def analysis(self, mode: str):
        text = self.text
        self.data = line_split(text)

        with contextlib.suppress(KeyError):
            self.data["qqs"] = [  # type: ignore
                self.data["qq"],
            ]
            self.data["ids"] = [  # type: ignore
                self.data["id"],
            ]
        if mode in {"search", "update"}:
            return self.data
        elif mode == "delete":
            return self.delete()
        elif mode == "add":
            return self.add()
        elif mode == "remove":
            self.data["qqs"] = [  # type: ignore
                self.data["qq"],
            ]
            return self.data

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
            logger.debug(data)
            raise KeyError("data is not complete")
        return data

    def delete(self):
        line = self.text.split("-")
        target = int(line[1]) if len(line) > 1 else int(line[0])
        return {"id": target}

    def get_result(self, res):
        return


class ResponseAnalysis:
    def __init__(self, mode) -> None:
        pass

    def add(self, res: AddResponse):
        if res.err_msg:
            return "添加失败"

    def delete(self, res: DeleteResponse):
        if res.err_msg:
            return "删除失败"

    def search(self, res: SearchResponse):
        if res.err_msg:
            return "查询失败"
        if data := res.data:
            for response_data in data:
                response_data.dict()

    def updata(self, res: UpdataResponse):
        if res.err_msg:
            return "更新失败"

    def join(self, res: JoinResponse):
        pass

    def quit(self, res: QuitResponse):
        pass

    def remove(self, res: RemoveResponse):
        pass

    def get_approval(self, res: GetApprovalResponse):
        pass

    def get_application(self, res: GetApplicationResponse):
        pass

    def accept(self, res: ApplicationResponse):
        pass

    def refuse(self, res: ApplicationResponse):
        pass

    def get_result(self):
        pass


a = {
    "id": 7,
    "ids": [8],
    "qqs": ["12345678"],
    "qq": "12345678",
    "title": "test",
    "kp_qq": "123456",
    "kp_name": "sad",
    "group": "123456",
    "groups": ["123456"],
    "start_time": "明天",
    "des": "test",
    "last_time": "1h",
    "minper": 1,
    "maxper": 2,
    "isfull": False,
    "ob": False,
    "tags": "1",
}
b = {
    "id": 9,
    "group": "123456",
}
join = {
    "qq": 12345678,
}


async def test():
    arc = ArcLight(a)
    # await get("search", b)
    add = await arc.get_application()
    print(add.dict())


if __name__ == "__main__":
    asyncio.run(test())
