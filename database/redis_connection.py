from upstash_redis import Redis
from config import Config

redis_url = Config.REDIS_URL
redis_token = Config.REDIS_TOKEN

# Crear la conexión con Redis usando Upstash
def get_redis_connection():
    return Redis(url=Config.REDIS_URL, token=Config.REDIS_TOKEN)
            
