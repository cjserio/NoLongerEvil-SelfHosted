"""Integration and weather-related SQLModel models."""

from sqlalchemy import Column, Index, Text
from sqlmodel import Field, SQLModel


class IntegrationConfigModel(SQLModel, table=True):
    """Third-party integration config stored in the 'integrations' table."""

    __tablename__ = "integrations"

    userId: str = Field(primary_key=True)
    type: str = Field(primary_key=True)
    enabled: int  # Boolean as integer (0/1)
    config: str = Field(sa_column=Column(Text))  # JSON as text
    createdAt: int  # Millisecond timestamp
    updatedAt: int  # Millisecond timestamp

    __table_args__ = (
        Index("idx_integrations_enabled", "enabled"),
    )


class WeatherDataModel(SQLModel, table=True):
    """Cached weather data stored in the 'weather' table."""

    __tablename__ = "weather"

    postalCode: str = Field(primary_key=True)
    country: str = Field(primary_key=True)
    fetchedAt: int  # Millisecond timestamp
    data: str = Field(sa_column=Column(Text))  # JSON as text
