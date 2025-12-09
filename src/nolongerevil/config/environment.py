"""Environment configuration with validation."""

from pathlib import Path

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
    proxy_port: int = Field(
        default=443,
        description="Port for device API (Nest protocol emulation)",
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
    subscription_timeout_ms: int = Field(
        default=0,
        description="Long-poll timeout in milliseconds (0 = infinite)",
    )
    max_subscriptions_per_device: int = Field(
        default=100,
        description="Maximum concurrent subscriptions per device",
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

    # Database configuration
    sqlite3_enabled: bool = Field(
        default=True,
        description="Use SQLite3 for persistence",
    )
    sqlite3_db_path: str = Field(
        default="./data/database.sqlite",
        description="Path to SQLite3 database file",
    )

    # MQTT configuration
    mqtt_broker_url: str | None = Field(
        default=None,
        description="MQTT broker URL (e.g., mqtt://localhost:1883)",
    )
    mqtt_topic_prefix: str = Field(
        default="nolongerevil",
        description="Prefix for MQTT topics",
    )

    @property
    def weather_cache_ttl_seconds(self) -> float:
        """Get weather cache TTL in seconds."""
        return self.weather_cache_ttl_ms / 1000.0

    @property
    def subscription_timeout_seconds(self) -> float | None:
        """Get subscription timeout in seconds, or None for infinite."""
        if self.subscription_timeout_ms == 0:
            return None
        return self.subscription_timeout_ms / 1000.0

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
