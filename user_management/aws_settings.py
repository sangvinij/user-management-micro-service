from typing import List, Tuple

import aioboto3
from pydantic import EmailStr
from user_management.config import config

session = aioboto3.Session()


async def get_aws_ses_client():
    async with session.client(
            "ses",
            endpoint_url="https://localhost:4566",
            aws_access_key_id="self.aws_access_key_id",
            aws_secret_access_key="self.aws_secret_access_key",
            region_name="eu-central-1",
    ) as ses:
        yield ses


# async def get_aws_s3_client():
#     async with self.session.client(
#         "s3",
#         endpoint_url=self.endpoint_url,
#         aws_access_key_id=self.aws_access_key_id,
#         aws_secret_access_key=self.aws_secret_access_key,
#     ) as s3:
#         yield s3


class AWSSettings:
    def __init__(self, aws_client):
        self.aws_client: aioboto3.Session.client = aws_client

    async def send_mail(self, message_text: str, subject_text: str, addresses: Tuple[EmailStr]):
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
