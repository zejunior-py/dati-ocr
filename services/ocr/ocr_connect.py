import logging
import boto3
from settings import AWS_BUCKET
from botocore.exceptions import ClientError


class ConnectOcr:
    def __init__(self):
        self.client = boto3.client('textract')
        self.status = "IN_PROGRESS"
        self.response_status = None
        self.doc_name = None

    def ocr_object(self):
        response = self.client.start_document_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': AWS_BUCKET,
                    'Name': self.doc_name
                }
            },
            FeatureTypes=['TABLES']
        )
        while self.status == "IN_PROGRESS":
            self.response_status = self.client.get_document_analysis(JobId=response["JobId"])
            self.status = self.response_status["JobStatus"]
        return self.response_status

    def upload_file(self, file):
        self.doc_name = file.filename
        s3_client = boto3.client('s3')
        try:
            s3_client.put_object(Bucket=AWS_BUCKET, Key=file.filename, Body=file.read())
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def delete_object_s3(self):
        s3 = boto3.resource('s3')
        s3.Object(AWS_BUCKET, self.doc_name).delete()
