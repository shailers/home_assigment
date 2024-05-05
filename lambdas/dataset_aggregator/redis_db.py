from redis.cluster import RedisCluster as Redis
import os
import json
import numpy as np
from lambdas.dataset_aggregator.logger import logger

def connect_and_get_redis_client():
    return Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'))


class NumpyEncoder(json.JSONEncoder):
    """ Custom encoder for numpy data types """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


def input_data_to_redis(user_aggregations, etag):
    redis_client = connect_and_get_redis_client()
    redis_unique_key = f"etag:{etag}"

    lua_script = """
    if redis.call('get', KEYS[1]) then
        return 0  -- ETag exists, skip processing
    else
        redis.call('set', KEYS[1], 'processed')  -- Mark this ETag as processed
        for i = 2, #ARGV-2, 2 do
            local user_key = ARGV[i]
            local data_json = ARGV[i+1]
            if data_json then
                local data = cjson.decode(data_json)
                if type(data) == 'table' then  -- Ensure the decoded data is a table
                    for event_type, additional_time in pairs(data) do
                        redis.call('hincrby', user_key, event_type, additional_time)
                    end
                else
                    return redis.error_reply('Data type mismatch: expected table, got ' .. type(data))
                end
            end
        end
        -- Convert the last argument to number for incrementing global playtime
        redis.call('incrby', 'global_user_total_playtime', tonumber(ARGV[#ARGV]))
        return 1
    end
    """

    args = [etag]
    for user_id, events in user_aggregations.items():
        events_json = json.dumps(events, cls=NumpyEncoder)
        args.append(user_id)
        args.append(events_json)

    for idx, arg in enumerate(args):
        logger.debug(f"Arg {idx}: {arg}, Type: {type(arg)}")

    try:
        result = redis_client.eval(lua_script, 1, redis_unique_key, *args)
        if result == 0:
            logger.info(f"ETag {etag} already found in redis, data not written.")
        else:
            logger.info(f"Data with ETag {etag} successfully written to Redis.")
    except Exception as e:
        logger.error(f"Error during Redis operation: {e}")