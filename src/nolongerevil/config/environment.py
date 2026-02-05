"""Environment configuration with validation."""

from pathlib import Path
from urllib.parse import urlparse, urlunparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    api_origin: str = Field(
        default="https://backdoor.nolongerevil.com",
        description="API URL for device communication",
    )
    proxy_host: str = Field(
        default="0.0.0.0",
        description="Host/IP to bind device API server",
    )
    proxy_port: int = Field(
        default=443,
        description="Port for device API (Nest protocol emulation)",
    )
    control_host: str = Field(
        default="0.0.0.0",
        description="Host/IP to bind control API server",
    )
    control_port: int = Field(
        default=8081,
        description="Port for control API (dashboard/automation)",
    )

    # TLS configuration
    cert_dir: str | None = Field(
        default=None,
        description="Directory containing TLS certificates",
    )

    # Entry key configuration
    entry_key_ttl_seconds: int = Field(
        default=3600,
        description="Pairing code expiration time in seconds",
    )

    # Weather configuration
    weather_cache_ttl_ms: int = Field(
        default=600000,
        description="Weather cache duration in milliseconds",
    )

    # Subscription configuration
    max_subscriptions_per_device: int = Field(
        default=100,
        description="Maximum concurrent subscriptions per device",
    )
    suspend_time_max: int = Field(
        default=60,
        ge=30,
        le=300,
        description="Maximum time in seconds before server sends tickle response",
    )

    # Debug configuration
    debug_logging: bool = Field(
        default=False,
        description="Enable detailed request/response logging",
    )
    debug_logs_dir: str = Field(
        default="./data/debug-logs",
        description="Directory for debug log files",
    )
    store_device_logs: bool = Field(
        default=False,
        description="Store uploaded device logs to disk",
    )

    # Database configuration
    sqlite3_db_path: str = Field(
        default="./data/database.sqlite",
        description="Path to SQLite3 database file",
    )

    # MQTT configuration (from environment variables set by run.sh)
    mqtt_host: str | None = Field(
        default=None,
        description="MQTT broker hostname",
    )
    mqtt_port: int = Field(
        default=1883,
        description="MQTT broker port",
    )
    mqtt_user: str | None = Field(
        default=None,
        description="MQTT username",
    )
    mqtt_password: str | None = Field(
        default=None,
        description="MQTT password",
    )
    mqtt_topic_prefix: str = Field(
        default="nolongerevil",
        description="Prefix for MQTT topics",
    )
    mqtt_discovery_prefix: str = Field(
        default="homeassistant",
        description="Home Assistant MQTT discovery prefix",
    )

    @property
    def mqtt_broker_url(self) -> str | None:
        """Get MQTT broker URL from host/port."""
        if not self.mqtt_host:
            return None
        return f"mqtt://{self.mqtt_host}:{self.mqtt_port}"

    @property
    def api_origin_with_port(self) -> str:
        """Get API origin with explicit port for device URLs.

        The Nest device firmware parses ports from URLs by searching backwards
        for ':' followed by digits. URLs without explicit ports (like
        http://192.168.20.20/path) fail to extract the port, causing the device
        to use a stale cached port value for TCP keepalive offload configuration.

        This property ensures the port is always explicit in URLs sent to devices.
        """
        parsed = urlparse(self.api_origin)
        if parsed.port is None:
            netloc = f"{parsed.hostname}:{self.proxy_port}"
            return urlunparse(parsed._replace(netloc=netloc))
        return self.api_origin

    @property
    def weather_cache_ttl_seconds(self) -> float:
        """Get weather cache TTL in seconds."""
        return self.weather_cache_ttl_ms / 1000.0

    @property
    def tickle_timeout(self) -> float:
        """Get tickle timeout (80% of suspend_time_max)."""
        return self.suspend_time_max * 0.80

    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return Path(self.sqlite3_db_path).parent

    def ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.debug_logging:
            Path(self.debug_logs_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()
