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
            else:
                if ele > 10:
                    totalDes.append("搜索项大于10，仅显示前10项")
                    ele = 10
                # totalDes.append("检索结果为————\n")
                for i in range(ele):
                    results = []
                    res = ret["data"]["list"][i]
                    title = res["title"]
                    moduleType = res["moduleType"]
                    opinion = res["opinion"]
                    url = res["url"]
                    results.append(f"模组名: {title}\n规则：{moduleType}\n")
                    results.append(f"简介：{opinion}\n下载链接：{url}\n")
                    totalDes.append(results)
            return totalDes


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(cnmods("扬镇"))
