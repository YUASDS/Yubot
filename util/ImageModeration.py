import json
import base64
import asyncio
from typing import Union
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import (
    TencentCloudSDKException,
)
from tencentcloud.ims.v20201229 import ims_client, models

from config import yaml_data


def image_moderation(img):
    try:
        cred = credential.Credential(
            yaml_data["Basic"]["API"]["Tencent"]["secretId"],
            yaml_data["Basic"]["API"]["Tencent"]["secretKey"],
        )
        httpProfile = HttpProfile()
        httpProfile.endpoint = "ims.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = ims_client.ImsClient(cred, "ap-shanghai", clientProfile)

        req = models.ImageModerationRequest()
        params = (
            {"BizType": "group_recall", "FileUrl": img}
            if type(img) == str
            else {"BizType": "group_recall", "FileContent": bytes_to_base64(img)}
        )
        req.from_json_string(json.dumps(params))

        resp = client.ImageModeration(req)
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        return err


async def image_moderation_async(img: Union[str, bytes]) -> dict:
    try:
        resp = await asyncio.to_thread(image_moderation, img)
        if resp["Suggestion"] != "Pass":
            return {"status": False, "message": resp["Label"]}
        else:
            return {"status": True, "message": None}
    except Exception as e:
        return {"status": "error", "message": e}


def bytes_to_base64(data):
    return base64.b64encode(data).decode("utf-8")
