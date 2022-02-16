import asyncio
import aiohttp


async def cnmods(mod):
    ero_url = f"https://www.cnmods.net/index/moduleListPage.do?title={mod}"
    async with aiohttp.ClientSession() as session:
        async with session.get(ero_url) as r:
            ret = await r.json(content_type='json', encoding="utf-8")

            totalDes = []
            ele = ret["data"]["totalElements"]
            if ele == 0:
                return totalDes
            elif ele > 5:
                totalDes.append("当前检索项大于5项，仅显示前5项\n")
                ele = 5
            else:
                totalDes.append("检索结果为————\n")
                for i in range(ele):
                    results = []
                    res = ret["data"]["list"][i]
                    title = res["title"]
                    moduleType = res["moduleType"]
                    opinion = res["opinion"]
                    url = res["url"]
                    results.append(f"\n模组名: {title}\n规则：{moduleType}\n")
                    results.append(f"简介：{opinion}\n下载链接：{url}\n")
                    totalDes.append(results)
            return totalDes


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cnmods("扬镇"))
