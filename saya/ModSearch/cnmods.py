import asyncio
import aiohttp


async def cnmods_search(mod):
    url = f"https://www.cnmods.net/index/moduleListPage.do?title={mod}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            ret = await r.json(content_type="json", encoding="utf-8")
            total_des = []
            num = ret["data"]["totalElements"]
            if num == 0:
                return False
            num = min(num, 10)
            for i in range(num):
                res = ret["data"]["list"][i]
                title = res["title"]
                moduleType = res["moduleType"]
                opinion = res["opinion"]
                url = res["url"]
                results = [
                    f"模组名: {title}\n规则：{moduleType}\n",
                    f"简介：{opinion}\n下载链接：{url}\n",
                ]
                total_des.append(results)
            return total_des


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(cnmods("扬镇"))
