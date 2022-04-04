import ujson
from pathlib import Path
from loguru import logger
from peewee import CharField, SqliteDatabase, Model, DoesNotExist

from util.TimeTool import date_today

path = Path(__file__).parent.joinpath("shop.json")
data: dict = ujson.loads(path.read_text(encoding="utf-8"))

db = SqliteDatabase(Path(__file__).parent.joinpath("funcData.db"))


class BaseModel(Model):
    class Meta:
        database = db


class Func(BaseModel):
    date = CharField(default=date_today())
    data = CharField(max_length=8000, default="")

    class Meta:
        db_table = "user_info"


db.create_tables([Func], safe=True)


def init_today():
    today = date_today()
    user = Func.select().where(Func.date == today)
    if not user.exists():
        p = Func(date=today)
        p.save()
        logger.info(f"已初始化{today}")


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
def get_data(date: str = None) -> dict:
    if date is None:
        date = date_today()
    return ujson.loads(Func.get(date=date).data.replace("'", '"'))


def add_count(func: str):
    func_data = get_data(date_today())
    if func not in func_data:
        func_data[func] = 1
    else:
        func_data[func] += 1
    Func_update(date_today(), func_data)


@Updata_Decorator
def Func_update(date: str, data: dict):
    return Func.update(data=data).where(Func.date == date).execute()


# if __name__ == "__main__":
#     pass
