import asyncio
import aiohttp


async def RandomSearch():
    # 获取数据
    api = "https://www.dicecho.com/api/mod/random?"
    PageSet = "pageSize=12&sort%5BlastRateAt%5D=-1&tagsMode=all"
    dicecho_url = api + PageSet
    async with aiohttp.ClientSession() as session:
        async with session.get(dicecho_url) as r:
            ret = await r.json(content_type="json", encoding="utf-8-sig")
        return getRandomRes(ret)


async def random_tag_search(tag="贴贴", times=1):
    api = "https://www.dicecho.com/api/mod/random?"
    page = "pageSize=12&sort%5BlastRateAt%5D=-1"
    rule = "&filter%5BmoduleRule%5D=克苏鲁的呼唤"
    tags = f"&tags%5B0%5D={tag}&tagsMode=in"
    dicecho_url = api + page + rule + tags
    res_list = []
    async with aiohttp.ClientSession() as session:
        for _ in range(times):
            async with session.get(dicecho_url) as r:
                ret = await r.json(content_type="json", encoding="utf-8-sig")
            res_get = getRandomRes(ret)
            if not res_get:
                res_list.append("此筛选条件下没有找到模组")
                break
            # if res_get in res_list:
            #     continue
            res_list.append(res_get)
    return res_list


def getRandomRes(ret: dict):

    data = ret.get("data")
    if not data:
        return False
    originTitle = data["originTitle"]
    title = data["title"]
    mod_random: list[str] = []
    if originTitle != title:
        mod_random.append(f"原模组名: {originTitle}\n")
    description = data["description"]
    moduleRule = data["moduleRule"]
    if data["modFiles"]:
        url_res = ""
        for i in data["modFiles"]:
            name = i["name"]
            url = i["url"]
            url_res += f"\n{name}：{url}"
    else:
        url_res = data["originUrl"]
    mod_random.append(
        f"模组名: {title}\n规则: {moduleRule}\n简介: {description}\n网站: {url_res}",
    )
    return "".join(mod_random)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(random_tag_search("sa6d", times=3))
