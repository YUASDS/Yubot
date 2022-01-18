import json
import base64
import asyncio

from tencentcloud.common import credential
from tencentcloud.tms.v20201229 import tms_client, models
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile

from config import yaml_data


def text_moderation(text: str):

    text_base64 = str(base64.b64encode(text.encode("utf-8")), "utf-8")
    cred = credential.Credential(
        yaml_data["Basic"]["API"]["Tencent"]["secretId"],
        yaml_data["Basic"]["API"]["Tencent"]["secretKey"],
    )
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tms.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tms_client.TmsClient(cred, "ap-shanghai", clientProfile)

    req = models.TextModerationRequest()
    params = {"Content": text_base64, "BizType": "group_recall_text"}
    req.from_json_string(json.dumps(params))

    resp = client.TextModeration(req)
    return json.loads(resp.to_json_string())


async def text_moderation_async(text: str) -> dict:
    try:
        resp = await asyncio.to_thread(text_moderation, text)
        if resp["Suggestion"] != "Pass":
            return {"status": False, "message": resp["Label"]}
        else:
            return {"status": True, "message": None}
    except Exception as e:
        return {"status": "error", "message": e}
