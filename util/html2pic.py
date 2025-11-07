from util.browser import get_browser
import asyncio
from io import BytesIO
from playwright._impl._api_structures import ViewportSize


async def html_to_pic(
    html: str,
    viewport: ViewportSize = None,
    selector: str = "",
    wait: float = 0.5,
    js_path: str = "",
    css_path: str = "",
    offset: dict = None,
):
    browser = await get_browser()
    page = await browser.new_page()
    await page.set_content(html)
    if js_path:
        await page.add_script_tag(path=js_path)
    if css_path:
        await page.add_style_tag(path=css_path)
    if viewport:
        await page.set_viewport_size(viewport)
    if selector:
        element = await page.query_selector(selector)
        await page.wait_for_selector(selector)
        assert element is not None
        height = await element.evaluate("el => el.offsetHeight")
        width = await element.evaluate("el => el.offsetWidth")
        if offset:
            height += offset.get("height", 0)
            width += offset.get("width", 0)
        await page.set_viewport_size({"width": width, "height": height})
    await asyncio.sleep(wait)
    img = await page.screenshot()
    await page.close()
    return BytesIO(img)
