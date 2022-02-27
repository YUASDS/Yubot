import os
import json
import random

from pathlib import Path
from graia.saya import Saya, Channel
from graia.ariadne.model import Group
from graia.ariadne.message.element import Member,Source
from graia.ariadne.event.message import GroupMessage,FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from util.sendMessage import safeSendGroupMessage
from util.control import Permission, Interval, Rest
from database.db import favor,get_info,add_favor,reduce_favor


func = os.path.dirname(__file__).split("\\")[-1]
FAVOR_PATH= Path(__file__).parent.joinpath("favor_chat_data.json")
COUNT_PATH=Path(__file__).parent.joinpath("count.txt")
favor_data:dict=json.loads(FAVOR_PATH.read_text(encoding="utf-8"))

saya = Saya.current()
channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage,FriendMessage],
        inline_dispatchers=[
            Twilight({
                "head": RegexMatch("(\S)*(千音)(\S)*",)
            })
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control(),
            Interval.require(15)
        ],
    ))
async def main(group: Group, head: RegexMatch, member: Member,source:Source):
    info=await get_info(str(member.id))
    # global PATH
    with open (file=COUNT_PATH,mode="r",encoding="utf-8") as c:
        count=int(c.read())
    order=head.result.asDisplay()
    pun=0
    bon=0
    info_favor=favor(info["favor"])
    if order in favor_data:   # 如果有这条好感度回复
        level_min=favor_data[order]["min"]
        level_max=favor_data[order]["max"]
        if info_favor.level>level_min:   # 如果满足最低好感度回复
            succ_rate=favor_data[order]["成功率"]
            rate_get=random.randint(1,100)
            if rate_get<succ_rate:  
                if info_favor.res<5: # 当好感度刚升级未超过5更容易触发本等级的回复
                    if info_favor.level>level_max: # 如果超过最高好感度回复等级
                        favor_choice=random.randint(2**level_min,2**level_max)
                    else:
                        favor_choice=random.randint(2**level_min,get_favor_full(info_favor.level))
                    level_choice=get_level(favor_choice) # 获取到触发回复的等级
                else:
                    if info_favor.level>level_max:# 如果超过没有最高好感度回复等级
                        level_choice=random.randint(level_min,level_max)
                    else:
                        level_choice==random.randint(level_min,info_favor.level)
                bon=random.randint(1,favor_data[order]["奖励"])
                reply=random.choice(favor_data[order][str(level_choice)]) #获取一条随机的回复
            else:
                reply=random.choice(favor_data[order]["失败"])
                if "惩罚" in favor_data[order]:
                    pun:int=favor_data[order]["惩罚"]
        else:
            reply=random.choice(favor_data[order]["失败"])
            if "惩罚" in favor_data[order]:
                    pun:int=favor_data[order]["惩罚"]
        if bon>0:
            count+=1
            if count<100:
                await add_favor(str(member.id),num=bon)
                with open (file=COUNT_PATH,mode="w",encoding="utf-8") as c:
                    c.write(str(count))
            else:
                with open (file=COUNT_PATH,mode="w",encoding="utf-8") as c:
                    c.write('1')
                bon=random.randint(10,20)
                await add_favor(str(member.id),num=bon)
                reply=random.choice(favor_data[order]["大成功"])
                await safeSendGroupMessage(group, MessageChain.create("千音完美亲和触发"))
        else:
            await reduce_favor(str(member.id),num=pun)
        await safeSendGroupMessage(group, MessageChain.create(reply),quote=source)
    else:
        pass

def  get_level(favors:int)->int: # 当前等级
    level=1
    while(2**level<favors or 2**level==favors):
        favors=favors-2**level
        level+=1
    return level

def get_favor_full(level:int)->int:
    favors=0
    for i in range(level+1):
        favors+=2**i
    return favors

