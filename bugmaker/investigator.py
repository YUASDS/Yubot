# code utf-8需要修改dice函数，出现每个数字
from Core import *  # noqa
import os
import sqlite3
import random
from GlobalVariable import attributeRecord, fightRecord
import re
import datetime
import time

data_path = os.path.join(os.getcwd(), "bugmaker\\investigator\\data")
monster_path = os.path.join(data_path, "monster.db")
monster_conn = sqlite3.connect(monster_path)
monster_data = monster_conn.cursor()
investigator_path = os.path.join(data_path, "investigator.db")
investigator_conn = sqlite3.connect(investigator_path)
investigator_data = investigator_conn.cursor()
goods_path = os.path.join(data_path, "goods.db")
goods_conn = sqlite3.connect(goods_path)
goods_data = goods_conn.cursor()
img_path = os.path.join(os.getcwd(), "investigator\\img")

DIC = {
    'STR': "力量",
    'CON': "体质",
    'SIZ': "体型",
    'DEX': "敏捷",
    'APP': "外貌",
    'INT': "智力",
    'POW': "意志",
    'EDU': "教育",
    'LUCKY': "幸运",
    "DB": "伤害加深",
    "QQ": "QQ",
    "HP": "生命值",
    "SAN": "SAN",
    "AVOID": "闪避",
    "SHOT": "射击",
    "DETECT": "侦查",
    "AID": "急救",
    "MEDICINE": "医学",
    "FIGHT": "格斗",
    "AVOID": "闪避",
    "SHOT": "射击",
    "DETECT": "侦查",
    "AID": "急救",
    "MEDICINE": "医学",
    "CLOTHES": "防具",
    "ARMOR": "护甲",
    "GUN": "枪械",
    "WEAPONS": "武器",
    "GUN_DAMAGE": "枪械伤害",
    "WEAPONS_DAMAGE": "武器伤害",
    "MAGIC1": "法术1",
    "MAGIC2": "法术2",
    "BAG": "背包",
}
DIC2 = {
    "AVOID": "闪避",
    "SHOT": "射击",
    "DETECT": "侦查",
    "AID": "急救",
    "MEDICINE": "医学",
    "FIGHT": "格斗"
}
'''
    attribute['DB'] = DB
    attribute['AVOID'] = AVOID
    attribute['SHOT'] = SHOT
    attribute['DETECT'] = CHECK
    attribute['AID'] = AID
    attribute['MEDICINE'] = MEDICINE
CREATE TABLE NAME(
    ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    QQ INT,
    NAME VACHAR(30),
)
'''
'''
CREATE TABLE ATTRIBUTE
(
ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
NAME VARCHAR(40),
HP INT,
STR INT,
CON INT,
SIZ INT,
DEX INT,
INT INT,
POW INT,
FIGHT INT,
AVOID INT,
SHOT INT,
ARMOR INT,
FRE INT, #是否贯穿
FIGHT_WAY VACHAR(100),
DAMAGE1 VACHAR(100),
DAMAGE2 VACHAR(100),
START VACHAR(100),
FIGHT_CG VACHAR(100),
FIGHT_SUCC VACHAR(100),
FIGHT_FAIL VACHAR(100),
FIGHT2_CG VACHAR(100),
FIGHT2_SUCC VACHAR(100),
FIGHT2_FAIL VACHAR(100),
CONTER_CG VACHAR(100),
CONTER_SUCC VACHAR(100),
CONTER_FAIL VACHAR(100),
AVOID_CG VACHAR(100),
AVOID_SUCC VACHAR(100),
AVOID_FAIL VACHAR(100),
END_FIGHT VACHAR(100),
END_SHOUT VACHAR(100),
END_FAIL VACHAR(100),
SPECIAL VACHAR(40)
)
'''


class monster:  # 怪物对象
    def __init__(self, name) -> None:
        self.hp = monsql(name="ID", id=name, attribute1="HP")[0][0]
        self.dex = monsql(name="ID", id=name, attribute1="DEX")[0][0]
        self.str = monsql(name="ID", id=name, attribute1="STR")[0][0]
        self.fight = monsql(name="ID", id=name, attribute1="FIGHT")[0][0]
        self.avoid = monsql(name="ID", id=name, attribute1="AVOID")[0][0]
        self.shot = monsql(name="ID", id=name, attribute1="SHOT")[0][0]
        self.name = monsql(name="ID", id=name, attribute1="NAME")[0][0]
        self.armor = monsql(name="ID", id=name, attribute1="ARMOR")[0][0]
        self.fre = monsql(name="ID", id=name, attribute1="FRE")[0][0]
        self.fight_way = monsql(name="ID", id=name,
                                attribute1="FIGHT_WAY")[0][0]
        self.damage1 = monsql(name="ID", id=name, attribute1="DAMAGE1")[0][0]
        self.damage2 = monsql(name="ID", id=name, attribute1="DAMAGE2")[0][0]
        self.db = monsql(name="ID", id=name, attribute1="DB")[0][0]
        self.special = monsql(name="ID", id=name, attribute1="SPECIAL")[0][0]
        self.START = monsql(name="ID", id=name, attribute1="START")[0][0]
        self.FIGHT_CG = monsql(name="ID", id=name, attribute1="FIGHT_CG")[0][0]
        self.FIGHT_SUCC = monsql(name="ID", id=name,
                                 attribute1="FIGHT_SUCC")[0][0]
        self.FIGHT_FAIL = monsql(name="ID", id=name,
                                 attribute1="FIGHT_FAIL")[0][0]
        self.FIGHT2_CG = monsql(name="ID", id=name,
                                attribute1="FIGHT2_CG")[0][0]
        self.FIGHT2_SUCC = monsql(name="ID", id=name,
                                  attribute1="FIGHT2_SUCC")[0][0]
        self.FIGHT2_FAIL = monsql(name="ID", id=name,
                                  attribute1="FIGHT2_FAIL")[0][0]
        self.CONTER_CG = monsql(name="ID", id=name,
                                attribute1="CONTER_CG")[0][0]
        self.CONTER_SUCC = monsql(name="ID", id=name,
                                  attribute1="CONTER_SUCC")[0][0]
        self.CONTER_FAIL = monsql(name="ID", id=name,
                                  attribute1="CONTER_FAIL")[0][0]
        self.AVOID_CG = monsql(name="ID", id=name, attribute1="AVOID_CG")[0][0]
        self.AVOID_SUCC = monsql(name="ID", id=name,
                                 attribute1="AVOID_SUCC")[0][0]
        self.AVOID_FAIL = monsql(name="ID", id=name,
                                 attribute1="AVOID_FAIL")[0][0]
        self.END_FIGHT = monsql(name="ID", id=name,
                                attribute1="END_FIGHT")[0][0]
        self.END_SHOT = monsql(name="ID", id=name,
                               attribute1="END_SHOUT")[0][0]
        self.END_FAIL = monsql(name="ID", id=name, attribute1="END_FAIL")[0][0]


