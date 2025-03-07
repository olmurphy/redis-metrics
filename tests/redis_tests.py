import unittest
from unittest.mock import MagicMock, mock_open, patch

import redis
from src.redis_config import RedisConfig
from src.redis_metrics import RedisMetrics


class TestRedisConfig(unittest.TestCase):

    def setUp(self):
        self.redis_url = "redis://user:password@localhost:6379/0"
        self.redis_cert_path = "test_cert.pem"
        self.logger = MagicMock()
        self.config = RedisConfig(
            redis_url=self.redis_url,
            redis_cert_path=self.redis_cert_path,
            logger=self.logger,
            max_connections=10,
        )

    def test_init(self):
        self.assertEqual(self.config.redis_url, self.redis_url)
        self.assertEqual(self.config.redis_cert_path, self.redis_cert_path)
        self.assertEqual(self.config.logger, self.logger)
        self.assertEqual(self.config.max_connections, 10)
        self.assertIsNone(self.config._redis_client)

    @patch("urllib.parse.urlparse")
    @patch("builtins.open", new_callable=mock_open, read_data="base64encodedcert")
    @patch("base64.b64decode")
    @patch("tempfile.NamedTemporaryFile")
    @patch("redis.ConnectionPool.from_url")
    def test_create_redis_client_success(
        self,
        mock_from_url,
        mock_tempfile,
        mock_b64decode,
        mock_open_file,
        mock_urlparse,
    ):
        mock_urlparse.return_value = MagicMock(
            hostname="localhost",
            port=6379,
            path="/0",
            password="password",
            username="user",
        )
        mock_b64decode.return_value = b"decodedcert"
        mock_tempfile_instance = MagicMock()
        mock_tempfile_instance.name = "temp_cert_path"
        mock_tempfile.NamedTemporaryFile.return_value.__enter__.return_value = (
            mock_tempfile_instance
        )

        self.config._create_redis_client()

        mock_from_url.assert_called_once()

    @patch("urllib.parse.urlparse")
    @patch("builtins.open", new_callable=mock_open, read_data="base64encodedcert")
    @patch("base64.b64decode")
    @patch("tempfile.NamedTemporaryFile")
    @patch("redis.ConnectionPool.from_url")
    def test_create_redis_client_connection_error(
        self,
        mock_from_url,
        mock_tempfile,
        mock_b64decode,
        mock_open_file,
        mock_urlparse,
    ):
        mock_from_url.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        mock_urlparse.return_value = MagicMock(
            hostname="localhost",
            port=6379,
            path="/0",
            password="password",
            username="user",
        )

        self.config._create_redis_client()

        self.logger.error.assert_called_once()

    @patch("urllib.parse.urlparse")
    def test_create_redis_client_no_url(self, mock_urlparse):
        self.config.redis_url = None
        self.config._create_redis_client()
        self.logger.debug.assert_called_once()

    def test_get_redis_client(self):
        with patch.object(self.config, "_create_redis_client") as mock_create:
            mock_create.return_value = "mock_client"
            client = self.config.get_redis_client()
            self.assertEqual(client, "mock_client")
            client2 = self.config.get_redis_client()
            self.assertEqual(client2, "mock_client")
            mock_create.assert_called_once()

    @patch("redis.Redis")
    def test_is_connected_true(self, mock_redis):
        mock_redis_instance = MagicMock()
        mock_redis.return_value.__enter__.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        self.config._redis_client = "mock_pool"
        self.assertTrue(self.config.is_connected())

    @patch("redis.Redis")
    def test_is_connected_false(self, mock_redis):
        mock_redis.side_effect = redis.exceptions.ConnectionError
        self.config._redis_client = "mock_pool"
        self.assertFalse(self.config.is_connected())

    def test_close_connection(self):
        mock_pool = MagicMock()
        self.config._redis_client = mock_pool
        self.config.close_connection()
        mock_pool.disconnect.assert_called_once()
        self.assertIsNone(self.config._redis_client)

    def test_update_max_connections_valid(self):
        self.config.update_max_connections(20)
        self.assertEqual(self.config.max_connections, 20)
        mock_pool = MagicMock()
        self.config._redis_client = mock_pool
        self.config.update_max_connections(30)
        self.assertEqual(self.config.max_connections, 30)
        mock_pool.max_connections = 30

    def test_update_max_connections_invalid(self):
        self.config.update_max_connections(0)
        self.logger.warning.assert_called_once()

    def test_repr(self):
        expected_repr = f"RedisConfig(redis_url='{self.redis_url}', redis_cert_path='{self.redis_cert_path}', max_connections=10)"
        self.assertEqual(repr(self.config), expected_repr)


class TestRedisMetrics(unittest.TestCase):

    def setUp(self):
        self.redis_pool = MagicMock()
        self.logger = MagicMock()
        self.metrics = RedisMetrics(
            redis_pool=self.redis_pool,
            logger=self.logger,
            polling_interval=1,
            slowlog_max_len=10,
        )
        self.redis_client = self.metrics.redis_client
        self.redis_client.info = MagicMock()
        self.redis_client.slowlog_get = MagicMock()

    def test_init(self):
        self.assertEqual(self.metrics.redis_client, self.redis_client)
        self.assertEqual(self.metrics.logger, self.logger)
        self.assertEqual(self.metrics.polling_interval, 1)
        self.assertEqual(self.metrics.slowlog_max_len, 10)

    def test_fetch_metrics_success(self):
        self.redis_client.info.return_value = {"connected_clients": 1}
        metrics = self.metrics._fetch_metrics()
        self.assertIn("connections", metrics)

    def test_fetch_metrics_connection_error(self):
        self.redis_client.info.side_effect = redis.exceptions.ConnectionError(
            "Connection failed"
        )
        metrics = self.metrics._fetch_metrics()
        self.assertEqual(metrics, {})
        self.logger.error.assert_called_once()

    def test_connection_metrics(self):
        info = {
            "connected_clients": 10,
            "rejected_connections": 5,
            "total_connections_received": 20,
        }
        metrics = self.metrics._connection_metrics(info)
        self.assertEqual(metrics["connected_clients"], 10)
        self.assertEqual(metrics["rejected_connections"], 5)

    def test_memory_metrics(self):
        info = {
            "used_memory": 1000,
            "used_memory_peak": 2000,
            "mem_fragmentation_ratio": 1.5,
            "evicted_keys": 10,
        }
        metrics = self.metrics._memory_metrics(info)
        self.assertEqual(metrics["used_memory"], 1000)
