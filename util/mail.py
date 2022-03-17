from alibabacloud_dm20151123.client import Client as Dm20151123Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dm20151123 import models as dm_20151123_models

from config import yaml_data

accessKeyId = yaml_data["Basic"]["API"]["AliYuncs"]["accessKeyId"]
accessKeySecret = yaml_data["Basic"]["API"]["AliYuncs"]["accessKeySecret"]


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dm20151123Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret,
        )
        # 访问的域名
        config.endpoint = "dm.aliyuncs.com"
        return Dm20151123Client(config)

    @staticmethod
    async def main_async(
        to_address: str, subject: str, html_body: str = None, text_body: str = ""
    ) -> None:
        client = Sample.create_client(accessKeyId, accessKeySecret)
        single_send_mail_request = dm_20151123_models.SingleSendMailRequest(
            account_name="yu@yucoc.xyz",
            address_type=0,
            reply_to_address=True,
            to_address=to_address,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )
        # 复制代码运行请自行打印 API 的返回值
        return await client.single_send_mail_async(single_send_mail_request)