# 数量
'''侦查 数量
ALTER TABLE 表名 ADD COLUMN 新列字段名 数据类型
CREATE TABLE ATTRIBUTE
(
ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
QQ INT,
STR INT,
CON INT,
SIZ INT,
DEX INT,
APP INT,
INT INT,
POW INT,
EDU INT,
LUCKY INT,
HP INT,
SAN INT,
MAGIC1 VACHAR(40) DEFAULT "无",
MAGIC2 VACHAR(40) DEFAULT "无",
NEXT INT DEFAULT 1,      #下一个怪物id
FIGHT INT,
AVOID INT,
DETECT INT,
SHOT INT,
AID INT,
MEDICINE INT,
CLOTHES VACHAR(40) DEFAULT "普通衣物",
ARMOR INT DEFAULT 0,
DB VACHAR(10),
GUN VACHAR(60) DEFAULT ".22小型手枪",
WEAPONS VACHAR(60) DEFAULT "弹簧折刀",
WEAPONS_TYPE VACHAR(60) DEFAULT "1",
GUN_DAMAGE VACHAR(20) DEFAULT "1d6",
WEAPONS_DAMAGE VACHAR(20) DEFAULT "1d4+db",
NAME VACHAR(20) DEFAULT NULL,
RECORD VACHAR(25) DEFAULT NULL,
SPECIAL VACHAR(40) DEFAULT NULL
)

CREATE TABLE ATTRIBUTE
(
ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
QQ INT,
GOODSID INT,
GOODS VACHAR(40)
)

'''


class investigator:  # 调查员对象
    def __init__(self, QQ=GetMsgQQ()) -> None:
        self.CON = invsql(name="QQ", id=QQ, attribute1="CON")[0][0]
        self.SIZ = invsql(name="QQ", id=QQ, attribute1="SIZ")[0][0]
        self.APP = invsql(name="QQ", id=QQ, attribute1="APP")[0][0]
        self.INT = invsql(name="QQ", id=QQ, attribute1="INT")[0][0]
        self.EDU = invsql(name="QQ", id=QQ, attribute1="EDU")[0][0]
        self.DEX = invsql(name="QQ", id=QQ, attribute1="DEX")[0][0]
        self.STR = invsql(name="QQ", id=QQ, attribute1="STR")[0][0]
        self.POW = invsql(name="QQ", id=QQ, attribute1="POW")[0][0]
        self.LUCKY = invsql(name="QQ", id=QQ, attribute1="LUCKY")[0][0]
        self.SAN = invsql(name="QQ", id=QQ, attribute1="SAN")[0][0]
        self.DB = invsql(name="QQ", id=QQ, attribute1="DB")[0][0]
        self.HP = invsql(name="QQ", id=QQ, attribute1="HP")[0][0]
        self.FIGHT = invsql(name="QQ", id=QQ, attribute1="FIGHT")[0][0]
        self.AVOID = invsql(name="QQ", id=QQ, attribute1="AVOID")[0][0]
        self.DETECT = invsql(name="QQ", id=QQ, attribute1="DETECT")[0][0]
        self.SHOT = invsql(name="QQ", id=QQ, attribute1="SHOT")[0][0]
        self.AID = invsql(name="QQ", id=QQ, attribute1="AID")[0][0]
        self.MEDICINE = invsql(name="QQ", id=QQ, attribute1="MEDICINE")[0][0]
        self.CLOTHES = invsql(name="QQ", id=QQ, attribute1="CLOTHES")[0][0]
        self.ARMOR = invsql(name="QQ", id=QQ, attribute1="ARMOR")[0][0]
        self.GUN = invsql(name="QQ", id=QQ, attribute1="GUN")[0][0]  # 武器
        self.GUN_DAMAGE = invsql(name="QQ", id=QQ,
                                 attribute1="GUN_DAMAGE")[0][0]
        self.WEAPONS = invsql(name="QQ", id=QQ,
                              attribute1="WEAPONS")[0][0]  # 法术

        self.WEAPONS_DAMAGE = invsql(name="QQ",
                                     id=QQ,
                                     attribute1="WEAPONS_DAMAGE")[0][0]
        self.WEAPONS_TYPE = invsql(name="QQ", id=QQ,
                                   attribute1="WEAPONS_TYPE")[0][0]
        self.MAGIC1 = invsql(name="QQ", id=QQ, attribute1="MAGIC1")[0][0]
        self.MAGIC2 = invsql(name="QQ", id=QQ, attribute1="MAGIC2")[0][0]
        self.RECORD = invsql(name="QQ", id=QQ,
                             attribute1="RECORD")[0][0]  # 记录日期
        self.NEXT = invsql(name="QQ", id=QQ,
                           attribute1="NEXT")[0][0]  # 下一次的怪物ID
        self.BAG = sqlSel(data=investigator_data,
                          table="BAG",
                          name="QQ",
                          id=QQ,
                          attribute1="GOODSID")  # 物品
        if len(self.BAG) == 0:
            self.BAG = "空"
        else:
            self.BAG = "请输入*背包/*我的背包查看"
            return

    def able(QQ) -> bool:
        if invsql(name="QQ", id=QQ, attribute1="ID"):
            return True
        else:
            return False


'''
a = dice("5+d5+3d6")
print(a, sum(a))
s = creat(5)
print(s)
'''


def getName(QQ=GetMsgQQ()) -> str:
    name = sqlSel(data=investigator_data,
                  table="NAME",
                  name="QQ",
                  id=QQ,
                  attribute1="NAME")
    if len(name) == 0:
        return "[@%s]" % (QQ)
    else:
        return name[0]


def setName(par, QQ=GetMsgQQ()):  # 设置昵称，如果
    getName = sqlSel(data=investigator_data,
                     table="NAME",
                     name="QQ",
                     id=QQ,
                     attribute1="NAME")
    if len(getName) == 0:
        sqlIns(data=investigator_data,
               conn=investigator_conn,
               table="NAME",
               attribute="NAME,QQ",
               value=par[0],
               name="QQ",
               id=QQ)
    else:
        sqlUpd(data=investigator_data,
               conn=investigator_conn,
               table="NAME",
               attribute="NAME",
               value=par[0],
               name="QQ",
               id=QQ)
    Print(num=3, con_name=par[0])
    return


def getDate():
    i = datetime.datetime.now()
    data_time = "%s-%s-%s" % (i.year, i.month, i.day)
    return data_time


def getdb(siz, str) -> str:  # 输入体型体质，返回db
    sum1 = siz + str
    if sum1 == 0:
        return False
    if sum1 < 65:
        return "-2"
    elif sum1 < 85:
        return "-1"
    elif sum1 < 125:
        return "0"
    elif sum1 < 165:
        return "1d4"
    elif sum1 < 205:
        return "1d6"
    sum1 = sum1 - 205
    sum1 = int(sum1 / 80) + 2
    return "%dd6" % sum1


