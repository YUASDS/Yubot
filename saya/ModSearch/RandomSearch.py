import asyncio
import aiohttp

async def RandomSearch():
    # 获取数据
    ero_url = "https://www.dicecho.com/api/mod/random?pageSize=12&sort%5BlastRateAt%5D=-1&tagsMode=all"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json(content_type='json',encoding="utf-8-sig")
        res=await getRandomRes(ret)
        return res
    
async def RandomLoveSearch():
    ero_url="https://www.dicecho.com/api/mod/random?pageSize=12&sort%5BlastRateAt%5D=-1&filter%5BmoduleRule%5D=%E5%85%8B%E8%8B%8F%E9%B2%81%E7%9A%84%E5%91%BC%E5%94%A4&tags%5B0%5D=%E8%B4%B4%E8%B4%B4&tagsMode=in"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json(content_type='json',encoding="utf-8-sig")
        res=await getRandomRes(ret)
        return res

        

async def getRandomRes(ret):
        modDes=[]
        data=ret["data"]
        originTitle=data["originTitle"]
        title=data["title"]
        modDes.append("\n你抽到的随机模组是————")
        if originTitle!=title:
            modDes.append(f"\n原模组名: {originTitle}")
            modDes.append(f"\n模组名: {title}")
        else:
            modDes.append(f"\n模组名: {title}")    
        moduleRule=data["moduleRule"]
        modDes.append(f"\n规则: {moduleRule}")
        description=data["description"]
        modDes.append(f"\n简介: {description}")
        originUrl=data["originUrl"]
        modDes.append(f"\n网站: {originUrl}")
        print(modDes)
        return modDes
if __name__=="__main__":      
    loop = asyncio.get_event_loop()
    loop.run_until_complete(RandomSearch())




