import json
import os
from io import BytesIO

import pandas as pd
import pyarrow.parquet as pq
import boto3

from logger import logger
from redis_db import input_data_to_redis

def extract_event_data(record):
    event_data = dict()

    logger.info(f"extracting data from event record: {record}")
    message_body = json.loads(record['body'])

    s3_data = message_body['Records'][0]['s3']

    event_data['bucket_name'] = s3_data["bucket"]["name"]
    event_data['object_key'] = s3_data["object"]["key"]
    event_data['object_etag'] = s3_data["object"]["eTag"]

    return event_data


def lambda_handler(event, context):
    logger.debug(f"got event: {event}")

    try:
        s3_client = boto3.client('s3')
        for i, record in enumerate(event['Records']):

            event_data = extract_event_data(record)

            logger.debug(f"event_data {i}: {event_data}")

            response = s3_client.get_object(Bucket=event_data['bucket_name'], Key=event_data['object_key'])
            content = response['Body'].read()

            file_stream = BytesIO(content)
            parquet_file = pq.ParquetFile(file_stream)

            total_aggregation = pd.DataFrame()
            batch_size = os.environ.get('BATCH_SIZE')

            for batch in parquet_file.iter_batches(batch_size=batch_size):
                df = batch.to_pandas()
                pivot_table = df.pivot_table(index='UserID', columns='EventType', values='EventDuration',
                                             aggfunc='sum').astype(int)
                total_aggregation = total_aggregation.add(pivot_table, fill_value=0).astype(int)

            total_aggregation['total_playtime'] = total_aggregation.sum(axis=1).astype(int)
            grand_total = total_aggregation['total_playtime'].sum()
            formatted_data = total_aggregation.to_dict(orient='index')
            formatted_data['total_playtime'] = grand_total

            logger.debug(f"formatted_data: {formatted_data}")

            input_data_to_redis(formatted_data, etag=event_data['object_etag'])
    except Exception as e:
        logger.error(f"dataset_aggregator lambda failed: {e}")
