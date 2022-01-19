import time

from peewee import IntegerField, SqliteDatabase, Model, CharField, BigIntegerField

db = SqliteDatabase("./database/talkData.db")


class BaseModel(Model):
    class Meta:
        database = db


class UserTalk(BaseModel):
    qq = CharField()
    group = CharField()
    msg = CharField()
    time = BigIntegerField()
    type = IntegerField()
    url = CharField(null=True)

    class Meta:
        table_name = "user_talk"


db.create_tables([UserTalk], safe=True)


async def add_talk(qq, group, type, msg, url=None):
    """
    type
    >>> 1 为文字
    >>> 2 为图片
    >>> 3 为闪照
    >>> 4 为语音
    """
    p = UserTalk(qq=qq, group=group, type=type, url=url, msg=msg, time=int(time.time()))
    p.save()


async def archive_exists(msg, type):
    msg_exists = UserTalk.select().where(UserTalk.msg == msg, UserTalk.type == type)
    if msg_exists.exists():
        return True
    else:
        return False


async def get_user_talk(qq, group, time=0):
    talklist = UserTalk.select().where(
        UserTalk.qq == qq,
        UserTalk.group == group,
        UserTalk.type == 1,
        UserTalk.time > time,
    )
    talk_list = []
    for talk in talklist:
        talk_list.append(talk.msg)
    return talk_list


async def get_group_talk(group, time=0):
    talklist = UserTalk.select().where(
        UserTalk.group == group, UserTalk.type == 1, UserTalk.time > time
    )
    talk_list = []
    for talk in talklist:
        talk_list.append(talk.msg)
    return talk_list


async def get_all_message():
    pass


def get_last_time(hour=24):
    curr_time = int(time.time())
    last_time = curr_time - curr_time % 3600 - hour * 3600
    return last_time


async def get_message_analysis():
    last_time = get_last_time(23)
    now = time.localtime(time.time())
    hour = now.tm_hour

    data = UserTalk.select().where(UserTalk.time >= last_time)
    res = {}

    for _ in range(24):
        if hour == 0:
            hour = 24
        res[f"{hour}:00"] = 0
        hour -= 1

    for item in data:
        item: UserTalk
        hour = f"{time.localtime(item.time).tm_hour or 24}:00"
        if hour in res:
            res[hour] += 1

    r1 = []
    r2 = []

    for ht in res:
        r1.append(ht)
        r2.append(res[ht])

    return r2, r1


def chat_count(m: str):
    c = UserTalk.select().where(UserTalk.msg.contains(m)).count()
    print(c)
