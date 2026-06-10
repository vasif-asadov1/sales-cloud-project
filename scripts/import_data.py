#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import boto3
import kagglehub

# 1. Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_and_upload_to_s3(dataset_name: str, target_dir: str, bucket_name: str):
    """
    Uses the modern kagglehub library to download the dataset,
    moves it to the local raw folder, and pushes it to AWS S3.
    """
    try:
        os.makedirs(target_dir, exist_ok=True)
        logging.info(f"Downloading dataset '{dataset_name}' using kagglehub...")
        
        # 2. Download using kagglehub (uses your ~/.kaggle/access_token)
        cache_path = kagglehub.dataset_download(dataset_name)
        logging.info(f"Dataset downloaded to cache: {cache_path}")
        
        # 3. AWS S3 Client setup
        s3_client = boto3.client('s3')
        logging.info(f"Connecting to AWS S3 bucket: '{bucket_name}'...")
        
        upload_count = 0
        
        # 4. Copy to data/raw AND upload to S3 Lakehouse
        for item in os.listdir(cache_path):
            if item.endswith(".csv"):
                source_item = os.path.join(cache_path, item)
                target_item = os.path.join(target_dir, item)
                
                # Move to local project folder
                shutil.copy2(source_item, target_item)
                
                # Upload to S3
                logging.info(f"Uploading {item} to S3...")
                s3_client.upload_file(target_item, bucket_name, item)
                upload_count += 1
                
        logging.info(f"🚀 Success: {upload_count} files securely staged locally and uploaded to your S3 lakehouse!")

    except Exception as e:
        logging.error(f"❌ An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    DATASET = "olistbr/brazilian-ecommerce"
    TARGET_DIR = "data/raw" 
    BUCKET = "olist-dataset-vasifasadov"  
    
    download_and_upload_to_s3(dataset_name=DATASET, target_dir=TARGET_DIR, bucket_name=BUCKET)