"""Subscription manager for long-polling connections.

Silent subscriptions hold the HTTP connection open without sending any response.
The notification queue wakes the handler when data arrives. When data is pushed
to the queue, the transport handler sends a complete HTTP response and closes.
"""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from aiohttp import web

from nolongerevil.config import settings
from nolongerevil.lib.logger import get_logger
from nolongerevil.lib.types import DeviceObject

logger = get_logger(__name__)

# If a subscription ended within this window, the next subscribe is a "re-subscribe"
RESUBSCRIBE_WINDOW_SECONDS = 5.0


@dataclass
class SilentSubscription:
    """A silent subscription (connection held open without HTTP response).

    The transport layer holds the HTTP connection open and waits on the
    notify_queue. When data is pushed to the queue, the transport sends
    a complete HTTP response and closes.
    """

    serial: str
    session_id: str
    subscribed_keys: dict[str, int]  # object_key -> last known revision
    # Queue for delivering notifications to transport layer
    # Transport loop waits on this; notify puts data here
    notify_queue: asyncio.Queue[list[dict[str, Any]]] = field(default_factory=asyncio.Queue)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PendingSubscription:
    """A pending long-poll subscription waiting for updates."""

    serial: str
    session_id: str
    subscribed_keys: dict[str, int]  # object_key -> last known revision
    future: asyncio.Future[list[DeviceObject]]
    created_at: datetime = field(default_factory=datetime.now)


