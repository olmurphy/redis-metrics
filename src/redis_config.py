"""Module for configuring and creating a Redis client.

This module provides the `RedisConfig` class, which parses a Redis URL,
handles SSL certificate decoding, and creates a Redis connection pool.
It supports secure connections using SSL certificates.
"""

import base64
import tempfile
import urllib.parse
from logging import Logger

import redis

FALLBACK_PORT: int = 6379
DEFAULT_MAX_CONNECTIONS = 10


class RedisConfig:
    """Configures and creates a Redis connection pool.

    This class parses a Redis URL, decodes SSL certificates, and creates a
    Redis connection pool for secure connections. It handles connection errors
    and provides lazy initialization of the Redis client.

    Attributes:
        redis_url: The Redis connection URL.
        redis_cert_path: The path to the SSL certificate file.
        logger: Logger instance for logging messages.
        max_connections: Maximum number of connections in the pool.
        _redis_client: Lazily initialized Redis connection pool.
    """

    def __init__(
        self,
        redis_url=None,
        redis_cert_path=None,
        logger=None,
        max_connections=DEFAULT_MAX_CONNECTIONS,
    ):
        """Initializes RedisConfig.

        Args:
            redis_url: The Redis connection URL.
            redis_cert_path: The path to the SSL certificate file.
            logger: Logger instance for logging messages. Defaults to None.
            max_connections: Maximum number of connections in the pool. Defaults to 10.
        """
        self.redis_url = redis_url
        self.redis_cert_path = redis_cert_path
        self.logger: Logger = logger
        self._redis_client = None  # Lazy initialization
        self.max_connections = max_connections

    def _create_redis_client(self):
        """Creates a Redis connection pool.

        Parses the Redis URL, decodes the SSL certificate, and creates a
        Redis connection pool with SSL enabled.

        Returns:
            A Redis connection pool or None if an error occurs.
        """
        if not self.redis_url:
            if self.logger:
                self.logger.debug({"message": "No Redis URL supplied"})
            return None
        try:
            parsed_url = urllib.parse.urlparse(self.redis_url)
            host = parsed_url.hostname
            port = parsed_url.port or FALLBACK_PORT  # Default Redis port
            db = (
                int(parsed_url.path.strip("/")) if parsed_url.path else 0
            )  # get the index from the url
            password = parsed_url.password
            username = parsed_url.username  # get the username

            if self.logger:
                self.logger.debug(
                    {
                        "message": "Redis client created",
                        "data": {
                            "host": host,
                            "port": port,
                            "db": db,
                            "cert_path": self.redis_cert_path,
                            "username": username,
                            "password": password,
                        },
                    }
                )  # logging for debugging

            with open(self.redis_cert_path, "r", encoding="utf-8") as f:
                encoded_cert = f.read()
            decoded_cert = base64.b64decode(encoded_cert).decode("utf-8")

            with tempfile.NamedTemporaryFile(delete=False) as temp_cert_file:
                temp_cert_file.write(decoded_cert.encode("utf-8"))
                temp_cert_path = temp_cert_file.name

            redis_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=self.max_connections,
                ssl_ca_certs=temp_cert_path,
                ssl_cert_reqs="required",
            )
            return redis_pool
        except (redis.exceptions.ConnectionError, ValueError) as e:
            if self.logger:
                self.logger.error(
                    {
                        "message": "Error connecting to Redis Instance",
                        "data": f"host: {host}, port: {port}, db: {db}",
                        "error": e,
                    }
                )  # logging for error.
            return None

    def get_redis_client(self):
        """Returns the Redis connection pool.

        Returns:
            The Redis connection pool or None if it could not be created.
        """
        if self._redis_client is None:
            self._redis_client = self._create_redis_client()
        return self._redis_client

    def is_connected(self) -> bool:
        """Checks if the Redis client is connected.

        Returns:
            True if connected, False otherwise.
        """
        if self._redis_client:
            try:
                with redis.Redis(connection_pool=self._redis_client) as r:
                    r.ping()
                return True
            except redis.exceptions.ConnectionError:
                return False
        return False

    def close_connection(self) -> None:
        """Closes the Redis connection pool.

        This method should be called when the Redis client is no longer needed.
        """
        if self._redis_client:
            self._redis_client.disconnect()
            self._redis_client = None

    def update_max_connections(self, new_max: int) -> None:
        """Updates the maximum number of connections in the pool.

        Args:
            new_max: The new maximum number of connections.
        """
        if new_max > 0:
            self.max_connections = new_max
            if self._redis_client:
                self._redis_client.max_connections = new_max
        else:
            if self.logger:
                self.logger.warning({"message": "Invalid max_connections value"})

    def __repr__(self) -> str:
        """Returns a string representation of the RedisConfig object."""
        return (
            f"RedisConfig("
            f"redis_url={self.redis_url!r}, "
            f"redis_cert_path={self.redis_cert_path!r}, "
            f"max_connections={self.max_connections})"
        )
