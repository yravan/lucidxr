from typing import List

import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from tqdm import tqdm


def upload_to_s3(file_path: str, bucket_name: str, s3_key: str) -> str:
    """
    Upload a single file to an S3 bucket and make it public.

    :param file_path: Local file path to upload
    :param bucket_name: Name of the S3 bucket
    :param s3_key: S3 object key (including optional folder paths)
    :return: URL of the uploaded file
    """
    # Initialize S3 client
    s3_client = boto3.client("s3")

    try:
        # Check if the file already exists in the S3 bucket
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            print(f"Warning: Overwriting existing file at '{s3_key}'.")
        except ClientError:
            pass  # File does not exist, proceed to upload

        # Upload the file to the S3 bucket
        s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=s3_key,
            ExtraArgs={"ACL": "public-read"},  # Make the file publicly accessible
        )

        # Construct and return the public URL of the file
        file_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        return file_url

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except NoCredentialsError:
        print("Error: No AWS credentials found.")
    except PartialCredentialsError:
        print("Error: AWS credentials are incomplete.")
    except Exception as e:
        print(f"An error occurred while uploading '{file_path}': {e}")

    return None


def upload_files_to_s3(file_list: List[str], bucket_name: str, s3_folder: str = None) -> List[str]:
    """
    Upload a list of files to an S3 bucket and make them public.

    :param file_list: List of file paths to upload
    :param bucket_name: Name of the S3 bucket
    :param s3_folder: (Optional) Folder path in the S3 bucket where files should be uploaded
    :return: List of URLs of the uploaded files
    """
    uploaded_files_urls = []

    it = tqdm(file_list, desc="Uploading files", unit="file")

    for file_path in it:
        # Generate S3 object key (including optional folder paths)
        s3_key = f"{s3_folder}/{file_path}" if s3_folder else file_path

        # Use upload_to_s3 to upload each file and get its URL
        uploaded_url = upload_to_s3(file_path, bucket_name, s3_key)
        it.write(f"File '{file_path}' uploaded successfully to {uploaded_url}.")
        if uploaded_url:
            uploaded_files_urls.append(uploaded_url)

    return uploaded_files_urls


if __name__ == "__main__":
    from glob import glob

    # Example usage:
    file_list = glob("./*.*")  # Replace with your files
    bucket_name = "vuer-hub-production"  # Replace with your bucket name
    s3_folder = "assets/lucid-xr"  # Optional: S3 folder name

    # Upload files to S3
    uploaded_urls = upload_files_to_s3(file_list, bucket_name, s3_folder)

    print("\nUploaded Files URLs:")
    for url in uploaded_urls:
        print(url, end="\r")
