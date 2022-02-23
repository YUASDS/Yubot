import random

from loguru import logger
from peewee import SqliteDatabase, Model, CharField, IntegerField

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
    gold_raw = CharField(default='0')
    res_time = IntegerField(default=0)
    ex_gold = IntegerField(default=0)
    anyOthers = IntegerField(default=0)

    class Meta:
        table_name = "user_info"


db.create_tables([Luck], safe=True)
db.create_tables([User], safe=True)


def init_luck(qq="0"):
    luck = Luck.select().where(Luck.is_sign == 0)
    if not luck.exists():
        p = Luck(qq=0, gold=10)
        p.save()
        logger.info("已初始化,并添加乌帕")
    luck = User.select().where(User.qq == qq)
    if not luck.exists():
        p = User(qq=qq, gold=0)
        p.save()
        logger.info("已初始化玩家数据")


async def sign(id):  # 切换是否打捞状态
    init_luck()
    luck = Luck.get(id=id)
    if luck.is_sign:
        return False
    else:
        p = Luck.update(is_sign=1).where(Luck.id == id)
        p.execute()
        logger.info("已转换状态")
        return True


async def get_luck_info(id):
    init_luck()
    luck = Luck.get(id=id)
    return [luck.qq, luck.is_sign, luck.gold, luck.anyOthers]


async def get_user_info(qq: str):
    init_luck(qq=qq)
    luck = User.get(qq=qq)
    return [luck.id, luck.is_sign, luck.gold, luck.anyOthers]


async def add_luck(qq: str, num: int):
    init_luck(qq=qq)
    Luck.insert(gold=num, qq=qq).execute()
    user = User.get(qq=qq)
    line = user.gold_raw
    s = ""
    if num < 30:
        s = "2"
        gold_change = line.join("2")
    elif num > 50:
        s = "1"
        gold_change = line.join("1")
    else:
        s = "0"
        gold_change = line.join("0")
    User.update(gold_raw=gold_change,
                res_time=user.res_time + 1).where(User.qq == qq).execute()
    return gold_dic[s]


async def get_user_time(qq: str):
    return User.get(qq=qq).res_time


async def reset_sign():
    Luck.update(is_sign=0).where(Luck.is_sign == 1).execute()
    return True


async def all_sign_num():
    all_num = Luck.select().count()
    sign_num = Luck.select().where(Luck.is_sign == 1).count()
    return [sign_num, all_num]


async def give_all_gold(num: int):
    Luck.update(gold=Luck.gold + num).execute()
    return True


async def get_luck_id():  # 随机取一个符合条件的瓶子
    un_sign = Luck.select().where(Luck.is_sign == 0)
    s = []
    for p in un_sign:
        num = int(p.id)
        s.append(num)
    id_get = random.choice(s)
    return id_get


async def get_luck_gold(id: int):
    try:
        luck = Luck.get(id=id)
        return luck.gold
    except:
        return False


async def get_user_change(qq: str):  # 返回本次变化
    user = User.get(qq=qq)
    line = user.gold_raw
    gold_change = line[-1]
    if len(line) > 0:
        new_raw = line[:-1]
    else:
        new_raw = "0"
    User.update(gold_raw=new_raw,
                res_time=user.res_time - 1).where(User.qq == qq).execute()
    return gold_dic[gold_change]


def set_all_luck_gold(gold: int):
    Luck.update(gold=gold).execute()
    return True


# async def get_ranking():
#     luck_list = Luck.select().order_by(Luck.gold.desc())
#     luck_num = len(luck_list)
#     gold_rank = PrettyTable()
#     gold_rank.field_names = [
#         " ID ",
#         "      QQ      ",
#         "             NICK             ",
#         "  GOLD  ",
#         "  TALK  ",
#         "ANSWER",
#         "RANK",
#     ]
#     gold_rank.align[" ID "] = "r"
#     gold_rank.align["  GOLD  "] = "r"
#     gold_rank.align["  TALK  "] = "r"
#     gold_rank.align["ANSWER"] = "r"
#     gold_rank.align["RANK"] = "r"
#     i = 1

#     for luck_info in luck_list[:15]:
#         luck_id = luck_info.id
#         luck_qq = luck_info.qq

#         async with httpx.AsyncClient(timeout=10) as client:
#             r = await client.get(
#                 f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={luck_qq}"
#             )
#             r.encoding = "GBK"
#             qqdata = r.text

#         qqdata = json.loads(qqdata[17:-1])
#         luck_nick = qqdata[luck_qq][-2]

