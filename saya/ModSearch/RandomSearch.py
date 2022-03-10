import asyncio
import aiohttp


async def RandomSearch():
    # 获取数据
    api = "https://www.dicecho.com/api/mod/random?"
    PageSet = "pageSize=12&sort%5BlastRateAt%5D=-1&tagsMode=all"
    dicecho_url = api + PageSet
    async with aiohttp.ClientSession() as session:
        async with session.get(dicecho_url) as r:
            ret = await r.json(content_type='json', encoding="utf-8-sig")
        return getRandomRes(ret)


async def RandomLoveSearch(tag="贴贴"):
    api = "https://www.dicecho.com/api/mod/random?"
    page = "pageSize=12&sort%5BlastRateAt%5D=-1"
    rule = "&filter%5BmoduleRule%5D=克苏鲁的呼唤"
    tags = f"&tags%5B0%5D={tag}&tagsMode=in"
    dicecho_url = api + page + rule + tags
    async with aiohttp.ClientSession() as session:
        async with session.get(dicecho_url) as r:
            ret = await r.json(content_type='json', encoding="utf-8-sig")
        return getRandomRes(ret)


def getRandomRes(ret):
    data = ret["data"]
    originTitle = data["originTitle"]
    title = data["title"]
    modDes = ["\n你抽到的随机模组是————"]
    if originTitle != title:
        modDes.append(f"\n原模组名: {originTitle}")
    modDes.append(f"\n模组名: {title}")
    moduleRule = data["moduleRule"]
    modDes.append(f"\n规则: {moduleRule}")
    description = data["description"]
    modDes.append(f"\n简介: {description}")
    originUrl = data["originUrl"]
    modDes.append(f"\n网站: {originUrl}")
    return modDes


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(RandomSearch())
