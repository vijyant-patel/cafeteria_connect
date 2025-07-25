import redis

redis_client = redis.StrictRedis(
    host='cafeteria_connect-redis-1',
    port=6379,
    db=0
)