#         # luck_nick = getCutStr(qqnick, 20)
#         luck_gold = luck_info.gold
#         luck_talk = luck_info.talk_num
#         luck_answer = luck_info.english_answer
#         gold_rank.add_row(
#             [luck_id, luck_qq, luck_nick, luck_gold, luck_talk, luck_answer, i]
#         )
#         i += 1

#     gold_rank = gold_rank.get_string()

#     luck_list = Luck.select().order_by(Luck.talk_num.desc())
#     luck_num = len(luck_list)
#     talk_rank = PrettyTable()
#     talk_rank.field_names = [
#         " ID ",
#         "      QQ      ",
#         "             NICK             ",
#         "  GOLD  ",
#         "  TALK  ",
#         "ANSWER",
#         "RANK",
#     ]
#     talk_rank.align[" ID "] = "r"
#     talk_rank.align["  GOLD  "] = "r"
#     talk_rank.align["  TALK  "] = "r"
#     talk_rank.align["ANSWER"] = "r"
#     talk_rank.align["RANK"] = "r"
#     i = 1

#     for luck_info in luck_list[:15]:
#         luck_id = luck_info.id
#         luck_qq = luck_info.qq

#         async with httpx.AsyncClient(timeout=10) as client:
#             r = await client.get(
#                 f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={luck_qq}"
#             )
#             r.encoding = "GBK"
#             qqdata = r.text

#         qqdata = json.loads(qqdata[17:-1])
#         luck_nick = qqdata[luck_qq][-2]

#         # luck_nick = getCutStr(qqnick, 20)
#         luck_gold = luck_info.gold
#         luck_talk = luck_info.talk_num
#         luck_answer = luck_info.english_answer
#         talk_rank.add_row(
#             [luck_id, luck_qq, luck_nick, luck_gold, luck_talk, luck_answer, i]
#         )
#         i += 1

#     talk_rank = talk_rank.get_string()

#     luck_list = Luck.select().order_by(Luck.english_answer.desc())
#     luck_num = len(luck_list)
#     answer_rank = PrettyTable()
#     answer_rank.field_names = [
#         " ID ",
#         "      QQ      ",
#         "             NICK             ",
#         "  GOLD  ",
#         "  TALK  ",
#         "ANSWER",
#         "RANK",
#     ]
#     answer_rank.align[" ID "] = "r"
#     answer_rank.align["  GOLD  "] = "r"
#     answer_rank.align["  TALK  "] = "r"
#     answer_rank.align["ANSWER"] = "r"
#     answer_rank.align["RANK"] = "r"
#     i = 1

#     for luck_info in luck_list[:15]:
#         luck_id = luck_info.id
#         luck_qq = luck_info.qq
#         async with httpx.AsyncClient(timeout=10) as client:
#             r = await client.get(
#                 f"https://r.qzone.qq.com/fcg-bin/cgi_get_portrait.fcg?uins={luck_qq}"
#             )
#             r.encoding = "GBK"
#             qqdata = r.text

#         logger.debug(qqdata)
#         qqdata = json.loads(qqdata[17:-1])
#         luck_nick = qqdata[luck_qq][-2]

#         # luck_nick = getCutStr(qqnick, 20)
#         luck_gold = luck_info.gold
#         luck_talk = luck_info.talk_num
#         luck_answer = luck_info.english_answer
#         answer_rank.add_row(
#             [luck_id, luck_qq, luck_nick, luck_gold, luck_talk, luck_answer, i]
#         )
#         i += 1

#     answer_rank = answer_rank.get_string()

#     return str(
#         f"YuBot 排行榜：\n当前共服务了 {luck_num} 位用户\n注意：排行榜每十分钟更新一次\n"
#         + "================================================================================================"
#         + f"\n{COIN_NAME}排行榜\n{gold_rank}\n发言排行榜\n{talk_rank}\n答题排行榜\n{answer_rank}\n"
#     )

# def ladder_rent_collection():
#     luck_list = Luck.select().where(Luck.gold >= 1000).order_by(Luck.gold.desc())
#     total_rent = 0
#     for luck in luck_list:
#         luck: Luck
#         leadder_rent = 1 - (math.floor(luck.gold / 1000) / 100)
#         Luck.update(gold=luck.gold * leadder_rent).where(Luck.id == luck.id).execute()
#         gold = Luck.get(Luck.id == luck.id).gold
#         total_rent += luck.gold - gold
#         logger.info(f"{luck.id} 被收取 {luck.gold - gold} {COIN_NAME}")

#     return total_rent
