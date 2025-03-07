"""Module for collecting and logging Redis metrics.

This module provides the `RedisMetrics` class, which connects to a Redis instance
and periodically collects and logs various performance and operational metrics.
It supports connection, memory, performance, persistence, pub/sub, and CPU usage
metrics, as well as slow log monitoring.
"""

import base64
import datetime
import threading
import time
from logging import Logger
from typing import Any, Dict

import redis


class RedisMetrics:
    """Collects and logs Redis metrics.

    This class provides functionality to connect to a Redis instance,
    collect various metrics at regular intervals, and log them using a
    provided logger. It also supports monitoring the Redis slow log.

    Attributes:
        redis_client: Redis client instance.
        logger: Logger instance for logging metrics and errors.
        polling_interval: Interval in seconds for collecting metrics.
        slowlog_max_len: Maximum number of slow log entries to retrieve.
        collection_interval: Interval in seconds for calculating command rate.
        _stop_event: Threading event to stop the metric collection thread.
        _thread: Thread for running the metric collection loop.
        previous_commands_processed: Previous number of commands processed.
        elapsed_time: Time elapsed for calculating command rate.
    """

    def __init__(
        self,
        redis_pool,
        logger: Logger = None,
        polling_interval=10,
        slowlog_max_len=128,
    ):
        """Initializes RedisMetrics.

        Args:
            redis_pool: Redis connection pool.
            logger: Logger instance for logging. Defaults to None.
            polling_interval: Interval in seconds for collecting metrics. Defaults to 10.
            slowlog_max_len: Maximum number of slow log entries to retrieve. Defaults to 128.
        """
        self.redis_client = redis.Redis(connection_pool=redis_pool)
        self.logger: Logger = logger
        self.polling_interval = polling_interval
        self.slowlog_max_len = slowlog_max_len
        self.collection_interval = 10
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self.previous_commands_processed = 0
        self.elapsed_time = 0

    def _fetch_metrics(self) -> Dict[str, Any]:
        """Fetches Redis metrics.

        Returns:
            A dictionary containing various Redis metrics.
        """
        try:
            info = self.redis_client.info()
            metrics = {
                "connections": self._connection_metrics(info),
                "memory_usage": self._memory_metrics(info),
                "performance": self._performance_metrics(info),
                "persistence": self._persistence_metrics(info),
                "pubsub": self._pubsub_metrics(info),
                "cpu": self._cpu_usage(),
            }
            return metrics
        except redis.exceptions.ConnectionError as e:
            if self.logger:
                self.logger.error(
                    {"message": "Failed to fetch Redis metrics", "error": str(e)}
                )
            return {}

    def _connection_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts connection-related metrics.

        Args:
            info: Redis info dictionary.

        Returns:
            A dictionary containing connection metrics.
        """
        return {
            "connected_clients": info.get("connected_clients", 0),
            "connection_errors": info.get("rejected_connections", 0),
            "connection_rate": info.get("total_connections_received", 0),
            "rejected_connections": info.get("rejected_connections", 0),
        }

    def _memory_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts memory-related metrics.

        Args:
            info: Redis info dictionary.

        Returns:
            A dictionary containing memory metrics.
        """
        return {
            "used_memory": info.get("used_memory", 0),
            "used_memory_peak": info.get("used_memory_peak", 0),
            "memory_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0),
            "evicted_keys": info.get("evicted_keys", 0),
        }

    def _performance_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts performance-related metrics.

        Args:
            info: Redis info dictionary.

        Returns:
            A dictionary containing performance metrics.
        """
        try:
            stats = self.redis_client.info("stats")
            total_commands_processed = int(stats.get("total_commands_processed", 0))

            if self.elapsed_time > 0:
                command_rate = (
                    total_commands_processed - self.previous_commands_processed
                ) / self.elapsed_time
            else:
                command_rate = 0

            self.previous_commands_processed = total_commands_processed
            self.elapsed_time = self.collection_interval

            return {
                "latency": self._measure_latency(),
                "commands_per_second": stats.get("instantaneous_ops_per_sec", 0),
                "cache_hit_ratio": self._calculate_cache_hit_ratio(info),
                "total_commands_processed": total_commands_processed,
                "instantaneous_ops_per_sec": stats.get("instantaneous_ops_per_sec"),
                "keyspace_hits": stats.get("keyspace_hits"),
                "keyspace_misses": stats.get("keyspace_misses"),
                "command_rate": command_rate,
            }
        except redis.exceptions.RedisError as e:
            if self.logger:
                self.logger.error(
                    {"message": "Error retrieving performance metrics:", "error": e}
                )
            return {}

    def _persistence_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts persistence-related metrics.

        Args:
            info: Redis info dictionary.

        Returns:
            A dictionary containing persistence metrics.
        """
        return {
            "rdb_last_save_time": info.get("rdb_last_save_time", None),
            "aof_enabled": info.get("aof_enabled", None),
            "aof_last_rewrite_time_sec": info.get("aof_last_rewrite_time_sec", None),
            "aof_delayed_fsyncs": info.get("aof_delayed_fsync", 0),
        }

    def _pubsub_metrics(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts pub/sub-related metrics.

        Args:
            info: Redis info dictionary.

        Returns:
            A dictionary containing pub/sub metrics.
        """
        return {
            "pubsub_channels": info.get("pubsub_channels", 0),
            "pubsub_patterns": info.get("pubsub_patterns", 0),
        }

    def _cpu_usage(self) -> Dict[str, Any]:
        """Extracts CPU usage metrics.

        Returns:
            A dictionary containing CPU usage metrics.
        """
        return {
            "cpu": self.redis_client.info(section="cpu"),
        }

    def _measure_latency(self) -> float:
        """Measures Redis latency.

        Returns:
            Redis latency in milliseconds.
        """
        try:
            start = time.time()
            self.redis_client.ping()
            return (time.time() - start) * 1000  # Convert to milliseconds
        except redis.exceptions.ConnectionError:
            return float("inf")

    def _calculate_cache_hit_ratio(self, info: Dict[str, Any]) -> float:
        """Calculates cache hit ratio.

        Args:
            info: Redis info dictionary.

        Returns:
            Cache hit ratio as a percentage.
        """
        keyspace_hits = info.get("keyspace_hits", 0)
        keyspace_misses = info.get("keyspace_misses", 0)
        total_requests = keyspace_hits + keyspace_misses
        return (keyspace_hits / total_requests) * 100 if total_requests else 0

    def _log_slow_log(self):
        """Logs Redis slow log entries."""
        try:
            formatted_logs = []  # Store formatted log entries
            slow_logs = self.redis_client.slowlog_get(self.slowlog_max_len)
            for log in slow_logs:
                duration_ms = log["duration"] / 1000.0

                try:  # Decode command (if simple)
                    command = base64.b64decode(log["command"]).decode("utf-8")
                # pylint: disable=W0718
                except Exception:
                    command = log["command"]

                try:  # Decode address
                    address = base64.b64decode(log["client_address"]).decode("utf-8")
                # pylint: disable=W0718
                except Exception:
                    address = log["client_address"]

                timestamp = datetime.datetime.fromtimestamp(
                    log["start_time"]
                ).isoformat()

                # Create a more readable log entry
                log_entry = {
                    "id": log["id"],
                    "timestamp": timestamp,
                    "duration_ms": duration_ms,
                    "command": command,
                    "client_address": address,
                    "client_name": log["client_name"],
                }
                formatted_logs.append(log_entry)  # append the log entry to the list.

            if formatted_logs:  # only log if there are logs.
                if self.logger:
                    self.logger.warning(
                        {"message": "Redis Slow Log", "logs": formatted_logs}
                    )
        except redis.exceptions.RedisError as e:
            if self.logger:
                self.logger.error({"message": "Error retrieving slow log", "error": e})

    def log_metrics(self):
        """Logs the collected Redis metrics and slow log."""
        metrics = self._fetch_metrics()
        if self.logger:
            self.logger.info({"message": "Redis Metrics", "redis_metrics": metrics})
            self._log_slow_log()

    def start(self):
        """Starts the metric collection thread."""
        self._thread.start()

    def stop(self):
        """Stops the metric collection thread."""
        self._stop_event.set()
        self._thread.join()

    def _run(self):
        """Runs the metric collection loop."""
        while not self._stop_event.is_set():
            try:
                self.log_metrics()
                time.sleep(self.polling_interval)
            except redis.exceptions.RedisError as e:
                if self.logger:
                    self.logger.error(
                        {"message": "Error in metric collection loop", "error": e}
                    )
