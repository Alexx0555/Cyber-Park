import json
import logging
from datetime import datetime
from functools import wraps
from typing import List
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, app=None):
        self.redis_client = None
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('CACHE_REDIS_HOST', 'localhost'),
                port=app.config.get('CACHE_REDIS_PORT', 6379),
                db=app.config.get('CACHE_REDIS_DB', 0),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            self.redis_client.ping()
            logger.info(" Redis cache connection established")

        except Exception as e:
            logger.error(f" Redis connection failed: {e}")
            self.redis_client = None
    
    def is_available(self):
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def get(self, key):
        if not self.is_available():
            logger.debug(f"Cache miss (Redis unavailable): {key}")
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                return None
            
            logger.debug(f"Cache hit: {key}")
            return json.loads(value)
        
        except Exception as e:
            logger.error(f"Cache get error for {key}: {e}")
            return None
    
    def set(self,key,value,ttl=300):
        if not self.is_available():
            logger.debug(f"Cache set skipped (Redis unavailable): {key}")
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            result = self.redis_client.setex(key, ttl, serialized_value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return result
        
        except Exception as e:
            logger.error(f"Cache set error for {key}: {e}")
            return False
    
    def delete(self,key):
        if not self.is_available():
            return False
        
        try:
            result = self.redis_client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return bool(result)
        
        except Exception as e:
            logger.error(f"Cache delete error for {key}: {e}")
            return False
    
    def delete_pattern(self, pattern):
        if not self.is_available():
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                result = self.redis_client.delete(*keys)
                logger.debug(f"Cache delete pattern: {pattern} ({len(keys)} keys)")
                return result
            return 0
        
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def exists(self,key):
        if not self.is_available():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        
        except Exception as e:
            logger.error(f"Cache exists error for {key}: {e}")
            return False
    
    def get_stats(self):
        if not self.is_available():
            return {"status": "unavailable"}
        
        try:
            info = self.redis_client.info()
            return {
                "status": "available",
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "0B"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            }
        
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "error": str(e)}

cache_manager = CacheManager()

class CacheKeys:
    @staticmethod
    def user_profile(user_id):
        return f"user:profile:{user_id}"
    
    @staticmethod
    def user_session(token):
        return f"user:session:{token}"
    
    @staticmethod
    def user_reservations(user_id):
        return f"user:reservations:{user_id}"
    
    @staticmethod
    def user_active(user_id):
        return f"user:active:{user_id}"
    
    @staticmethod
    def parking_lot(lot_id):
        return f"parking:lot:{lot_id}"
    
    @staticmethod
    def parking_spots(lot_id):
        return f"parking:spots:{lot_id}"
    
    @staticmethod
    def parking_availability(lot_id):
        return f"parking:availability:{lot_id}"
    
    @staticmethod
    def parking_lots_all():
        return "parking:lots:all"
    
    @staticmethod
    def spot_status(lot_id,spot_number):
        return f"spot:status:{lot_id}:{spot_number}"
    
    @staticmethod
    def admin_revenue_daily(date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"admin:revenue:daily:{date}"
    
    @staticmethod
    def admin_usage(lot_id):
        return f"admin:usage:{lot_id}"
    
    @staticmethod
    def admin_stats(date=None):
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        return f"admin:stats:{date}"
    
    @staticmethod
    def admin_history():
        return "admin:history:all"

class CacheTTL:
    USER_PROFILE = 3600        # 1 hr
    USER_SESSION = 7200        # 2 hrs (or token expiry)
    USER_RESERVATIONS = 600    # 10 mins
    USER_ACTIVE = 300          # 5 mins
    
    PARKING_LOT = 3600         # 1 hr
    PARKING_SPOTS = 120        # 2 mins
    PARKING_AVAILABILITY = 120 # 2 mins
    PARKING_LOTS_ALL = 1800    # 30 mins
    
    SPOT_STATUS = 120          # 2 mins
    
    ADMIN_REVENUE = 900        # 15 mins
    ADMIN_USAGE = 900          # 15 mins
    ADMIN_STATS = 3600         # 1 hr
    ADMIN_HISTORY = 600        # 10 mins
    ADMIN_RECORDS = 300        # 5 mins
    ADMIN_FEEDBACK = 600       # 10 mins

def cached(key_func,ttl=300,invalidate_on: List[str] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
            
            if invalidate_on:
                for pattern in invalidate_on:
                    cache_manager.delete_pattern(pattern)
            
            return result
        return wrapper
    return decorator

def invalidate_user_cache(user_id):
    patterns = [
        f"user:*:{user_id}",
        f"user:*:{user_id}:*"
    ]
    for pattern in patterns:
        cache_manager.delete_pattern(pattern)

    logger.info(f"Invalidated user cache for user_id: {user_id}")

def invalidate_parking_cache(lot_id=None):
    if lot_id:
        patterns = [
            f"parking:*:{lot_id}",
            f"spot:*:{lot_id}:*"
        ]
    else:
        patterns = [
            "parking:*",
            "spot:*"
        ]
    
    for pattern in patterns:
        cache_manager.delete_pattern(pattern)

    logger.info(f"Invalidated parking cache for lot_id: {lot_id or 'all'}")

def invalidate_admin_cache():
    patterns = ["admin:*"]
    for pattern in patterns:
        cache_manager.delete_pattern(pattern)
    logger.info("Invalidated admin cache")