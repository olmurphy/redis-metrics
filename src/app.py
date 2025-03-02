import argparse
import os

from dotenv import load_dotenv
from logger import get_logger
from redis_config import RedisConfig
from redis_metrics import RedisMetrics

if __name__ == "__main__":
    load_dotenv()
    logger = get_logger(logger_name="Redis Metrics")

    parser = argparse.ArgumentParser(description="Collect Redis metrics.")
    parser.add_argument("--redis-url", required=True, help="Redis connection URL.")
    parser.add_argument(
        "--redis-cert-path", required=True, help="Path to Redis certificate."
    )
    args = parser.parse_args()

    redis_config = RedisConfig(  # Initialize RedisConfig
        redis_url=os.environ.get("REDIS_URL"),
        redis_cert_path=os.environ.get("REDIS_CERT_PATH"),
        logger=logger,
        max_connections=10,
    )
    redis_pool = redis_config.get_redis_client()
    try:
        redis_metrics = RedisMetrics(
            redis_pool=redis_config.get_redis_client(), logger=logger
        )
        redis_metrics.log_metrics()
    except Exception as e:
        logger.error({"message": "Failed to run Redis Metrics"})