class SubscriptionManager:
    """Manages active long-poll subscriptions.

    Silent subscriptions:
    - Connection is held open without sending HTTP response
    - Notification queue wakes the transport handler when data arrives
    - Transport sends complete response and closes

    Also supports future-based subscriptions for programmatic use.
    """

    def __init__(self) -> None:
        """Initialize the subscription manager."""
        self._subscriptions: dict[str, dict[str, PendingSubscription]] = {}
        self._silent_subscriptions: dict[str, dict[str, SilentSubscription]] = {}
        self._last_subscription_end: dict[str, float] = {}  # serial -> timestamp
        self._lock = asyncio.Lock()

    # ========== Silent Subscription Methods ==========

    async def add_silent_subscription(
        self,
        serial: str,
        session_id: str,
        subscribed_keys: dict[str, int],
    ) -> bool:
        """Add a silent subscription (connection held without response).

        Args:
            serial: Device serial number
            session_id: Session identifier
            subscribed_keys: Map of object_key -> last known revision

        Returns:
            True if added, False if limit exceeded
        """
        async with self._lock:
            device_subs = self._silent_subscriptions.get(serial, {})
            if len(device_subs) >= settings.max_subscriptions_per_device:
                logger.warning(
                    f"Max subscriptions ({settings.max_subscriptions_per_device}) "
                    f"exceeded for device {serial}"
                )
                return False

            subscription = SilentSubscription(
                serial=serial,
                session_id=session_id,
                subscribed_keys=subscribed_keys,
            )

            if serial not in self._silent_subscriptions:
                self._silent_subscriptions[serial] = {}
            self._silent_subscriptions[serial][session_id] = subscription

            logger.debug(
                f"Added silent subscription {session_id} for device {serial} "
                f"(total: {len(self._silent_subscriptions[serial])})"
            )

            return True

    async def remove_silent_subscription(self, serial: str, session_id: str) -> None:
        """Remove a silent subscription.

        Args:
            serial: Device serial number
            session_id: Session identifier
        """
        async with self._lock:
            if serial in self._silent_subscriptions:
                if session_id in self._silent_subscriptions[serial]:
                    del self._silent_subscriptions[serial][session_id]
                    self._last_subscription_end[serial] = time.monotonic()
                    logger.debug(f"Removed silent subscription {session_id} for {serial}")

                if not self._silent_subscriptions[serial]:
                    del self._silent_subscriptions[serial]

    async def notify_silent_subscribers(
        self,
        serial: str,
        changed_objects: list[dict[str, Any]],
    ) -> int:
        """Notify all silent subscribers for a device.

        This puts data on each subscription's queue. The transport layer
        (which is waiting on the queue) will wake up, send the HTTP response,
        and close the connection.

        Args:
            serial: Device serial number
            changed_objects: List of changed object dicts

        Returns:
            Number of subscribers notified (queued)
        """
        notified = 0

        async with self._lock:
            device_subs = self._silent_subscriptions.get(serial, {})

            for session_id, sub in device_subs.items():
                try:
                    # Put data on queue - transport layer will read and respond
                    sub.notify_queue.put_nowait(changed_objects)
                    notified += 1
                    logger.debug(f"Queued notification for silent subscriber {session_id}")

                except Exception as e:
                    logger.debug(f"Failed to queue notification for {session_id}: {e}")

        return notified

    def get_subscription_queue(
        self, serial: str, session_id: str
    ) -> asyncio.Queue[list[dict[str, Any]]] | None:
        """Get the notification queue for a subscription.

        Used by transport layer to wait for notifications.

        Args:
            serial: Device serial number
            session_id: Session identifier

        Returns:
            The notification queue, or None if subscription not found
        """
        device_subs = self._silent_subscriptions.get(serial, {})
        sub = device_subs.get(session_id)
        return sub.notify_queue if sub else None

    # ========== Future-based Subscription Methods ==========

    async def add_subscription(
        self,
        serial: str,
        subscribed_keys: dict[str, int],
    ) -> tuple[str, asyncio.Future[list[DeviceObject]]]:
        """Add a future-based subscription."""
        async with self._lock:
            device_subs = self._subscriptions.get(serial, {})
            if len(device_subs) >= settings.max_subscriptions_per_device:
                raise web.HTTPTooManyRequests(text="Too many subscriptions for this device")

            session_id = str(uuid.uuid4())
            future: asyncio.Future[list[DeviceObject]] = asyncio.Future()

            subscription = PendingSubscription(
                serial=serial,
                session_id=session_id,
                subscribed_keys=subscribed_keys,
                future=future,
            )

            if serial not in self._subscriptions:
                self._subscriptions[serial] = {}
            self._subscriptions[serial][session_id] = subscription

            return session_id, future

    async def remove_subscription(self, serial: str, session_id: str) -> None:
        """Remove a future-based subscription."""
        async with self._lock:
            if serial in self._subscriptions and session_id in self._subscriptions[serial]:
                sub = self._subscriptions[serial].pop(session_id)
                if not sub.future.done():
                    sub.future.cancel()

                if not self._subscriptions[serial]:
                    del self._subscriptions[serial]

    async def notify_subscribers(
        self,
        serial: str,
        updated_objects: list[DeviceObject],
    ) -> int:
        """Notify future-based subscribers."""
        notified = 0

        async with self._lock:
            device_subs = self._subscriptions.get(serial, {})
            sessions_to_remove = []

            for session_id, sub in device_subs.items():
                relevant_updates = []
                for obj in updated_objects:
                    if obj.object_key in sub.subscribed_keys:
                        last_rev = sub.subscribed_keys[obj.object_key]
                        if obj.object_revision > last_rev:
                            relevant_updates.append(obj)

                if relevant_updates and not sub.future.done():
                    sub.future.set_result(relevant_updates)
                    sessions_to_remove.append(session_id)
                    notified += 1

            for session_id in sessions_to_remove:
                del device_subs[session_id]

            if not device_subs and serial in self._subscriptions:
                del self._subscriptions[serial]

        return notified

    async def notify_subscribers_with_objects(
        self,
        serial: str,
        updated_objects: list[DeviceObject],
    ) -> int:
        """Notify subscribers with DeviceObject list (formats them).

        Args:
            serial: Device serial number
            updated_objects: List of DeviceObject instances

        Returns:
            Total number of subscribers notified
        """
        if not updated_objects:
            return 0

        # IMPORTANT: object_revision and object_timestamp MUST come before object_key
        # Note: serial omitted per spec - device extracts from object_key
        formatted_objects = [
            {
                "object_revision": obj.object_revision,
                "object_timestamp": obj.object_timestamp,
                "object_key": obj.object_key,
                "value": obj.value,
            }
            for obj in updated_objects
        ]
        return await self._notify_all(serial, formatted_objects, updated_objects)

    async def notify_subscribers_with_dicts(
        self,
        serial: str,
        formatted_objects: list[dict[str, Any]],
    ) -> int:
        """Notify subscribers with pre-formatted dicts.

        Args:
            serial: Device serial number
            formatted_objects: List of pre-formatted object dicts

        Returns:
            Total number of subscribers notified
        """
        if not formatted_objects:
            return 0
        return await self._notify_all(serial, formatted_objects, [])

    async def _notify_all(
        self,
        serial: str,
        formatted_objects: list[dict[str, Any]],
        device_objects: list[DeviceObject],
    ) -> int:
        """Internal: notify both silent and future-based subscribers.

        Args:
            serial: Device serial number
            formatted_objects: Pre-formatted object dicts for silent subscribers
            device_objects: Original DeviceObjects for future-based subscribers

        Returns:
            Total number of subscribers notified
        """
        total_notified = 0

        # Notify silent subscribers
        silent_count = await self.notify_silent_subscribers(serial, formatted_objects)
        total_notified += silent_count

        # Notify future-based subscribers (if we have DeviceObject list)
        if device_objects:
            future_count = await self.notify_subscribers(serial, device_objects)
            total_notified += future_count

        return total_notified

    async def notify_all_subscribers(
        self,
        serial: str,
        updated_objects: list[DeviceObject] | list[dict[str, Any]],
    ) -> int:
        """Notify all subscribers (both silent and future-based) for a device.

        Deprecated: Use notify_subscribers_with_objects or notify_subscribers_with_dicts
        for clearer type handling.

        Args:
            serial: Device serial number
            updated_objects: List of updated device objects (or dicts)

        Returns:
            Total number of subscribers notified
        """
        if not updated_objects:
            return 0

        # Handle both DeviceObject and dict inputs
        if isinstance(updated_objects[0], DeviceObject):
            return await self.notify_subscribers_with_objects(serial, updated_objects)  # type: ignore
        return await self.notify_subscribers_with_dicts(serial, updated_objects)  # type: ignore

    # ========== Utility Methods ==========

    def get_subscription_count(self, serial: str) -> int:
        """Get total subscriptions for a device."""
        future_count = len(self._subscriptions.get(serial, {}))
        silent_count = len(self._silent_subscriptions.get(serial, {}))
        return future_count + silent_count

    def get_total_subscription_count(self) -> int:
        """Get total subscriptions across all devices."""
        future_total = sum(len(subs) for subs in self._subscriptions.values())
        silent_total = sum(len(subs) for subs in self._silent_subscriptions.values())
        return future_total + silent_total

    def has_active_subscription(self, serial: str) -> bool:
        """Check if device has any active subscription."""
        has_future = serial in self._subscriptions and len(self._subscriptions[serial]) > 0
        has_silent = (
            serial in self._silent_subscriptions and len(self._silent_subscriptions[serial]) > 0
        )
        return has_future or has_silent

    def is_resubscribe(self, serial: str) -> bool:
        """Check if this is a re-subscribe (recent subscription ended).

        Returns True if a subscription for this device ended within the
        re-subscribe window (typically 5 seconds). This indicates the device
        is in a normal cycle and we can use standard timing.

        Returns False if this is a fresh subscribe (no recent history).
        """
        last_end = self._last_subscription_end.get(serial)
        if last_end is None:
            return False
        return (time.monotonic() - last_end) < RESUBSCRIBE_WINDOW_SECONDS

    def get_stats(self) -> dict[str, Any]:
        """Get subscription statistics."""
        return {
            "total_subscriptions": self.get_total_subscription_count(),
            "future_subscriptions": sum(len(subs) for subs in self._subscriptions.values()),
            "silent_subscriptions": sum(
                len(subs) for subs in self._silent_subscriptions.values()
            ),
            "devices_with_subscriptions": len(
                set(self._subscriptions.keys()) | set(self._silent_subscriptions.keys())
            ),
        }
