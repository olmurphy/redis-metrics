"""Main script to collect and log Redis metrics.

This script initializes a Redis configuration, establishes a connection pool,
and then collects and logs Redis metrics using the `RedisMetrics` class.
It also handles environment variable loading and error logging.
"""

import os
import traceback

import redis
from dotenv import load_dotenv
from logger import get_logger
from redis_config import RedisConfig
from redis_metrics import RedisMetrics

if __name__ == "__main__":

    # Load environment variables from .env file
    load_dotenv()

    # Initialize logger
    logger = get_logger(logger_name="Redis Metrics")

    # Initialize Redis configuration
    redis_config = RedisConfig(
        redis_url=os.environ.get("REDIS_URL"),
        redis_cert_path=os.environ.get("REDIS_CERT_PATH"),
        logger=logger,
        max_connections=10,
    )

    # Get Redis connection pool
    redis_pool = redis_config.get_redis_client()

    try:
        # Initialize Redis metrics collector
        redis_metrics = RedisMetrics(
            redis_pool=redis_config.get_redis_client(), logger=logger
        )

        # Log Redis metrics
        redis_metrics.log_metrics()

    except redis.exceptions.ConnectionError as e:
        # Log error if metrics collection fails
        logger.error({"message": "Failed to run Redis Metrics", "error": e})
    except redis.exceptions.TimeoutError as e:
        logger.error(
            {"message": "Redis connection timed out", "error": traceback.format_exc()}
        )
