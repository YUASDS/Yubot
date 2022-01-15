import os
import asyncio
from unittest import async_case

async def opens (contain):# a test for read and write
    with open ("new.txt",mode="a",encoding="utf-8") as new:
        new.write(contain)
    with open ("new.txt",mode="r",encoding="utf-8") as new2:
        read=new2.read()
    return read
        