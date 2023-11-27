import aioboto3

from user_management.config import config

session = aioboto3.Session()


async def get_aws_ses_client():
    async with session.client(
        "ses",
        endpoint_url=config.LOCALSTACK_HOST,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_REGION_NAME,
    ) as ses:
        yield ses


async def get_aws_s3_client():
    async with session.client(
        "s3",
        endpoint_url=f"{config.LOCALSTACK_HOST}:{config.LOCALSTACK_PORT}",
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    ) as s3:
        yield s3
