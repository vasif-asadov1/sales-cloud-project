#!/usr/bin/env python3
import os
import sys
import boto3
from botocore.exceptions import ClientError

def create_s3_bucket(bucket_name: str, region: str = None) -> bool:
    """
    Creates an S3 bucket in a specified region.
    If a region is not specified, the bucket is created in the S3 default region (us-east-1).
    """
    try:
        if region is None or region == "us-east-1":
            s3_client = boto3.client('s3')
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = boto3.client('s3', region_name=region)
            location = {'LocationConstraint': region}
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
        print(f"Success: Bucket '{bucket_name}' created successfully!")
        return True
    except ClientError as e:
        print(f"Error creating bucket: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    # Define bucket name exactly as specified
    BUCKET_NAME = "olist-dataset-vasifasadov"  # Note: S3 bucket names must be globally unique across all AWS accounts
    
    # Retrieve default region from environment or fallback to us-east-1
    aws_region = boto3.session.Session().region_name or "eu-central-1"
    
    print(f"Targeting AWS Region: {aws_region}")
    create_s3_bucket(BUCKET_NAME, region=aws_region)