def dice(num, full=0) -> list:  # 返回出目列表，第一个字符串，第二个总伤害，每个就是出目,当full=1代表取满值
    print("dice:")
    print(num)
    if isinstance(num, int):
        return ["%s" % num, 0]
    if str.isdigit(num):
        return ["%s" % num, 0]
    con = []
    Damage = []
    par = num.split("+")
    for i in par:
        con.append(i.split("d"))
    i = 0
    lens = len(con)
    while i < lens:
        if con[i][0] == "":
            con[i][0] = "1"
        i = i + 1
    i = 0
    # 骰子个数
    while i < lens:
        dicenum = 0
        sight = 0
        if len(con[i]) > 1:
            while dicenum < int(con[i][0]):
                if full == 0:
                    sight = random.randint(1, int(con[i][1])) + sight  # 出目
                else:
                    sight = int(con[i][1]) + sight
                dicenum = dicenum + 1
            Damage.append(sight)
        else:
            Damage.append(int(con[i][0]))
        i = i + 1
    sums = sum(Damage)
    damaGet = []
    strs = ''
    damageLens = len(Damage)
    count = 0
    for s in Damage:
        if count < damageLens - 1:
            strs = strs + "%s+" % (s)
        else:
            strs = strs + "%s" % (s)
        count = count + 1
    damaGet.append(strs)
    damaGet.append(sums)
    return damaGet


def ratePun() -> list[int]:  # 返回list，惩罚骰后出目以及一个惩罚骰的值
    num = [0, 0, 0]
    s = random.randint(1, 100)
    pun = random.randint(0, 9)
    num[2] = s
    if int(s / 10) < pun:
        s = int(s % 10 + pun * 10)
    num[0] = s
    num[1] = pun
    return num


def rateBon() -> list[int]:
    num = [0, 0, 0]
    s = random.randint(1, 100)
    bon = random.randint(0, 9)
    num[2] = s
    if int(s / 10) > bon:
        s = int(s % 10 + bon * 10)
    num[0] = s
    num[1] = bon
    return num


def sqlSel(  # sql读取
        data,  # sql读取
        table,
        name,
        id,
        attribute1=None,
        attribute2=None,
        attribute3=None) -> list:
    if (not attribute1):
        strs = "select * from %s where %s = '%s'" % (table, name, id)
        return data.execute(strs).fetchall()
    elif (not attribute2):
        strs = "select %s from %s where %s='%s'" % (attribute1, table, name,
                                                    id)
        return data.execute(strs).fetchall()
    elif (not attribute3):
        strs = "select %s,%s from %s where %s='%s'" % (attribute1, attribute2,
                                                       table, name, id)
        return data.execute(strs).fetchall()
    else:
        strs = "select %s,%s,%s from %s where %s='%s'" % (
            attribute1, attribute2, attribute3, table, name, id)
        return data.execute(strs).fetchall()


def sqlIns(data, conn, table, attribute, value):
    strs = "insert into %s (%s) values (%s)" % (table, attribute, value)

    data.execute(strs)
    conn.commit()
    print("finish inserting")
    return


def sqlBag(attribute,
           value,
           data=investigator_data,
           conn=investigator_conn,
           table="BAG"):
    strs = "insert into %s (%s) values (%s)" % (table, attribute, value)

    data.execute(strs)
    conn.commit()
    print("finish inserting")
    return


def sqlUpd(data, conn, table, attribute, value, name, id):
    strs = "UPDATE %s SET %s = %s WHERE %s = %s" % (table, attribute, value,
                                                    name, id)

    data.execute(strs)
    conn.commit()
    print("finish updating")
    return


def sqlDel(data, conn, table, name, id):
    strs = "DELETE FROM %s  WHERE %s = %s" % (table, name, id)
    data.execute(strs)
    conn.commit()
    print("finish updating")
    return


def creat(time=1, QQ=GetMsgQQ()) -> dict:  # 创建调查员信息同时放入全局变量中
    attribute = {}
    if time < 1:
        time = 1
    for i in range(0, time):
        Str = int(int(dice("3d6")[1]) * 5)
        Con = int(int(dice("3d6")[1]) * 5)
        Siz = int(int(dice("2d6")[1] + 6) * 5)
        Dex = int(int(dice("3d6")[1]) * 5)
        App = int(int(dice("3d6")[1]) * 5)
        Int = int(int(dice("3d6")[1]) * 5)
        Pow = int(int(dice("3d6")[1]) * 5)
        Edu = int(int(dice("2d6")[1] + 6) * 5)
        Lucky = int(int(dice("3d6")[1]) * 5)
        attribute[i] = {}
        attribute[i]["STR"] = Str
        attribute[i]["CON"] = Con
        attribute[i]["SIZ"] = Siz
        attribute[i]["DEX"] = Dex
        attribute[i]["APP"] = App
        attribute[i]["INT"] = Int
        attribute[i]["POW"] = Pow
        attribute[i]["EDU"] = Edu
        attribute[i]["LUCKY"] = Lucky
    attributeRecord[QQ] = attribute
    return attribute


# 拼接字符串 返回可以方便写入数据库的格式,修改输入
def splice(res, Str, values):
    if len(res) == 0:
        res[0] = '%s' % Str
        res[1] = '%s' % values
    else:
        res[0] = res[0] + ',%s' % Str
        res[1] = res[1] + ',%s' % values
    return res


def inv_sql_creat(
    attribute_dict
):  # 不修改输入，(输入为一维字典)将属性列表作成方便写入数据库的格式，res[1]属性，res[2]数值,如果是字符类型的数据需要自带''
    attribute_get = attribute_dict
    res = {}
    for i in attribute_get:
        splice(res=res, Str=i, values=attribute_get[i])
    return res


# print(inv_sql_creat(creat(time=1)[0]))


def monsql(name,
           id,
           table="ATTRIBUTE",
           attribute1=None,
           attribute2=None,
           attribute3=None):  # 怪物读取
    return sqlSel(data=monster_data,
                  table=table,
                  name=name,
                  id=id,
                  attribute1=attribute1,
                  attribute2=attribute2,
                  attribute3=attribute3)


def invsql(name,
           id,
           table="ATTRIBUTE",
           attribute1=None,
           attribute2=None,
           attribute3=None):  # 调查员数据读取
    return sqlSel(data=investigator_data,
                  table=table,
                  name=name,
                  id=id,
                  attribute1=attribute1,
                  attribute2=attribute2,
                  attribute3=attribute3)


def Damage(
    succ,
    damage,
    db=0,
    Type=0,
    Type2=0
) -> list:  # [,]输入成功度，武器伤害，db，是否为贯穿武器，1为贯穿，0为不贯穿，返回[0]为输出伤害格式，[1]为总伤害
    dbget = ['0', 0]
    dbget2 = ['0', 0]
    print(succ, damage, db, Type, Type2)
    if succ > 4:
        print("输入错误，成功度大于4")
    elif succ == -1:
        dbget = ["-1", -1]
        damageget = ["-1", -1]
    elif succ == 0:
        dbget = ["0", 0]
        damageget = ["0", 0]
    elif succ == 1 or Type2 == 1 or succ == 2:
        dbget = dice(db)
        damageget = dice(damage)

    elif succ == 3:
        if Type == 1:
            dbget = dice(db, full=1)
            damageget = dice(damage, full=1)
            dbget2 = dice(damage)
        elif Type == 0:
            damageget = dice(damage, full=1)
            dbget = dice(db, full=1)
    elif succ == 4:  # 当大成功时，非贯穿武器，武器伤害加满，db加满，贯穿武器额外的武器伤害骰，同时取满
        if Type == 1:
            dbget = dice(db, full=1)
            damageget = dice(damage, full=1)
            dbget2 = damageget

        elif Type == 0:
            damageget = dice(damage, full=1)
            dbget = dice(db, full=1)
    if dbget2[1] == 0:
        if dbget[1] == 0:
            strs = damageget[0]
        else:
            strs = damageget[0] + "+" + dbget[0]
    else:
        if dbget[1] == 0:
            strs = damageget[0] + "+" + dbget2[0]
        else:
            strs = damageget[0] + "+" + dbget[0] + "+" + dbget2[0]
    print(1)
    sunms = damageget[1] + dbget[1] + dbget2[1]
    get = [strs, sunms]
    return get


