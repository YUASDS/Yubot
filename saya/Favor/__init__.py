import os
import json
import random
import time

from pathlib import Path
from typing import DefaultDict,Tuple
from collections import defaultdict
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.ariadne.model import Member,Friend
from graia.broadcast.exceptions import ExecutionStop
from graia.ariadne.event.message import MessageEvent,FriendMessage,GroupMessage
from graia.ariadne.message.chain import MessageChain,Source
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.parser.twilight import Twilight, RegexMatch

from util.sendMessage import autoSendMessage
from util.control import Permission, Rest
from database.db import favor,get_info,add_favor,reduce_favor


func = os.path.dirname(__file__).split("\\")[-1]
FAVOR_PATH= Path(__file__).parent.joinpath("favor_chat_data.json")
COUNT_PATH=Path(__file__).parent.joinpath("count.txt")
favor_data:dict=json.loads(FAVOR_PATH.read_text(encoding="utf-8"))
key_word = "|".join(list(favor_data))

last_exe=[]


saya = Saya.current()
channel = Channel.current()


async def get_reply(order:str,qq:int):
    if order not in favor_data:   # 如果有这条好感度回复
        
        return None
    pun=0
    bon=0
    with open (file=COUNT_PATH,mode="r",encoding="utf-8") as c:
        count:int=int(c.read())
    info=await get_info(str(qq))
    info_favor=favor(info["favor"])
    level_min=favor_data[order]["min"]
    level_max=favor_data[order]["max"]
    reply=[]
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
            elif info_favor.level>level_max:# 如果超过没有最高好感度回复等级
                level_choice=random.randint(level_min,level_max)
            else:
                level_choice=random.randint(level_min,info_favor.level)
            bon=random.randint(1,favor_data[order]["奖励"]) # 获取奖励
            reply.append(random.choice(favor_data[order][str(level_choice)])) #获取一条随机的回复
        else:
            reply.append(random.choice(favor_data[order]["失败"]))
            if "惩罚" in favor_data[order]:
                pun:int=random.randint(1,favor_data[order]["惩罚"])
    else:
        reply.append(random.choice(favor_data[order]["失败"]))
        if "惩罚" in favor_data[order]:
                pun:int=favor_data[order]["惩罚"]
    if bon>0:
        count+=1
        if count<100:
            with open (file=COUNT_PATH,mode="w",encoding="utf-8") as c:
                c.write(str(count))
            await add_favor(str(qq),num=bon)
        else:
            with open (file=COUNT_PATH,mode="w",encoding="utf-8") as c:
                c.write('1')
            bon=random.randint(10,20)
            reply = ["千音完美亲和触发", random.choice(favor_data[order]["大成功"])]
            await add_favor(str(qq),num=bon,force=True)
    elif pun>0:
        await reduce_favor(str(qq),num=pun)
    return count,reply



def get_level(favors:int) -> int: # 当前等级
    level=1
    while (2**level<favors or 2**level==favors):
        favors -= 2**level
        level+=1
    return level

def get_favor_full(level:int) -> int:
    return sum(2**i for i in range(level+1))

last_exec_favor:DefaultDict[str, Tuple[int, float]]=defaultdict(lambda: (1, 0.0))
async def cd_check(event:MessageEvent, suspend_time:float=60, silent:bool=False, sent_alert = None):
    if sent_alert is None:
        sent_alert = []
    current = time.time()
    eid=str(event.sender.id)
    if current - last_exec_favor[eid][1] >= suspend_time:
        last_exec_favor[eid] = (1, current)
        if eid in sent_alert:
            sent_alert.remove(eid)
        return
    if eid not in sent_alert:
        app:Ariadne=Ariadne.get_running()
        if not silent:
            if isinstance(event.sender,Member):
                await app.sendGroupMessage(
                    event.sender.group,
                    MessageChain.create(
                        "前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）"
                    ),
                    quote=event.messageChain.getFirst(Source).id,
                )

            elif isinstance(event.sender,Friend):

                await app.sendFriendMessage(
                    event.sender,
                    MessageChain.create(
                        "前辈不要心急哦~心急的孩子可是要被做成玩具的哦~（当前功能正处于冷却哦~）"
                    ),
                    quote=event.messageChain.getFirst(Source).id,
                )

        sent_alert.append(eid)
    raise ExecutionStop()


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage,GroupMessage],
        inline_dispatchers=[
            Twilight({
                "head": RegexMatch(key_word)
            })
        ],
        decorators=[
            Permission.require(),
            Permission.restricter(func),
            Rest.rest_control()
        ],
     ))
async def main(head: RegexMatch, event: MessageEvent,Source_msg:Source):
    await cd_check(event)
    order=head.result.asDisplay()
    source=event.sender
    result=await get_reply(order=order,qq=source.id)
    if not result :
        return
    for reply in result[1]:
        await autoSendMessage(source,MessageChain.create(reply),quote=Source_msg)
    return
