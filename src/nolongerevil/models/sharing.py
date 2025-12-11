"""Device sharing-related SQLModel models."""

from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class DeviceShareModel(SQLModel, table=True):
    """Device share between users stored in the 'deviceShares' table."""

    __tablename__ = "deviceShares"

    ownerId: str = Field(primary_key=True)
    sharedWithUserId: str = Field(primary_key=True)
    serial: str = Field(primary_key=True)
    permissions: str  # Enum value stored as string ("read", "write", "control", "admin")
    createdAt: int  # Millisecond timestamp

    __table_args__ = (
        Index("idx_deviceShares_serial", "serial"),
        Index("idx_deviceShares_sharedWithUserId", "sharedWithUserId"),
    )


class DeviceShareInviteModel(SQLModel, table=True):
    """Device share invitation stored in the 'seviceShareInvites' table.

    Note: Table name has intentional typo to match existing schema.
    """

    __tablename__ = "seviceShareInvites"  # Intentional typo - matches existing schema

    inviteToken: str = Field(primary_key=True)
    ownerId: str
    email: str
    serial: str
    permissions: str  # Enum value stored as string
    status: str  # Enum value stored as string ("pending", "accepted", "expired", "revoked")
    invitedAt: int  # Millisecond timestamp
    expiresAt: int  # Millisecond timestamp
    acceptedAt: int | None = None  # Millisecond timestamp
    sharedWithUserId: str | None = None