def succ(
    skill,
    pun=0,
    bon=0,
) -> list:  # 返回list[0]出目list[1]惩罚骰/奖励骰数字，为-1代表没有惩罚骰/奖励骰list[2]成功度-1，0，1，2，3，4,
    if (not isinstance(skill, int)):
        print("Type error,输入应为int类型")
    if pun:
        s = ratePun()
        rand = s[0]
        pun = s[1]
        # print(s)
    elif bon:
        s = rateBon()
        rand = s[0]
        pun = s[1]
    else:
        rand = random.randint(1, 100)
        pun = -1
    if rand > 95:
        randGet = [rand, pun, -1]
        return randGet
    elif rand < 6:
        randGet = [rand, pun, 4]
        return randGet
    part = rand / skill
    if (part > 1):
        return [rand, pun, 0]
    elif (part > 0.5):
        return [rand, pun, 1]
    elif (part > 0.2):
        return [rand, pun, 2]
    else:
        return [rand, pun, 3]


def getShot(shot_rate,
            time=1,
            damage="1d10") -> list[int]:  # 射击方法，输入成功率，射击轮数，武器伤害
    dama = []  # list[0][0]出目，list[0][1]惩罚/奖励骰,
    # list[0][2]成功度,list[0][3]伤害列表(),list[0][4]db伤害（0/-1（大失败
    if time == 1:
        succGet = succ(shot_rate)
        res = (Damage(succ=succGet[2], damage=damage, Type=1))
        s = []
        for x in succGet:
            s.append(x)
        for y in res:
            s.append(y)
        dama.append(s)
    else:
        for i in range(time):
            succGet = succ(skill=shot_rate, pun=1)
            res = Damage(succ=succGet[2], damage=damage, Type=1)
            # print(res)
            s = []
            for x in succGet:
                s.append(x)
            for y in res:
                s.append(y)
            dama.append(s)
    return dama


# print(getShot(70))


def getFight(
    skill1,
    skill2,
    damage1,
    damage2=0,
    db1=0,
    db2=0,
    bonus1=0,
    bonus2=0,
    Type1=0,
    Type2=0,
):
    # Type1为攻击方武器是否贯穿，Type2为是否为反击
    # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
    # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
    dama = []
    succGet = succ(skill=skill1, bon=bonus1)
    res = (Damage(succ=succGet[2], damage=damage1, Type=Type1, db=db1))
    s = []
    for x in succGet:
        s.append(x)
    for y in res:
        s.append(y)
    dama.append(s)
    avoidGet = succ(skill=skill2, bon=bonus2)
    avoidRes = (Damage(succ=avoidGet[2], damage=damage2, Type2=Type2, db=db2))
    s = []
    for x in avoidGet:
        s.append(x)
    for y in avoidRes:
        s.append(y)
    dama.append(s)
    return dama


def getAttribute(attribute_list, time, QQ=GetMsgQQ(), TYPE=1):  # 将属性变换为中文
    if TYPE == 1:
        strs = "" + getName(QQ=QQ) + "的调查员作成：\n"
        for i in range(time):
            Sum = 0
            strs = strs + "[%s]" % (i + 1)
            for x in attribute_list[i]:
                Sum = Sum + attribute_list[i][x]
                strs = strs + DIC[x] + ":%s " % attribute_list[i][x]
            strs = strs + "总计：%s\n" % Sum
        strs = strs + "请选择序号创建调查员。(如*选择调查员1)"
    elif TYPE == 0:
        strs = "" + getName(QQ=QQ) + "的调查员属性：\n"
        i = 0
        for x in attribute_list:
            if x in DIC:
                strs = strs + DIC[x] + ":%s " % attribute_list[x]
                i = i + 1
                if x == "HP":
                    strs = strs + '\n'
                if i % 5 == 0:
                    strs = strs + '\n'
    elif TYPE == 2:
        strs = "" + getName(QQ=QQ) + "的调查员属性：\n"
        i = 0
        for x in attribute_list:
            if x in DIC:
                strs = strs + DIC[x] + ":%s " % attribute_list[x]
                i = i + 1
                if DIC[x] == "生命值" or DIC[x] == "医学" or DIC[x] == "护甲" or DIC[
                        x] == "枪械伤害" or DIC[x] == "武器伤害" or DIC[x] == "魔法位2":
                    strs = strs + '\n'
                    i = 1

                if i % 5 == 0:
                    strs = strs + '\n'
    return strs


# print(getAttribute(attribute_list=creat(time=4), time=4))


def Print(con="",
          con_attribute=0,
          num=0,
          Type=0,
          con_name=0,
          con_skill=0,
          con_dex1=0,
          con_dex2=0):
    if num == 0:
        Send(con)
    if num == 1:
        Send("你还没有创建调查员，先来创建调查员吧~\n（输入*创建调查员）")
    if num == 2:
        Send("请输入次数")
    if num == 3:
        Send("今后就叫你%s" % con_name)
    if num == 4:
        Send("你已经有创建好了的调查员了~")
    if num == 5:
        Send("创建成功，你的调查员属性为：\n%s" % con_attribute)
    if num == 6:
        Send("你当前拥有技能点数为：%s\n接下来请为技能分配点数如：*st侦查50格斗50（注：点数上限为75）" % con_skill)
    if num == 7:
        Send("创建格式不正确，最后部分应为数字")
    if num == 8:
        Send("技能点尚未用完，要继续创建吗？（输入*确认继续创建，或者重新分配点数）")
    if num == 9:
        Send("技能点使用过多")
    if num == 10:
        Send("创建完成")
    if num == 11:
        Send("你还没有创建调查员，请先创建调查员吧~")
    if num == 12:
        Send("%s ：敏捷->%s\n怪物：敏捷->%s " % (getName(), con_dex1, con_dex2))
    if num == 13:
        Send("你已经开始了今日的行动了哦~")
    if num == 14:
        Send("技能超过了75,请重新设置")
    if num == 15:
        Send("%s的回合，行动为：\n->*格斗\n->*射击\n->*三连射\n->*逃离" % (getName()))
    if num == 16:
        Send("%s的回合，行动为：\n->*格斗\n->*射击\n->*三连射\n->*法术1\n->*逃离" % (getName()))
    if num == 17:
        Send("%s的回合，行动为：\n->*格斗\n->*射击\n->*三连射\n->*使用法术1\n->*使用法术2\n->*逃离" %
             (getName()))
    if num == 18:
        Send("怪物的回合：")
    if num == 19:
        Send("%s的行动为：\n->*反击\n->*闪避\n->*逃离" % (getName()))
    if num == 50:
        Send("你不断前进，不断前进，转头看去，沙漠之中已经不知前往何方，渐渐的，你已经不知前往何方。")
        Send("而在此时，一颗星闪耀在你的眼前，它是如此的耀眼，你深深的为之所着迷，至此你开始追寻的路途——")

    time.sleep(1)


