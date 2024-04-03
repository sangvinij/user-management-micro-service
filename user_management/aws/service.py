import contextlib
from typing import List

import aioboto3
import botocore.errorfactory
from fastapi import UploadFile
from pydantic import EmailStr

from user_management.config import config


class AWSService:
    def __init__(self, aws_client: aioboto3.Session.client):
        self.aws_client: aioboto3.Session.client = aws_client

    async def send_mail(self, message_text: str, subject_text: str, addresses: List[EmailStr]):
        await self.aws_client.verify_email_identity(EmailAddress=config.SOURCE_EMAIL)

        rs = await self.aws_client.send_email(
            Destination={"ToAddresses": addresses},
            Source=config.SOURCE_EMAIL,
            Message={
                "Body": {
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": message_text,
                    }
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject_text,
                },
            },
        )

        return rs

    async def upload_image(self, file: UploadFile, key: str) -> str:
        with contextlib.suppress(botocore.errorfactory.ClientError):
            await self.aws_client.create_bucket(
                Bucket=config.AWS_S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": config.AWS_REGION_NAME},
            )

        await self.aws_client.upload_fileobj(file, config.AWS_S3_BUCKET_NAME, key)

        image_s3_path: str = f"{config.LOCALSTACK_HOST}:{config.LOCALSTACK_PORT}/{config.AWS_S3_BUCKET_NAME}/{key}"

        return image_s3_path
