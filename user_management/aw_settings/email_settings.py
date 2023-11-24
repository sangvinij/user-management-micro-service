# # import asyncio
# # from typing import Annotated
# #
# import aioboto3
#
# # import aiobotocore
# # from fastapi import Depends
# #
# # # ses = boto3.client(
# # #     "ses",
# # #     endpoint_url="http://localhost:4566",
# # #     region_name="eu-central-1",
# # #     aws_access_key_id="aws_access_key_id",
# # #     aws_secret_access_key="aws_secret_access_key",
# # # )
# #
# #
# # # rs2 = ses.send_email(
# # #     Destination={"ToAddresses": ["artyom.vorozhbyanov@gmail.com"]},
# # #     Source="jamestaylor25565@gmail.com",
# # #     Message={
# # #         "Body": {
# # #             "Text": {
# # #                 "Charset": "UTF-8",
# # #                 "Data": "This is the message body.",
# # #             }
# # #         },
# # #         "Subject": {
# # #             "Charset": "UTF-8",
# # #             "Data": "Test email",
# # #         },
# # #     },
# # # )
# # #
# # # s3 = boto3.resource(
# # #     "s3",
# # #     endpoint_url="http://localhost:4566",
# # #     aws_access_key_id="aws_access_key_id",
# # #     aws_secret_access_key="aws_secret_access_key",
# # # )
# # #
# # #
# # # bucket_name = "my-test-bucket"
# # # image_path = "path_to_your_image.jpg"
# # # s3.create_bucket(Bucket=bucket_name)
# # #
# # # with open("__init__.py", "rb") as image_file:
# # #     rs = s3.Bucket(bucket_name).put_object(Key="kartinka2.jpg", Body=image_file)
# # #     print(rs)
# # #     print(rs.bucket_name)
# # #
# # # print(s3.buckets.all())
# # # for bucket in s3.buckets.all():
# # #     print(bucket)
# #
#
# session = aioboto3.Session()
#
#
# async def get_aws_ses_client():
#     async with session.client(
#         "ses",
#         endpoint_url="http://localhost:4566",
#         aws_access_key_id="aws_access_key_id",
#         aws_secret_access_key="aws_secret_access_key",
#         region_name="eu-central-1",
#     ) as ses:
#         yield ses
#
#
# #
# #
# async def upload(s3: aioboto3.Session.client):
#   bucket = await s3.create_bucket(Bucket="bucket")
#   with open("kartinka.jpg") as file:
#        rs = await s3.upload_file(file, bucket, "kartinka")
#      print(rs)
# # #
# #
# # async def send_email():
# #     ses = await get_aws_ses_client().__anext__()
# #     rs2 = await ses.verify_email_identity(EmailAddress="jamestaylor25565@gmail.com")
# # #
# # #     rs = await ses.send_email(
# # #         Destination={"ToAddresses": ["artyom.vorozhbyanov@gmail.com"]},
# # #         Source="jamestaylor25565@gmail.com",
# # #         Message={
# # #             "Body": {
# # #                 "Text": {
# # #                     "Charset": "UTF-8",
# # #                     "Data": "This is the message body.",
# # #                 }
# # #             },
# # #             "Subject": {
# # #                 "Charset": "UTF-8",
# # #                 "Data": "Test email",
# # #             },
# # #         },
# # #     )
# #
# #
# #
# # # async def get_aws_s3_client():
# # #     session = aioboto3.Session()
# # #     async with session.resource("s3") as s3:
# # #         yield s3