def succChange(rank):  # 等级
    if rank == -1:
        return "大失败"
    if rank == 0:
        return "失败"
    if rank == 1:
        return "成功"
    if rank == 2:
        return "困难成功"
    if rank == 3:
        return "极难成功"
    if rank == 4:
        return "大成功"


def getAction():
    return "反击"


def bon(name):
    if name == "食尸鬼":
        money = 20 + random.randint(1, 15)
        sqlBag(attribute="QQ", value=money)
    return


def pun():
    return


def Fight(par, QQ=GetMsgQQ()):
    turn = fightRecord[QQ]["turn"]
    mon = fightRecord[QQ]["monster"]
    inv = fightRecord[QQ]["attribute"]
    inv['WEAPONS_DAMAGE'] = inv['WEAPONS_DAMAGE'].replace("+db", '')
    mon['damage1'] = mon['damage1'].replace("+db", '')
    invSkill = 0  # 用于剔除不正确的指令
    if turn == "怪物":  # 怪物回合
        if par[0] == "反击":
            invSkill = inv["FIGHT"]
            invDamage = inv["WEAPONS_DAMAGE"]
        if par[0] == "闪避":
            invSkill = inv["AVOID"]
            invDamage = '0'
        if par[0] == "逃离":
            invSkill = inv["DEX"]
            invDamage = '0'
        if mon["fight_way"] == "格斗":
            monSkill = mon["fight"]
            monDamage = mon["damage1"]
        if mon["fight_way"] == "射击":  # 这里添加射击的函数
            monSkill = mon["shot"]
            monDamage = mon["damage2"]
        if invSkill == 0:
            return
        invDamage2 = invDamage + "+" + inv['DB']
        if par[0] == "反击":
            lists = fight_fight(skill1=monSkill,
                                skill2=invSkill,
                                damage1=monDamage,
                                damage2=invDamage,
                                db1=mon["db"],
                                db2=inv['DB'],
                                Type1=mon["fre"])
            str1 = "你挥舞着手中的利刃朝眼前的怪物攻去。"
            strs = str1 + "\n对抗——>\n%s：%s/%s->%s\n%s：%s/%s->%s" % (
                mon["name"], lists[0], monSkill, succChange(rank=lists[1]),
                getName(), lists[2], invSkill, succChange(rank=lists[3]))
            Print(strs)
            # 返回1出目，1成功度，2出目,2成功度，伤害文本，总伤害，特征--0 反击失败，1反击成功
            if lists[3] == -1:  # 调查员大失败时
                if inv["WEAPONS"] == "弹簧折刀":
                    dam = random.randint(1, 4)
                    Print("你用力拿起手中的利刃，朝眼前的怪物发起了攻势，" +
                          "但是却因用力过大，利刃扎在了身上，血流不止。受到%s点伤害" % dam)
                    inv["HP"] = inv["HP"] - dam
                else:
                    inv["WEAPONS"] = "弹簧折刀"
                    inv['WEAPONS_DAMAGE'] = '1d4+db'
                    Print("你用力拿起手中的利刃，朝眼前的怪物发起了攻势，" +
                          "但是却因用力过大，利刃被你一下扔了出去，看来只能先解决眼前的怪物了。")
            if lists[5] == 0:  # 反击失败
                if lists[3] == -1:  # 一起大失败
                    Print("怪物朝你扑来，但是仅仅只是与你擦肩而过.")
                else:  # 怪物失败
                    Print("怪物朝你扑来，但是仅仅只是与你擦肩而过，而你的攻击也同样打在了空处")

            elif lists[6] > 0:  # 反击成功
                Sum = lists[5]
                Print("反击成功，你手中的利刃精准的刺在了怪物身上。\n" + "造成伤害%s->%s->%s" %
                      (invDamage2, lists[4], Sum))
                damage = Sum - mon["armor"]
                if damage < 0:
                    damage = 0
                mon["hp"] = mon["hp"] - damage
            else:  # 反击失败

                Print(mon["FIGHT_SUCC"])
                Sum = lists[5]
                armor = inv["ARMOR"]
                damage = Sum - armor
                if damage < 0:
                    damage = 0
                inv["HP"] = inv["HP"] - damage
                Print("反击失败，受到伤害:%s->%s-%s->%s\n剩余HP:%s" %
                      (monDamage, lists[4], armor, damage, inv["HP"]))

        if par[0] == "闪避":
            lists = fight_avoid(skill1=monSkill,
                                skill2=invSkill,
                                db1=mon["db"],
                                damage1=monDamage,
                                Type1=mon["fre"])
            # Type1为攻击方武器是否贯穿，Type2为是否为反击
            # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
            # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
            # 返回1出目[0]，1成功度[1]，2出目[2],2成功度[3]，伤害文本[4]，总伤害[5]，
            # [6]特征--0 闪避失败，1闪避成功
            str1 = "你侧身一转，准备躲开怪物的攻击。"
            strs = str1 + "\n对抗——>\n%s：%s/%s->%s\n%s：%s/%s->%s" % (
                mon["name"], lists[0], monSkill, succChange(rank=lists[1]),
                getName(), lists[2], invSkill, succChange(rank=lists[3]))
            Print(strs)
            damage_text = lists[4]
            damage_sum = lists[5]
            if damage_sum > 0:
                armor = inv["ARMOR"]
                damage = damage_sum - armor
                if damage < 0:
                    damage = 0
                inv["HP"] = inv["HP"] - damage
                Print(mon["FIGHT_SUCC"])
                Print("闪避失败，受到伤害%s->%s-%s->%s\n剩余HP:%s" %
                      (monDamage, damage_text, armor, damage, inv["HP"]))
            if damage_sum == 0:
                Print(mon["FIGHT_FAIL"])
                Print("你成功的躲开了怪物的攻击。")
        if mon["hp"] < 1:

            Print(mon['END_FIGHT'])
            del fightRecord[QQ]
            bon()
        elif inv["HP"] < 1:

            Print(mon['END_FAIL'])
            del fightRecord[QQ]
            pun()
        elif inv['MAGIC1'] == 0:
            Print(num=15)  # 没有法术1
            fightRecord[QQ]["turn"] = "调查员"
        elif inv['MAGIC2'] == 0:
            Print(num=16)  # 没有法术2
            fightRecord[QQ]["turn"] = "调查员"
        else:
            Print(num=17)  # 法术1，2都有
            fightRecord[QQ]["turn"] = "调查员"

    if turn == "调查员":

        if par[0] == "格斗":
            invDamage = inv["WEAPONS_DAMAGE"]
            invDamage2 = inv["WEAPONS_DAMAGE"] + "+" + inv["DB"]
            if getAction() == "反击":
                monDamage = mon["damage1"]
                Print(mon["CONTER_CG"])
                lists = fight_fight(skill1=inv["FIGHT"],
                                    skill2=mon["fight"],
                                    db1=inv["DB"],
                                    db2=mon['db'],
                                    Type1=inv["WEAPONS_TYPE"],
                                    damage1=inv["WEAPONS_DAMAGE"],
                                    damage2=mon["damage1"])
                strs = "对抗——>\n%s：%s/%s->%s\n%s：%s/%s->%s" % (
                    getName(), lists[0], inv["FIGHT"],
                    succChange(rank=lists[1]), mon["name"], lists[2],
                    mon["fight"], succChange(rank=lists[3]))
                Print(strs)
                a = lists[1]
                damage_text = lists[4]
                damage_sum = lists[5]
                if a == -1:
                    if inv["WEAPONS"] == "弹簧折刀":
                        dam = random.randint(1, 4)
                        Print("你用力拿起手中的利刃，朝眼前的怪物发起了攻势，" +
                              "但是却因用力过大，利刃扎在了身上，血流不止。受到%s点伤害" % dam)
                        inv["HP"] = inv["HP"] - dam
                    else:
                        inv["WEAPONS"] = "弹簧折刀"
                        inv['WEAPONS_DAMAGE'] = '1d4+db'
                        Print("你用力拿起手中的利刃，朝眼前的怪物发起了攻势，" +
                              "但是却因用力过大，利刃被你一下扔了出去，看来只能先解决眼前的怪物了。")
                if lists[5] == 0:
                    if lists[3] == -1:
                        Print("怪物朝你扑来，但是仅仅只是与你擦肩而过.")
                    else:
                        Print("怪物朝你扑来，但是仅仅只是与你擦肩而过，而你的攻击也同样打在了空处")

                elif lists[6] > 0:
                    Sum = damage_sum
                    armor = inv["ARMOR"]
                    damage = Sum - armor
                    if damage < 0:
                        damage = 0
                    inv["HP"] = inv["HP"] - damage
                    Print(mon["CONTER_SUCC"] +
                          "\n受到伤害:%s->%s-%s->%s\n剩余HP:%s" %
                          (monDamage, damage_text, armor, damage, inv["HP"]))
                else:
                    Sum = damage_sum
                    armor = inv["ARMOR"]
                    damage = Sum - armor
                    if damage < 0:
                        damage = 0
                    mon["hp"] = mon["hp"] - damage
                    Print(mon["CONTER_FAIL"] + "造成伤害:%s->%s->%s" % (
                        invDamage2,
                        damage_text,
                        Sum,
                    ))

            if getAction() == "闪避":
                lists = fight_avoid(skill1=invSkill,
                                    skill2=monSkill,
                                    db1=inv["db"],
                                    damage1=invDamage,
                                    Type1=inv["WEAPONS_TYPE"])
                # Type1为攻击方武器是否贯穿，Type2为是否为反击
                # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
                # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
                # 返回1出目[0]，1成功度[1]，2出目[2],2成功度[3]，伤害文本[4]，总伤害[5]，
                # [6]特征--0 闪避失败，1闪避成功
                Print(mon["AVOID_CG"])
                strs = "\n对抗——>\n%s：%s/%s->%s\n%s：%s/%s->%s" % (
                    getName(), lists[0], monSkill, succChange(rank=lists[1]),
                    mon["name"], lists[2], invSkill, succChange(rank=lists[3]))
                Print(strs)
                damage_text = lists[4]
                damage_sum = lists[5]
                if damage_sum > 0:
                    armor = mon["armor"]
                    damage = damage_sum - armor
                    if damage < 0:
                        damage = 0
                    mon["hp"] = mon["hp"] - damage
                    Print(mon["AVOID_FAIL"])
                    Print("造成伤害%s->%s->%s" %
                          (invDamage2, damage_text, damage_sum))
                if damage_sum == 0:
                    Print(mon["AVOID_SUCC"])
                    Print("怪物成功的躲开了你的攻击。")
        if par[0] == "射击":
            # list[0][0]出目，list[0][1]惩罚/奖励骰,
            # list[0][2]成功度,list[0][3]伤害列表(),list[0][4]总伤害（0/-1（大失败
            lists = getShot(shot_rate=inv["SHOT"], damage=inv["GUN_DAMAGE"])

            if lists[0][2] > 0:

                Sum = lists[0][4]
                armor = mon["armor"]
                damage = Sum - armor
                if damage < 0:
                    damage = 0
                mon["hp"] = mon["hp"] - damage
                Print("你拿起了手中的武器准备射击—>\n" +
                      "射击鉴定——>：\n%s/%s->%s\n造成伤害%s->%s->%s" %
                      (lists[0][0], inv["SHOT"], succChange(rank=lists[0][2]),
                       inv["GUN_DAMAGE"], lists[0][3], Sum))
            if lists[0][2] == 0:
                Print("你拿起了手中的武器准备射击—>\n" +
                      "射击鉴定——>：\n%s/%s->%s\n子弹从怪物身旁飞过，并未命中目标。" % (
                          lists[0][0],
                          inv["SHOT"],
                          succChange(rank=lists[0][2]),
                      ))
            if lists[0][2] == -1:
                Print("你拿起了手中的武器准备射击—>\n" +
                      "射击鉴定——>：\n%s/%s->%s\n子弹从怪物身旁飞过，并未命中目标。" % (
                          lists[0][1],
                          inv["SHOT"],
                          succChange(rank=lists[0][2]),
                      ))

        if par[0] == "三连射":
            lists = getShot(shot_rate=inv["SHOT"],
                            time=3,
                            damage=inv["GUN_DAMAGE"])
            strs = "你拿起了手中的武器朝眼前的怪物连开三枪—>\n射击鉴定——>\n"
            for i in range(3):
                if lists[i][2] > 0:

                    Sum = lists[i][4]
                    armor = mon["armor"]
                    damage = Sum - armor
                    if damage < 0:
                        damage = 0
                    mon["hp"] = mon["hp"] - damage
                    strs = strs + "%s/%s（惩罚骰：%s）->%s\n造成伤害%s->%s\n" % (
                        (lists[i][0], inv["SHOT"], lists[i][1],
                         succChange(rank=lists[i][2]), inv["GUN_DAMAGE"], Sum))
                if lists[i][2] == -1:

                    strs = strs + "%s/%s（惩罚骰：%s）->%s\n子弹从怪物身旁飞过，并未命中目标。\n" % (
                        lists[i][0], inv["SHOT"], lists[i][1],
                        succChange(rank=lists[i][2]))
                if lists[i][2] == 0:

                    strs = strs + "%s/%s（惩罚骰：%s）->%s\n子弹从怪物身旁飞过，并未命中目标。\n" % (
                        lists[i][0], inv["SHOT"], lists[i][1],
                        succChange(rank=lists[i][2]))
            Print(strs)

        if par[0] == "逃离":
            magic()
        if par[0] == "使用法术1":
            magic()
        if par[0] == "使用法术2":
            if not fightRecord[QQ]['MAGIC1'] == "空":
                magic()
                Print(strs)
        if mon["hp"] < 1:
            Print(mon['END_FIGHT'])
            del fightRecord[QQ]
        elif inv["HP"] < 1:
            Print(mon['END_FAIL'])
            del fightRecord[QQ]
        else:
            fightRecord[QQ]["turn"] = "怪物"
            if mon["fight_way"] == "格斗":
                Print("怪物的回合：\n" + mon["FIGHT_CG"])
                Print(num=19)
            if mon["fight_way"] == "射击":
                Print("怪物的回合：\n" + mon["FIGHT2_CG"])
                Print(num=19)

    return


