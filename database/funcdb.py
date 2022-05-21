import ujson
import time
from pathlib import Path
from loguru import logger
from peewee import CharField, SqliteDatabase, Model, DoesNotExist, IntegerField


def date_today():
    """
    "%Y年%m月%d日
    """
    now_time = time.localtime()
    return time.strftime("%Y年%m月%d日", now_time)


db = SqliteDatabase(Path(__file__).parent.joinpath("funcData.db"))


class BaseModel(Model):
    class Meta:
        database = db


class Func(BaseModel):
    date = CharField(default=date_today())
    data = CharField(max_length=8000, default="{}")

    class Meta:
        db_table = "user_info"


class Limit(BaseModel):
    qq = CharField(default="")
    today = CharField(default="{}")

    class Meta:
        db_table = "limit"


db.create_tables([Func, Limit], safe=True)


def init_today():
    today = date_today()
    user = Func.select().where(Func.date == today)
    if not user.exists():  # type: ignore
        p = Func(date=today)
        p.save()
        logger.info(f"已初始化{today}")


def init_today_limit(qq: str):
    user = Limit.select().where(Limit.qq == qq)
    if not user.exists():  # type: ignore
        p = Limit(qq=qq)
        p.save()
        logger.info(f"已初始化{qq}")


def limit_Decorator(func):
    def init(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            if args:
                init_today_limit(args[0])
            if kwargs:
                init_today_limit(kwargs["qq"])
            return func(*args, **kwargs)

    return init


def limit_Updata_Decorator(func):
    def init(*args, **kwargs):
        try:
            if s := func(*args, **kwargs):
                return s
            if args:
                init_today_limit(args[0])
            if kwargs:
                init_today_limit(kwargs["qq"])
            return func(*args, **kwargs)
        except ValueError:
            return 0

    return init


@limit_Updata_Decorator
def Limit_update(qq: str, limit_data: dict):
    return Limit.update(today=limit_data).where(Limit.qq == qq).execute()  # type: ignore


@limit_Decorator
def limit_today(qq: str) -> dict:
    return ujson.loads(Limit.get(qq=qq).today.replace("'", '"'))


def limit_add_count(qq: str, func: str):
    limit_data = limit_today(qq)
    if func not in limit_data:
        limit_data[func] = 1
    else:
        limit_data[func] += 1
    logger.debug(limit_data)
    Limit_update(qq, limit_data)


def clear_limit():
    Limit.update(today="{}").where(Limit.today != "{}").execute()  # type: ignore


def Decorator(func):
    def init(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            init_today()
            return func(*args, **kwargs)

    return init


def Updata_Decorator(func):
    def init(*args, **kwargs):
        try:
            if s := func(*args, **kwargs):
                return s
            init_today()
            return func(*args, **kwargs)
        except ValueError:
            return 0

    return init


@Decorator
def get_info(date: str) -> Func:
    return Func.get(date=date)


@Decorator
def get_data(date: str = "") -> dict:
    if not date:
        date = date_today()
    return ujson.loads(Func.get(date=date).data.replace("'", '"'))


async def add_count(func: str):
    func_data = get_data(date_today())
    if func not in func_data:
        func_data[func] = 1
    else:
        func_data[func] += 1
    Func_update(date_today(), func_data)


@Updata_Decorator
def Func_update(date: str, data: dict):
    return Func.update(data=data).where(Func.date == date).execute()  # type: ignore


if __name__ == "__main__":
    """"""
