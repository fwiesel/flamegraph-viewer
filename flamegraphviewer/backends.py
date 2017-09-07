import contextlib
import redis

@contextlib.contextmanager
def get_db(db_url):
    yield redis.StrictRedis.from_url(db_url)
