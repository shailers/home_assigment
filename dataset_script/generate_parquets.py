import random
import numpy as np
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

NUM_BATCHES = 3


def upload_to_s3(file_path, bucket):
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket, file_path)
        print(f" {file_path} File uploaded to bucket {bucket} successfully.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Credentials issue: {e}")
    except Exception as e:
        print(f"Failed to upload file: {e}")


for batch_num in range(NUM_BATCHES):
    event_types = ['roadside', 'battle', 'menu']
    user_ids = [f'user_{i}' for i in range(1, 11)]
    data = [(random.choice(user_ids), random.choice(event_types)) for _ in range(100000)]

    df = pd.DataFrame(data, columns=['UserID', 'EventType'])
    df['EventDuration'] = np.random.randint(1, 11, size=len(df))
    total_event_time_seconds = df['EventDuration'].sum()

    print("Total Event Time Seconds:", total_event_time_seconds)
    batch_id = f'a_{batch_num}'
    file_path = f"ht_events_{batch_id}.parquet"
    df.to_parquet(file_path)

    bucket_name = 'quago-python-home-task-bucket'

    upload_to_s3(file_path, bucket_name)
