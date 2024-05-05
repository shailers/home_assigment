import json
import os
import collections
from redis.cluster import RedisCluster as Redis
from redis.cluster import ClusterNode


def sort_key(user_id):
    parts = user_id.split('_')
    return int(parts[1])


def lambda_handler(event, context):
    startup_nodes = [ClusterNode(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))]
    redis_client = Redis(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=True)

    user_data = {}
    for key in sorted(redis_client.scan_iter(match='user_*', count=100), key=sort_key):
        user_details = redis_client.hgetall(key)
        user_data[key] = user_details

    global_total_playtime = redis_client.get("global_user_total_playtime")
    global_total_playtime = int(global_total_playtime) if global_total_playtime else 0

    sorted_user_data = collections.OrderedDict(sorted(user_data.items()))
    sorted_user_data['total_playtime'] = global_total_playtime

    print(sorted_user_data)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(sorted_user_data)
    }
