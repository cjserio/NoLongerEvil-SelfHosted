"""Authentication-related SQLModel models."""

from typing import Optional

from sqlalchemy import Column, Index, Text
from sqlmodel import Field, SQLModel


class APIKeyModel(SQLModel, table=True):
    """API authentication key stored in the 'apiKeys' table."""

    __tablename__ = "apiKeys"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyHash: str = Field(unique=True)
    keyPreview: str
    userId: str
    name: str
    permissions: str = Field(sa_column=Column(Text))  # JSON as text
    createdAt: int  # Millisecond timestamp
    expiresAt: Optional[int] = None  # Millisecond timestamp
    lastUsedAt: Optional[int] = None  # Millisecond timestamp

    __table_args__ = (
        Index("idx_apiKeys_userId", "userId"),
        Index("idx_apiKeys_keyHash", "keyHash"),
    )
