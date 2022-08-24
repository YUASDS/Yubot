import asyncio
import aiohttp


async def dicecho_search(mod):
    # 获取数据
    url = f"https://www.dicecho.com/api/mod/?keyword={mod}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            ret = await r.json(content_type="json", encoding="utf-8-sig")
        res = getRes(ret)
    return res


def getRes(ret):
    total_des = []
    num = ret["data"]["totalCount"]
    if num < 1:
        return False
    num = min(num, 10)
    for i in range(num):
        modDes = []
        data = ret["data"]["data"][i]
        originTitle = data["originTitle"]
        title = data["title"]
        if originTitle != title:
            modDes.append((f"原模组名: {originTitle}", f"\n模组名: {title}"))
        else:
            modDes.append(f"模组名: {title}")
        moduleRule = data["moduleRule"]
        if data["modFiles"]:
            url_res = ""
            for i in data["modFiles"]:
                name = i["name"]
                url = i["url"]
                url_res += f"\n{name}：{url}"
        else:
            url_res = data["originUrl"]
        description = data["description"]
        modDes.extend(
            (f"\n规则: {moduleRule}", f"\n简介: {description}", f"\n网站: {url_res}")
        )
        total_des.append(modDes)
    return total_des


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(dicecho("奇迹"))

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
