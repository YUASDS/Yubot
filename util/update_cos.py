import asyncio

from config import yaml_data
from qcloud_cos import CosConfig, CosS3Client


secret_id = yaml_data["Basic"]["API"]["Tencent"]["secretId"]
secret_key = yaml_data["Basic"]["API"]["Tencent"]["secretKey"]
region = yaml_data["Basic"]["API"]["Tencent"]["Cos"]["region"]
bucket = yaml_data["Basic"]["API"]["Tencent"]["Cos"]["bucket"]

cos_config = CosConfig(
    Region=region,
    SecretId=secret_id,
    SecretKey=secret_key,
)
client = CosS3Client(cos_config)


class UpdateCos:
    def __init__(self, fb: bytes, key: str):
        self.fb = fb
        self.key = key

    async def update(self):
        return await asyncio.to_thread(
            client.put_object,
            Bucket=bucket,
            Body=self.fb,
            Key=self.key,
            StorageClass="STANDARD",
            Metadata={"x-cos-meta-type": "waifu2x"},
        )

    async def get_url(self, expired: int = 600) -> str:
        return await asyncio.to_thread(
            client.get_presigned_download_url,
            Bucket=bucket,
            Key=self.key,
            Expired=expired,
        )
