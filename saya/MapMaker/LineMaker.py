# make a map
import json
import os
import asyncio


import httpx
from io import BytesIO
from PIL import Image
import numpy as np


class line_maker():

    def __init__(self, file, cell_size=30, part=6) -> None:
        self.file = file
        self.cell_size = cell_size
        self.part = part
        self.Img = None

    async def map(self) -> bytes:
        file = self.file
        cell_size = self.cell_size
        img=Image.open(file).convert('RGBA')
        img=np.array(img)

        (w, h, _) = img.shape
        w_line = w // cell_size + 1
        h_line = h // cell_size + 1
        for i in range(w_line):
            img[i * cell_size, :, :] = 0
        for j in range(h_line):
            img[:, j * cell_size, :] = 0
            # 因为对数据修改过，所有不能直接将数组转换为bytes，需要先编码
        self.Img = img
        img = Image.fromarray(img).convert('RGBA')
        imgByteArr = BytesIO()
        img.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        return img.tostring()

    async def map_pice(self,option=False) -> bytes:
        file = self.file
        part = self.part
        if option:
            img=file
        else:
            # img = cv2.imread(file, 1)
            img=Image.open(file).convert('RGBA')
            img=np.array(img)
        (h, w, _) = img.shape
        if w > h:
            rg1 = part
            cell_size = w // part
            rg2 = h // cell_size
        else:
            rg2 = part
            cell_size = h // part
            rg1 = w // cell_size
        self.rg1 = rg1
        self.rg2 = rg2
        for i in range(rg2):
            img[i * cell_size, :, :] = 0
        for j in range(rg1):
            img[:, j * cell_size, :] = 0
        self.cell_size = cell_size
        self.Img = img
        # succ, img = cv2.imencode(".jpg", img)
        img = Image.fromarray(img).convert('RGBA')
        imgByteArr = BytesIO()
        img.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def post_char(self,
                  img: np.array,
                  x: int,
                  y: int,
                  optional=False) -> bytes:
        file = self.file
        cell_size = self.cell_size
        back = Image.fromarray(file).convert('RGBA')
        img = Image.fromarray(img).convert('RGBA')

        imgs = img.resize((cell_size, cell_size), Image.ANTIALIAS)
        r, g, b, a = imgs.split()
        # imgs.show()
        # back.show()
        y_dir = y * cell_size
        x_dir = x * cell_size
        # print(x, y, cell_size)
        # print(y_dir, x_dir)

 
        back.paste(imgs, (x_dir, y_dir), mask=a)
        self.bg_img_array = np.array(back)
        # if optional:
        #     return
        imgByteArr = BytesIO()
        back.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        return imgByteArr

    def post_array(self, pet_dict: dict, bg_array: list) -> bytes:
        i = 0
        for x in bg_array:
            j = 0
            for y in x:
                if y in pet_dict:
                    n = self.post_char(img=pet_dict[str(y)],
                                       x=j,
                                       y=i,
                                       optional=True)

                    self.file = self.bg_img_array
                j = j + 1
            i = i + 1
        # succ, img = cv2.imencode(".jpg", self.bg_img_array)
        return n


async def test():
    MAP = {}
    gid = "123"
    MAP[gid] = {}
    MAP[gid]["pet"] = {}
    MAP[gid]["array"] = np.zeros((6, 6), dtype=int, order='C')
    img = line_maker(os.path.join(os.path.dirname(__file__), 'bg.jpg'))
    pet = await get_pet(1787569211)
    im_g = Image.fromarray(pet).convert('RGBA')
    im_g.show()
    MAP[gid]["pet"]["1787569211"] = pet
    MAP[gid]["array"][0][0] = 1787569211
    MAP[gid]["array"][2][2] = 1787569211
    s = await img.map_pice()
    img.file = img.Img
    n = img.post_array(MAP[gid]["pet"], MAP[gid]["array"])


async def save_config(config: dict, path):
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(ex)
        return False


async def load_config(path):

    try:
        with open(path, 'r', encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return {}


async def get_pet(member_id: str=None,image_url=None,msgchain=False) -> np.array:
    if member_id:
        url = f"http://q1.qlogo.cn/g?b=qq&nk={member_id}&s=640"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url=url)

        avatar = Image.open(BytesIO(resp.content)).convert('RGBA')
        return np.array(avatar)
    elif msgchain:
        resp=msgchain
        image =  Image.open(BytesIO(resp)).convert('RGBA')
        return np.array(image)
    else:
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
        image =  Image.open(BytesIO(resp.content)).convert('RGBA')
        return np.array(image)



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