def fight_fight(skill1,
                skill2,
                damage1,
                damage2,
                db1,
                db2,
                bonus1=0,
                bonus2=0,
                Type1=0):
    get = getFight(skill1=skill1,
                   skill2=skill2,
                   damage1=damage1,
                   damage2=damage2,
                   db1=db1,
                   db2=db2,
                   bonus1=bonus1,
                   bonus2=bonus2,
                   Type1=Type1,
                   Type2=1)
    # Type1为攻击方武器是否贯穿，Type2为是否为反击
    # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
    # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
    # 返回1出目，1成功度，2出目,2成功度，伤害文本，总伤害，特征--0 反击失败，1反击成功
    a = get[0][2]
    b = get[1][2]
    end1 = get[0][0]
    end2 = get[1][0]
    Bool = 0
    res = []
    if a < 1:
        if b > 0:  # 反击成功
            damage_text = get[1][3]
            damage_num = get[1][4]
            Bool = 1
        else:
            damage_text = ''
            damage_num = 0
    else:
        if a < b:
            damage_text = get[1][3]
            damage_num = get[1][4]
            Bool = 1
        else:
            damage_text = get[0][3]
            damage_num = get[0][4]
    res = [end1, a, end2, b, damage_text, damage_num, Bool]
    return res


# print(fight_fight(65, 65, "1d3", "1d4", "0", "0"))


