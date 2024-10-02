# Lambda script for twa-chatbot-pinecone-backup. Scheduled with Amazon EventBridge to run once a week. Creates a backup in s3 bucket named twa-chatbot-pinecone-backups.
# Can utilize pineconeBackupUpload.py to upload one of the save files
import json
import datetime
import os
from pinecone import Pinecone
import numpy as np
import zipfile
import boto3
import io

# Initialize configuration and Pinecone
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
pc = Pinecone(api_key=PINECONE_API_KEY)

# Initialize Pinecone indices
source_index = pc.Index('twa-chatbot2')
target_index = pc.Index('twa-chatbot2-backup')

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
bucket_name = "twa-chatbot-pinecone-backups"
bucket = s3.Bucket(bucket_name)


def get_all_ids_with_metadata(index, num_dimensions):
    stats = index.describe_index_stats()
    namespace_map = stats['namespaces']

    all_ids_metadata = {}
    for namespace in namespace_map:
        num_vectors = namespace_map[namespace]['vector_count']
        all_ids_metadata[namespace] = {}
        while len(all_ids_metadata[namespace]) < num_vectors:
            input_vector = np.random.rand(num_dimensions).tolist()
            ids_metadata_embeddings = get_ids_with_metadata(index, input_vector, namespace)
            all_ids_metadata[namespace].update(ids_metadata_embeddings)
            print(f"Collected {len(all_ids_metadata[namespace])} ids out of {num_vectors} in namespace '{namespace}'.")

    return all_ids_metadata


def get_ids_with_metadata(index, input_vector, namespace):
    results = index.query(vector=input_vector, top_k=10000, namespace=namespace, include_values=True,
                          include_metadata=True)
    return {result['id']: {'metadata': result['metadata'], 'embedding': result['values']} for result in
            results['matches']}


def upsert_data(index, all_data):
    for namespace, ids_info in all_data.items():
        print(f"Processing namespace: {namespace} with {len(ids_info)} entries.")
        vectors_to_upsert = [(id, info['embedding'], info['metadata']) for id, info in ids_info.items() if
                             'embedding' in info and 'metadata' in info]
        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)
            print(f"Upserted batch {i // batch_size + 1} in namespace '{namespace}'")


def delete_oldest_object_if_necessary():
    objects = list(bucket.objects.all())

    if len(objects) >= 5:
        # Sort objects by last modified date
        objects.sort(key=lambda obj: obj.last_modified)

        # Get the oldest object
        oldest_object = objects[0]

        # Delete the oldest object
        oldest_object.delete()
        print(f"Deleted the oldest object: {oldest_object.key}")
    else:
        print("There are less than 5 objects in the bucket. No deletion performed.")


def get_current_datetime():
    # Get the current date and time
    now = datetime.datetime.now()
    # Format the date and time as 'month-day-year-hour-minute AM/PM'
    datetime_string = now.strftime("%m-%d-%Y-%I-%M-%p")
    return datetime_string


def lambda_handler(event, context):
    all_data = get_all_ids_with_metadata(source_index, 1536)

    with io.BytesIO() as file_stream:
        with zipfile.ZipFile(file_stream, 'w', zipfile.ZIP_DEFLATED) as z:
            data_str = json.dumps(all_data)  # Convert data to JSON string
            z.writestr("dbBackup.txt", data_str)
        file_stream.seek(0)  # Reset file position to the beginning after writing

        # Upload the stream content directly to S3 using the correct S3 client method
        s3_object_key = f"{get_current_datetime()}.zip"
        s3_client.upload_fileobj(
            file_stream,
            bucket_name,
            s3_object_key
        )

    delete_oldest_object_if_necessary()

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }