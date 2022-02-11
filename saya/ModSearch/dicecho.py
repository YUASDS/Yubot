import asyncio
import aiohttp


async def dicecho(mod):
    # 获取数据
    ero_url = f"https://www.dicecho.com/api/mod/?keyword={mod}"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json(content_type='json', encoding="utf-8-sig")
        res = await getRes(ret)
        return res


async def getRes(ret):
    totalDes = []
    totalCount = ret["data"]["totalCount"]
    if totalCount < 1:
        return totalDes
    else:
        if totalCount > 5:
            totalDes.append("\n搜索项大于五，仅显示前五项")
            totalCount = 5
        for i in range(totalCount):
            modDes = []
            data = ret["data"]["data"][i]
            originTitle = data["originTitle"]
            title = data["title"]
            if originTitle != title:
                modDes.append(f"\n原模组名: {originTitle}")
                modDes.append(f"\n模组名: {title}")
            else:
                modDes.append(f"\n模组名: {title}")
            moduleRule = data["moduleRule"]
            modDes.append(f"\n规则: {moduleRule}")
            description = data["description"]
            modDes.append(f"\n简介: {description}")
            originUrl = data["originUrl"]
            modDes.append(f"\n网站: {originUrl}")
            totalDes.append(modDes)
    return totalDes


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(dicecho("奇迹"))

    # file=open("tests\\dicecho.html",encoding="utf-8")
    # soup = BeautifulSoup(file,features="html.parser")
    # find=soup.find_all( class_="jet-listing-dynamic-field__content")
    # print(find)
    # for i in range(len(find)):
    # # print(i)
    # if find[i].string:
    #     print(find[i].string)
    # elif find[i].p:
    #     print (find[i].p.string)
    # elif find[i].strong.string:
    #     print(find[i].strong.string)

#

# soup = BeautifulSoup(html)
# # print (soup.head.contents[0])
