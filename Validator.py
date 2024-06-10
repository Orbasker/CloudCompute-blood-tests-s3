import os
import shutil
import time
import json
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(
    filename="/home/nour/Desktop/validator/validator.log",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
)

# AWS S3 configuration
VALID_BUCKET = "a2g11-valid"
INVALID_BUCKET = "a2g11-invalid"
AWS_REGION = "il-central-1"

# Directories
SOURCE_DIR = "/home/nour/Desktop/bloodtests"
TEMP_DIR = "/home/nour/Desktop/temp"

# Initialize S3 client using default AWS CLI credentials and region
s3_client = boto3.client("s3", region_name=AWS_REGION)

# Gmail API configuration
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
SENDER_EMAIL = "orbasker@gmail.com"
RECEIVER_EMAIL = "nj.mawasi@hotmail.com"


def get_credentials():
    creds = None
    creds_path = "/home/nour/Desktop/validator/credentials.json"
    token_path = "/home/nour/Desktop/validator/token.json"
    try:
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
    except Exception as e:
        logging.error(f"Error getting credentials: {e}")
    return creds


def create_message(sender, to, subject, message_text):
    try:
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = sender
        message["subject"] = subject

        msg = MIMEText(message_text)
        message.attach(msg)

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        return {"raw": raw}
    except Exception as e:
        logging.error(f"Error creating message: {e}")


def send_message(service, user_id, message):
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message).execute()
        )
        logging.info(f'Message Id: {message["id"]}')
        return message
    except HttpError as error:
        logging.error(f"An error occurred: {error}")
        return None


def is_file_complete(file_path):
    try:
        initial_size = os.path.getsize(file_path)
        time.sleep(5)
        final_size = os.path.getsize(file_path)
        return initial_size == final_size
    except Exception as e:
        logging.error(f"Error checking if file is complete: {e}")


def validate_file(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            required_fields = ["patient_id", "sample_id", "result"]
            if all(key in data and data[key] for key in required_fields):
                return True, ""
            missing_fields = [
                key for key in required_fields if key not in data or not data[key]
            ]
            return False, f"Missing or empty fields: {', '.join(missing_fields)}"
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {file_path}")
        return False, "Invalid JSON format"
    except Exception as e:
        logging.error(f"Error validating file: {e}")


def upload_to_s3(file_path, bucket_name):
    try:
        s3_client.upload_file(file_path, bucket_name, os.path.basename(file_path))
        logging.info(f"Uploaded {file_path} to {bucket_name}")
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Credentials error: {e}")
    except Exception as e:
        logging.error(f"Error uploading {file_path} to S3: {e}")


def notify_invalid_sample(file_path, reason):
    try:
        creds = get_credentials()
        if creds:
            service = build("gmail", "v1", credentials=creds)
            subject = "Invalid Sample Detected"
            message_text = (
                f"The file {file_path} is invalid due to the following reason: {reason}"
            )
            message = create_message(
                SENDER_EMAIL, RECEIVER_EMAIL, subject, message_text
            )
            send_message(service, "me", message)
    except Exception as e:
        logging.error(f"Error notifying invalid sample: {e}")


def move_files():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    for filename in os.listdir(SOURCE_DIR):
        source_path = os.path.join(SOURCE_DIR, filename)
        temp_path = os.path.join(TEMP_DIR, filename)

        if os.path.isfile(source_path) and is_file_complete(source_path):
            try:
                shutil.move(source_path, temp_path)
                logging.info(f"Moved: {source_path} to {temp_path}")

                is_valid, reason = validate_file(temp_path)
                if is_valid:
                    upload_to_s3(temp_path, VALID_BUCKET)
                else:
                    upload_to_s3(temp_path, INVALID_BUCKET)
                    notify_invalid_sample(temp_path, reason)
                os.remove(temp_path)
                logging.info(f"Deleted {temp_path}")
            except Exception as e:
                logging.error(f"Error moving or deleting file: {e}")


if __name__ == "__main__":
    move_files()
