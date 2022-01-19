import random

from peewee import SqliteDatabase, Model, CharField, IntegerField


db = SqliteDatabase("./saya/EnglishTest/database/WordData.db")


class BaseModel(Model):
    class Meta:
        database = db


class Word(BaseModel):
    word = CharField()
    pos = CharField()
    tran = CharField()
    bookId = IntegerField()

    class Meta:
        table_name = "word_dict"


db.create_tables([Word], safe=True)


def add_word(data):
    word = data[0]
    pos = data[1]
    tran = data[2]
    book = data[3]
    p = Word(word=word, pos=pos, tran=tran, bookId=book)
    p.save()


async def random_word(bookid):
    p = Word.select().where(Word.bookId == bookid)
    data = random.choice(p)
    return [data.word, data.pos, data.tran]
