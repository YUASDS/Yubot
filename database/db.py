import json
import math
import httpx

from loguru import logger
from prettytable import PrettyTable
from peewee import SqliteDatabase, Model, CharField, IntegerField

from config import COIN_NAME


db = SqliteDatabase("./database/userData.db")


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    qq = CharField()
    is_sign = IntegerField(default=0)
    sign_num = IntegerField(default=0)
    english_answer = IntegerField(default=0)
    gold = IntegerField(default=0)
    talk_num = IntegerField(default=0)

    class Meta:
        table_name = "user_info"


db.create_tables([User], safe=True)


def init_user(qq: str):
    user = User.select().where(User.qq == str(qq))
    if not user.exists():
        p = User(qq=qq, gold=60)
        p.save()
        logger.info(f"已初始化{qq}")


async def sign(qq):
    init_user(qq)
    user = User.get(qq=qq)
    if user.is_sign:
        return False
    else:
        p = User.update(is_sign=1, sign_num=User.sign_num + 1).where(User.qq == qq)
        p.execute()
        return True


async def get_info(qq):
    init_user(qq)
    user = User.get(qq=qq)
    return [user.id, user.is_sign, user.sign_num, user.gold, user.talk_num]


async def add_gold(qq: str, num: int):
    init_user(qq)
    p = User.update(gold=User.gold + num).where(User.qq == qq)
    p.execute()
    return True


async def reduce_gold(qq: str, num: int, force: bool = False):
    init_user(qq)
    gold_num = User.get(qq=qq).gold
    if gold_num < num:
        if force:
            p = User.update(gold=0).where(User.qq == qq)
            p.execute()
            return
        else:
            return False
    else:
        p = User.update(gold=User.gold - num).where(User.qq == qq)
        p.execute()
        return True


async def trans_all_gold(from_qq: str, to_qq: str) -> int:
    init_user(from_qq)
    init_user(to_qq)
    from_user_gold = User.get(qq=from_qq).gold
    await reduce_gold(from_qq, from_user_gold)
    await add_gold(to_qq, from_user_gold)
    return from_user_gold


async def add_talk(qq: str):
    init_user(qq)
    User.update(talk_num=User.talk_num + 1).where(User.qq == qq).execute()
    return


async def reset_sign():
    User.update(is_sign=0).where(User.is_sign == 1).execute()
    return


async def all_sign_num():
    all_num = User.select().count()
    sign_num = User.select().where(User.is_sign == 1).count()
    return [sign_num, all_num]


async def give_all_gold(num: int):
    User.update(gold=User.gold + num).execute()
    return


async def add_answer(qq: str):
    User.update(english_answer=User.english_answer + 1).where(User.qq == qq).execute()
    return


async def get_ranking():
    user_list = User.select().order_by(User.gold.desc())
    user_num = len(user_list)
    gold_rank = PrettyTable()
    gold_rank.field_names = [
        " ID ",
        "      QQ      ",
        "             NICK             ",
        "  GOLD  ",
        "  TALK  ",
        "ANSWER",
        "RANK",
    ]
    gold_rank.align[" ID "] = "r"
    gold_rank.align["  GOLD  "] = "r"
    gold_rank.align["  TALK  "] = "r"
    gold_rank.align["ANSWER"] = "r"
    gold_rank.align["RANK"] = "r"
    i = 1

    for user_info in user_list[:15]:
        user_id = user_info.id
        user_qq = user_info.qq

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={user_qq}"
            )
            r.encoding = "GBK"
            qqdata = r.text

        qqdata = json.loads(qqdata[17:-1])
        user_nick = qqdata[user_qq][-2]

        # user_nick = getCutStr(qqnick, 20)
        user_gold = user_info.gold
        user_talk = user_info.talk_num
        user_answer = user_info.english_answer
        gold_rank.add_row(
            [user_id, user_qq, user_nick, user_gold, user_talk, user_answer, i]
        )
        i += 1

    gold_rank = gold_rank.get_string()

    user_list = User.select().order_by(User.talk_num.desc())
    user_num = len(user_list)
    talk_rank = PrettyTable()
    talk_rank.field_names = [
        " ID ",
        "      QQ      ",
        "             NICK             ",
        "  GOLD  ",
        "  TALK  ",
        "ANSWER",
        "RANK",
    ]
    talk_rank.align[" ID "] = "r"
    talk_rank.align["  GOLD  "] = "r"
    talk_rank.align["  TALK  "] = "r"
    talk_rank.align["ANSWER"] = "r"
    talk_rank.align["RANK"] = "r"
    i = 1

    for user_info in user_list[:15]:
        user_id = user_info.id
        user_qq = user_info.qq

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={user_qq}"
            )
            r.encoding = "GBK"
            qqdata = r.text

        qqdata = json.loads(qqdata[17:-1])
        user_nick = qqdata[user_qq][-2]

        # user_nick = getCutStr(qqnick, 20)
        user_gold = user_info.gold
        user_talk = user_info.talk_num
        user_answer = user_info.english_answer
        talk_rank.add_row(
            [user_id, user_qq, user_nick, user_gold, user_talk, user_answer, i]
        )
        i += 1

    talk_rank = talk_rank.get_string()

    user_list = User.select().order_by(User.english_answer.desc())
    user_num = len(user_list)
    answer_rank = PrettyTable()
    answer_rank.field_names = [
        " ID ",
        "      QQ      ",
        "             NICK             ",
        "  GOLD  ",
        "  TALK  ",
        "ANSWER",
        "RANK",
    ]
    answer_rank.align[" ID "] = "r"
    answer_rank.align["  GOLD  "] = "r"
    answer_rank.align["  TALK  "] = "r"
    answer_rank.align["ANSWER"] = "r"
    answer_rank.align["RANK"] = "r"
    i = 1

    for user_info in user_list[:15]:
        user_id = user_info.id
        user_qq = user_info.qq
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={user_qq}"
            )
            r.encoding = "GBK"
            qqdata = r.text

        logger.debug(qqdata)
        qqdata = json.loads(qqdata[17:-1])
        user_nick = qqdata[user_qq][-2]

        # user_nick = getCutStr(qqnick, 20)
        user_gold = user_info.gold
        user_talk = user_info.talk_num
        user_answer = user_info.english_answer
        answer_rank.add_row(
            [user_id, user_qq, user_nick, user_gold, user_talk, user_answer, i]
        )
        i += 1

    answer_rank = answer_rank.get_string()

    return str(
        f"ABot 排行榜：\n当前共服务了 {user_num} 位用户\n注意：排行榜每十分钟更新一次\n"
        + "================================================================================================"
        + f"\n{COIN_NAME}排行榜\n{gold_rank}\n发言排行榜\n{talk_rank}\n答题排行榜\n{answer_rank}\n"
    )


def ladder_rent_collection():
    user_list = User.select().where(User.gold >= 1000).order_by(User.gold.desc())
    total_rent = 0
    for user in user_list:
        user: User
        leadder_rent = 1 - (math.floor(user.gold / 1000) / 100)
        User.update(gold=user.gold * leadder_rent).where(User.id == user.id).execute()
        gold = User.get(User.id == user.id).gold
        total_rent += user.gold - gold
        logger.info(f"{user.id} 被收取 {user.gold - gold} {COIN_NAME}")

    return total_rent


def set_all_user_gold(gold: int):
    User.update(gold=gold).execute()