def fight_avoid(skill1, skill2, damage1, db1, bonus1=0, bonus2=0, Type1=0):
    get = getFight(skill1=skill1,
                   skill2=skill2,
                   damage1=damage1,
                   damage2=0,
                   db1=db1,
                   db2=0,
                   bonus1=bonus1,
                   bonus2=bonus2,
                   Type1=Type1,
                   Type2=1)
    # Type1为攻击方武器是否贯穿，Type2为是否为反击
    # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
    # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
    # 返回1出目，1成功度，2出目,2成功度，伤害文本，总伤害，特征--0 闪避失败，1闪避成功
    a = get[0][2]
    b = get[1][2]
    end1 = get[0][0]
    end2 = get[1][0]
    Bool = 0
    res = []
    if a < 1:
        damage_text = ''
        damage_num = 0
        Bool = 1
    else:
        if a > b:
            damage_text = get[0][3]
            damage_num = get[0][4]
        else:
            damage_text = ''
            damage_num = 0
            Bool = 1
    res = [end1, a, end2, b, damage_text, damage_num, Bool]
    return res


def magic():
    return


def inv_mon(QQ, par, inv=0, mon=0):

    if fightRecord[QQ]["turn"] == '0':
        turn = 0
        Print(num=50)
        # fightRecord[QQ]["time"] = 1
        Print(mon.START)
        Print("——————战斗开始——————")
        Print(num=12, con_dex1=inv.DEX, con_dex2=mon.dex)
        i = datetime.datetime.now()
        data_time = "'%s-%s-%s'" % (i.year, i.month, i.day)
        sqlUpd(data=investigator_data,
               conn=investigator_conn,
               table="ATTRIBUTE",
               attribute="RECORD",
               name="QQ",
               id=QQ,
               value=data_time)
        if inv.DEX == mon.dex:
            lists = getFight(skill1=inv.DEX, skill2=mon.dex, damage1="1d4")
            # Type1为攻击方武器是否贯穿，Type2为是否为反击
            # list[0][0]出目，list[0][1]惩罚/奖励骰,list[0][2]成功度,
            # list[0][3]伤害,list[0][4]总伤害（0/-1（大失败
            Print(
                "敏捷对抗——>\n%s：%s/%s->%s\n%s：%s/%s->%s" %
                (getName(), lists[0][0], inv.DEX, succChange(rank=lists[0][2]),
                 mon.name, lists[1][0], mon.dex, succChange(rank=lists[1][2])))
            if lists[0][2] > lists[1][2]:
                turn = "调查员"
            else:
                turn = "怪物"
        if inv.DEX > mon.dex or turn == 1:
            fightRecord[QQ]["turn"] = "调查员"
            if inv.MAGIC1 == "无":
                Print(num=15)  # 没有法术1
            elif inv.MAGIC2 == "无":
                Print(num=16)  # 没有法术2
            else:
                Print(num=17)  # 法术1，2都有

        else:
            fightRecord[QQ]["turn"] = "怪物"
            Print(num=18)
            if mon.fight_way == 1:  # 输出第一段CG
                Print(mon.FIGHT_CG)
            elif mon.fight_way == 2:
                Print(mon.FIGHT2_CG)
            Print(num=19)
        for key in inv.__dict__:
            fightRecord[QQ]["attribute"][key] = inv.__dict__[key]
        for key in mon.__dict__:
            fightRecord[QQ]["monster"][key] = mon.__dict__[key]
        # damage = inv.WEAPONS_DAMAGE.replace("db", inv.DB)
        # fightRecord[QQ]["attribute"]["WEAPONS_DAMAGE"] = damage
    else:
        Print("你的冒险已经开始了~")
        return

    print(fightRecord)
    return


def getOtherAttribute(  # 急救 AID 医学
        attribute):
    # 获取衍生属性输入为{'STR':65,'CON',.....}，输出将衍生属性添加到dict中
    DB = "'%s'" % (getdb(siz=attribute['SIZ'], str=attribute['STR']))
    HP = int((attribute['CON'] + attribute['SIZ']) / 10)
    AVOID = int(attribute['DEX'] / 2)
    SHOT = 20
    FIGHT = 25
    CHECK = 25
    AID = 30
    MEDICINE = 1
    SAN = attribute['POW']
    attribute['HP'] = HP
    attribute['SAN'] = SAN
    attribute['DB'] = DB
    attribute['FIGHT'] = FIGHT
    attribute['AVOID'] = AVOID
    attribute['SHOT'] = SHOT
    attribute['DETECT'] = CHECK
    attribute['AID'] = AID
    attribute['MEDICINE'] = MEDICINE
    return attribute


def getTime():
    return 3


def getSkillPoint(attribute):
    return int(attribute['EDU'] * 2 + attribute['INT'])


def investigatorCreate(lenget, time, QQ=GetMsgQQ()):
    if lenget == 0:
        # 需要增加判断之前是否已经创建过调查员
        attribute = creat(time=time)
        # 随机属性，同时写入全局变量attributeRecord[QQ][TIME][ATTRIBUTE]
        strs = getAttribute(attribute_list=attribute, time=time, QQ=QQ)
        # 拼接字符串，返回字段
        Print(con=strs, num=0)
        # 输出字段
    else:
        Print(num=4)


