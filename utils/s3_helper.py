import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional

from config.secrets import get_secrets


class S3Helper:
    def __init__(self):
        aws_secrets = get_secrets("aws")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_secrets["access_key_id_s3"],
            aws_secret_access_key=aws_secrets["secret_access_key_s3"],
            region_name=aws_secrets["region"],
        )
        self.bucket_name = aws_secrets["s3_bucket"]

    def upload_file(self, file_data: bytes, file_name: str) -> Optional[str]:
        """Upload file to S3 and return public URL"""
        try:
            # Generate S3 key
            s3_key = f"logos/{file_name}"

            # Upload file
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType="image/png",  # Adjust based on file type
                ACL="public-read",
            )

            # Generate public URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            return url

        except ClientError as e:
            print(f"Error uploading to S3: {str(e)}")
            return None
