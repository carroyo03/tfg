import redis
import json
import reflex as rx

redis_client = redis.Redis(host='localhost', port=6379, db=0)
class CacheState(rx.State):



    @rx.event
    def cache_results(self,results,user_email=None):
        if user_email:

            key = f"results:{user_email}"
        else:
            key = f"results:guest:{id(results)}"

        redis_client.setex(name=key, time=3600, value=json.dumps(results))
        print(f"Cache results in Redis with {key}")

    @classmethod
    def get_cache_results(self, user_email=None):
        if user_email:
            key = f"results:{user_email}"
        else:
            key = f"results:guest:{id(self)}"
        cached = redis_client.get(key)
        return json.loads(cached) if cached else None