def attributeSelect(lenGet, par, time, QQ=GetMsgQQ()):
    matchObj1 = re.match('选择调查员([1-%s])' % (time), par[0],
                         re.M | re.I)  # 正则匹配得到玩家的选择
    if matchObj1:
        if attributeRecord[QQ]:
            select = int(matchObj1.group(1)) - 1
            if lenGet == 0:
                attribute = attributeRecord[QQ][select]  # 获取选择的数据
                attribute = getOtherAttribute(
                    attribute=attribute)  # 获取其他衍生属性，并写入到全局变量
                attributeAdd = attribute.copy()  # 复制属性并添加QQ
                attributeAdd['QQ'] = QQ
                write = inv_sql_creat(attributeAdd)  # 转换为方便写入数据库的字符
                sqlIns(
                    data=investigator_data,  # 写入数据库
                    conn=investigator_conn,
                    table="ATTRIBUTE",
                    attribute=write[0],
                    value=write[1])
                strs = getAttribute(attribute_list=attribute,
                                    time=0,
                                    QQ=QQ,
                                    TYPE=0)
                print(strs)
                Print(con_attribute=strs, num=5)  # 发送创建好的人物信息
                del attributeRecord[QQ]
                attributeRecord[QQ] = {}
                attributeRecord[QQ]["select"] = attribute  # 将选择好的属性放入全局变量之中
                skillPoint = getSkillPoint(attribute)  # 获取技能点数量
                attributeRecord[QQ]["select"][
                    "skill"] = skillPoint  # 将技能点数写入全局变量中
                Print(num=6, con_skill=skillPoint)
                return True
        else:
            Print(num=11)


def attributeSet(par, QQ=GetMsgQQ()):
    pattern = re.compile(r'st+|[^\d\s]+|\d+')
    matchObj2 = pattern.findall(par[0])
    print(matchObj2[0])
    if matchObj2:
        count = 0  # 计数
        sumSkill = 0
        if not matchObj2[0] == "st":  # 不是设置命令
            return False
        elif not str.isdigit(matchObj2[-1]):  # 最后一位不是数字出现错误
            Print(num=7)
            return True
        elif attributeRecord[QQ]["select"]["skill"] > 0:
            attributeRecord[QQ]["set"] = {}
            for i in range(1, len(matchObj2)):  # 遍历文本 侦查 75 聆听 35
                count = count + 1
                if count % 2 == 1:
                    if not str.isdigit(matchObj2[i]):
                        for key in DIC2:
                            if matchObj2[i] == DIC2[key]:
                                skillGet = int(matchObj2[i + 1])  # 获取技能数值
                                if skillGet > 75:
                                    print(num=14)
                                    return
                                else:
                                    usedSkill = skillGet - attributeRecord[QQ][
                                        "select"][key]
                                    sumSkill = sumSkill + usedSkill
                                    attributeRecord[QQ]["set"][key] = skillGet
            if sumSkill < attributeRecord[QQ]["select"]["skill"]:  # 未用完
                Print(num=8)
                return True
            elif sumSkill > attributeRecord[QQ]["select"]["skill"]:  # 过多
                Print(num=9)
                return True
            else:
                Print(num=10)
                for key in attributeRecord[QQ]["set"]:
                    sqlUpd(
                        data=investigator_data,  # 写入数据库
                        conn=investigator_conn,
                        table="ATTRIBUTE",
                        name="QQ",
                        id=QQ,
                        attribute=key,
                        value=attributeRecord[QQ]["set"][key])
                attributeRecord[QQ]["select"]["skill"] = 0
                return True


def getInvestigator(inv, QQ=GetMsgQQ()):
    inv = investigator(QQ)
    '''for key in inv.__dict__:
        if key in Dict:
            get[key]='''

    return getAttribute(attribute_list=inv.__dict__,
                        time=0,
                        QQ=GetMsgQQ(),
                        TYPE=2)


def main(par, QQ=GetMsgQQ()):
    if len(par) == 0:
        return
    if QQ == "1787569211" or QQ == "100000":  # 清空指令
        if par[0] == "清空":
            attributeRecord.clear()
            fightRecord.clear()
            Print("清空完成")
            return

    lenGet = len(
        sqlSel(data=investigator_data, table="ATTRIBUTE", name="QQ", id=QQ))
    if par[0] == "开始冒险！" or par[0] == "前进！":
        if lenGet == 0:
            Print(num=1)  # 进行调查员创建

        else:
            inv = investigator(QQ)
            mon = monster(inv.NEXT)
            if QQ in fightRecord:
                return
            if getDate() == inv.RECORD:
                Print("今天已经进行过冒险了，明天继续吧~")
                #  return
            fightRecord[QQ] = {
                "monster": {},
                "attribute": {},
                "turn": '0',
                "PRINT": 0
            }

            inv_mon(par=par, inv=inv, mon=mon, QQ=QQ)  # 开始战斗
            return

    time = getTime()  # 创建次数
    if par[0] == "创建调查员":
        investigatorCreate(lenget=lenGet, time=time, QQ=GetMsgQQ())
        return

    # 选择调查员属性
    if attributeSelect(lenGet=lenGet, par=par, time=time, QQ=GetMsgQQ()):
        return
    # 设置调查员属性（*st侦查70————）
    if attributeSet(par, QQ=GetMsgQQ()):
        return
    if par[0] == "确认继续创建":
        Print(num=10)
        for key in attributeRecord[QQ]["set"]:
            sqlUpd(
                data=investigator_data,  # 写入数据库
                conn=investigator_conn,
                table="ATTRIBUTE",
                name="QQ",
                id=QQ,
                attribute=key,
                value=attributeRecord[QQ]["set"][key])
        attributeRecord[QQ]["select"]["skill"] = 0
        return

    print(attributeRecord)
    if par[0] == "我的调查员":
        if lenGet == 0:
            Print(num=1)
        else:
            inv = investigator(QQ)
            strs = getInvestigator(inv=inv, QQ=QQ)
            Print(con=strs, num=0)
        return

    if par[0] == "闪避" or par[0] == "反击" or par[0] == "格斗" or par[
            0] == "射击" or par[0] == "三连射" or par[0] == "使用道具" or par[
                0] == "使用魔法1" or par[0] == "使用魔法2":
        if QQ not in fightRecord:
            return
        Fight(par, QQ=QQ)
        return

    if par[0] == "反击":
        return

    if par[0] == "格斗":
        return

    if par[0] == "射击":
        return

    if par[0] == "三连射":
        return

    if par[0] == "使用道具":
        return

    if par[0] == "使用魔法1":
        return

    if par[0] == "使用魔法2":
        return


# print(re.match(r'创建调查员([0-9])', "sad", re.M | re.I).group(1))

# print(len(sqlSel(data=investigator_data, table="ATTRIBUTE", name="QQ",
#                 id=123)))
# print(fight(skill1=70, skill2=60, damage1="2d6", Type1=1))
