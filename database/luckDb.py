import random


import ujson
from typing import Union
from loguru import logger
from peewee import CharField, DoesNotExist, IntegerField, Model, SqliteDatabase

db = SqliteDatabase("./database/luckData.db")

gold_dic = {"0": 0, "1": 10, "2": -10}


class BaseModel(Model):
    class Meta:
        database = db


class Luck(BaseModel):
    qq = CharField()
    is_sign = IntegerField(default=0)
    gold = IntegerField(default=0)
    anyOthers = IntegerField(default=0)

    class Meta:
        table_name = "luck_info"


class User(BaseModel):
    qq = CharField()
    gold_raw = CharField(default="[]")
    anyOthers = IntegerField(default=0)
    res_time = IntegerField(default=0)
    ex_gold = IntegerField(default=0)

    class Meta:
        table_name = "user_info"


db.create_tables([Luck], safe=True)
db.create_tables([User], safe=True)


def init_user(qq: str):
    # luck = Luck.select().where(Luck.is_sign == 0)
    # if not luck.exists():
    #     p = Luck(qq=0, gold=10)
    #     p.save()
    #     logger.info("已初始化,并添加乌帕")
    luck = User.select().where(User.qq == qq)
    if not luck.exists():
        p = User(qq=qq)
        p.save()
        logger.info("已初始化玩家数据")


def Decorator(func):
    def init(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            if args:
                init_user(args[0])
            if kwargs:
                init_user(kwargs["qq"])
            return func(*args, **kwargs)

    return init


def Updata_Decorator(func):
    def init(*args, **kwargs):
        try:
            if s := func(*args, **kwargs):
                return s
            if args:
                init_user(args[0])
            if kwargs:
                init_user(kwargs["qq"])
            return func(*args, **kwargs)
        except ValueError:
            return 0

    return init


def sign(id):  # 切换是否打捞状态
    luck = Luck.get(id=id)
    if luck.is_sign:
        return False
    logger.info(f"ID{id}已转换状态")
    return Luck.update(is_sign=1).where(Luck.id == id).execute()


def get_luck_info(id: int) -> Luck:
    return Luck.get(id=id)


@Decorator
def get_user_info(qq: str) -> User:
    return User.get(qq=qq)


@Decorator
def get_gold_raw(qq: str) -> list:
    return ujson.loads(User.get(qq=qq).gold_raw)


def add_luck(qq: str, num: int) -> int:
    Luck.insert(gold=num, qq=qq).execute()
    gold_raw: list = get_gold_raw(qq)
    if num <= 10:
        gold_raw.append(-4)
    elif num < 15:
        gold_raw.append(0)
    else:
        gold_raw.append(num // 5)
    User.update(gold_raw=gold_raw).where(User.qq == qq).execute()
    return gold_raw[-1]


def reset_sign():
    return Luck.update(is_sign=0).where(Luck.is_sign == 1).execute()


def all_sign_num():
    all_num = Luck.select().count()
    sign_num = Luck.select().where(Luck.is_sign == 1).count()
    return sign_num, all_num


def give_all_gold(num: int):
    return Luck.update(gold=Luck.gold + num).execute()


def get_luck_id():  # 随机取一个符合条件的瓶子
    un_sign = Luck.select().where(Luck.is_sign == 0)
    s = [p.id for p in un_sign]
    return random.choice(s)


def get_user_change(
    qq: str,
) -> Union[int, None]:  # 返回本次变化
    line = get_gold_raw(qq)
    if len(line) == 0:
        return None
    User.update(gold_raw=line[:-1]).where(User.qq == qq).execute()
    return line[-1]


def set_all_luck_gold(gold: int):
    return Luck.update(gold=gold).execute()


if __name__ == "__main__":
    User.update(gold_raw="[]").where(User.gold_raw != "[]").execute()
