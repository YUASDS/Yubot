from io import BytesIO

import aiohttp


bg = "https://s2.loli.net/2022/03/15/ZPBOy4UoihuNAxL.jpg"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Referer": "http://www.baidu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.39",
}


async def get(url: str, type: str = "JSON", headers=headers, encoding="utf-8"):

    async with aiohttp.ClientSession() as session:
        resp = await session.get(url=url, headers=headers)
        if type in {"JSON", "json"}:
            return await resp.json(encoding=encoding)
        if type in {"img", "IMG"}:
            return await BytesIO(resp.content).getvalue()
        return await resp.text(encoding=encoding)


async def post(url, data, type="json", headers=headers, encoding="utf-8") -> dict:
    """ """
    async with aiohttp.ClientSession() as session:
        resp = await session.post(url=url, data=data, headers=headers)
        if type in {"JSON", "json"}:
            return await resp.json(encoding=encoding, content_type="text/html")
        if type in {"img", "IMG"}:
            return await BytesIO(resp.content).getvalue()
        return await resp.text(encoding=encoding)
