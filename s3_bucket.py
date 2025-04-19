import boto3
import streamlit as st
from botocore.exceptions import NoCredentialsError

# == CONFIG ==
BUCKET_NAME = "my-streamlit-s3-demo-bucket-1234"
REGION = "ap-south-1"
SNS_TOPIC_NAME = "S3UploadAlert"
EMAIL_TO_SUBSCRIBE = "kodavatigeetanjali@gmail.com"

# == AWS CLIENT ==
s3 = boto3.client("s3", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)


# == CREATE BUCKET IF NEEDED ==
def create_bucket(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
    except:
        s3.create_bucket(
            Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": REGION}
        )


# == SNS SETUP + NOTIFICATION ==
def send_sns_notification(file_key):
    topic = sns.create_topic(Name=SNS_TOPIC_NAME)
    topic_arn = topic["TopicArn"]
    try:
        sns.subscribe(TopicArn=topic_arn, Protocol="email", Endpoint=EMAIL_TO_SUBSCRIBE)
    except:
        pass  # Already Subscribed

    sns.publish(
        TopicArn=topic_arn,
        Subject="S3 Upload Notification",
        Message=f"File '{file_key}' was uploaded to bucket '{BUCKET_NAME}'.",
    )


# == STREAMLIT UI ==
st.set_page_config(page_title="S3 Upload/Download", layout="centered")
st.title("AWS S3 UPLOADED/DOWNLOADER")

create_bucket(BUCKET_NAME)

# == UPLOAD FILE ==
st.subheader("Upload Fils to S3")
uploaded_file = st.file_uploader("Choos a file to upload")

send_mail = st.checkbox("Send SNS Email Notification")

if uploaded_file and st.button("Upload"):
    try:
        s3.upload_fileobj(uploaded_file, BUCKET_NAME, uploaded_file.name)
        st.success(f"Uploaded '{uploaded_file.name}' to S3 Bucket")
        if send_mail:
            send_sns_notification(uploaded_file.name)
            st.info("SNS Email Alert Sent")
    except NoCredentialsError:
        st.error("AWS  credential not found")

# == DOWNLOAD FILE ==
st.subheader("Download File from S3")
file_key = st.text_input("Enter the filename (key) in S3")

if st.button("Download"):
    try:
        with open(file_key, "wb") as f:
            s3.download_fileobj(BUCKET_NAME, file_key, f)
        st.success(f"Download '{file_key}' to the current directory")
        with open(file_key, "rb") as file:
            st.download_button("Click to downlaod", data=file, file_name=file_key)
    except Exception as e:
        st.error(f"Error : {e}")
