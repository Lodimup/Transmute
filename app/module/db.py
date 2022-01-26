import redis

def set_redis_json(rdb: redis.client.Redis, key: str, path: str, payload: dict) -> None:
    rdb.json().set(key, path, payload)


def get_redis_json(rdb: redis.client.Redis, key: str) -> dict:
    return rdb.json().get(key)


def set_redis_expire(rdb: redis.client.Redis, key: str, seconds: int) -> None:
    rdb.expire(key, seconds)
