"""
Redis Client for Streams and Pub/Sub

Handles:
- Redis Streams for reliable message passing (face events, video frames)
- Redis Pub/Sub for fast broadcasting (alerts, notifications)
- Buffering during database outages
"""
import json
import asyncio
import structlog
from typing import Dict, Optional, List, Any
from redis import asyncio as aioredis
from .config import settings

logger = structlog.get_logger()


class RedisClient:
    """
    Redis Client for Face Recognition Service

    Features:
    - Redis Streams for face events and video frames
    - Redis Pub/Sub for alerts and notifications
    - Automatic buffering during database outages
    - Connection pooling
    """

    def __init__(self):
        """Initialize Redis Client"""
        self.redis: Optional[aioredis.Redis] = None
        self.pubsub: Optional[aioredis.client.PubSub] = None

        # Stream names
        self.face_events_stream = settings.FACE_EVENTS_STREAM
        self.person_count_stream = settings.PERSON_COUNT_STREAM
        self.video_frames_stream = settings.VIDEO_FRAMES_STREAM
        self.buffer_stream = settings.BUFFER_STREAM

        # Pub/Sub channels
        self.alerts_channel = settings.ALERTS_CHANNEL
        self.face_detection_channel = settings.FACE_DETECTION_CHANNEL

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            logger.info(
                "connecting_to_redis",
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
            )

            self.redis = await aioredis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=False,  # Keep as bytes for binary data
                max_connections=20,
            )

            # Test connection
            await self.redis.ping()

            logger.info("redis_connected")

        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("redis_disconnected")

    # ==================== Streams ====================

    async def publish_face_event(
        self,
        event_data: Dict[str, Any],
        use_buffer: bool = False,
    ) -> Optional[str]:
        """
        Publish face recognition event to Redis Stream

        Args:
            event_data: Event data dictionary
            use_buffer: Use buffer stream (for database outage)

        Returns:
            str: Message ID or None if failed
        """
        try:
            stream_name = self.buffer_stream if use_buffer else self.face_events_stream

            # Serialize data
            data = {"data": json.dumps(event_data)}

            # Add to stream with max length limit
            message_id = await self.redis.xadd(
                stream_name,
                data,
                maxlen=settings.MAX_BUFFER_SIZE if use_buffer else 100000,
            )

            logger.debug(
                "face_event_published",
                stream=stream_name,
                message_id=message_id.decode() if isinstance(message_id, bytes) else message_id,
                person_id=event_data.get("person_id"),
            )

            return message_id.decode() if isinstance(message_id, bytes) else message_id

        except Exception as e:
            logger.error("face_event_publish_failed", error=str(e))
            return None

    async def publish_person_count(
        self,
        count_data: Dict[str, Any],
    ) -> Optional[str]:
        """
        Publish person count data to Redis Stream

        Args:
            count_data: Count data dictionary

        Returns:
            str: Message ID or None if failed
        """
        try:
            data = {"data": json.dumps(count_data)}

            message_id = await self.redis.xadd(
                self.person_count_stream,
                data,
                maxlen=100000,
            )

            logger.debug(
                "person_count_published",
                message_id=message_id.decode() if isinstance(message_id, bytes) else message_id,
                camera_id=count_data.get("camera_id"),
                count=count_data.get("count"),
            )

            return message_id.decode() if isinstance(message_id, bytes) else message_id

        except Exception as e:
            logger.error("person_count_publish_failed", error=str(e))
            return None

    async def consume_stream(
        self,
        stream_name: str,
        consumer_group: str,
        consumer_name: str,
        count: int = 10,
        block: int = 1000,
    ) -> List[Dict]:
        """
        Consume messages from Redis Stream

        Args:
            stream_name: Stream name
            consumer_group: Consumer group name
            consumer_name: Consumer name
            count: Number of messages to read
            block: Block time in milliseconds

        Returns:
            List[Dict]: List of messages
        """
        try:
            # Create consumer group if not exists
            try:
                await self.redis.xgroup_create(
                    stream_name,
                    consumer_group,
                    id="0",
                    mkstream=True,
                )
            except Exception:
                # Group already exists
                pass

            # Read messages
            messages = await self.redis.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_name: ">"},
                count=count,
                block=block,
            )

            parsed_messages = []
            for stream, msg_list in messages:
                for msg_id, data in msg_list:
                    try:
                        # Decode message
                        msg_data = json.loads(data[b"data"].decode())
                        parsed_messages.append(
                            {
                                "message_id": msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                                "data": msg_data,
                            }
                        )
                    except Exception as e:
                        logger.error("message_parse_failed", error=str(e))

            return parsed_messages

        except Exception as e:
            logger.error("stream_consume_failed", error=str(e))
            return []

    async def ack_message(
        self,
        stream_name: str,
        consumer_group: str,
        message_id: str,
    ) -> bool:
        """
        Acknowledge message in stream

        Args:
            stream_name: Stream name
            consumer_group: Consumer group name
            message_id: Message ID

        Returns:
            bool: Success
        """
        try:
            await self.redis.xack(stream_name, consumer_group, message_id)
            return True
        except Exception as e:
            logger.error("ack_failed", error=str(e))
            return False

    async def get_stream_info(self, stream_name: str) -> Optional[Dict]:
        """Get stream information"""
        try:
            info = await self.redis.xinfo_stream(stream_name)
            return info
        except Exception as e:
            logger.error("stream_info_failed", error=str(e))
            return None

    # ==================== Pub/Sub ====================

    async def publish_alert(
        self,
        alert_type: str,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        Publish alert to Pub/Sub channel

        Args:
            alert_type: Alert type ('info', 'warning', 'critical')
            message: Alert message
            metadata: Additional metadata
        """
        try:
            alert_data = {
                "type": alert_type,
                "message": message,
                "service": settings.SERVICE_NAME,
                "camera_id": settings.CAMERA_ID,
                "timestamp": str(asyncio.get_event_loop().time()),
                "metadata": metadata or {},
            }

            await self.redis.publish(
                self.alerts_channel,
                json.dumps(alert_data),
            )

            logger.info(
                "alert_published",
                type=alert_type,
                message=message,
            )

        except Exception as e:
            logger.error("alert_publish_failed", error=str(e))

    async def publish_face_detection(
        self,
        detection_data: Dict[str, Any],
    ) -> None:
        """
        Publish face detection event to Pub/Sub (real-time)

        Args:
            detection_data: Detection data dictionary
        """
        try:
            await self.redis.publish(
                self.face_detection_channel,
                json.dumps(detection_data),
            )

            logger.debug(
                "face_detection_broadcast",
                person_id=detection_data.get("person_id"),
            )

        except Exception as e:
            logger.error("face_detection_broadcast_failed", error=str(e))

    async def subscribe_channel(self, channel: str):
        """Subscribe to Pub/Sub channel"""
        try:
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(channel)

            logger.info("subscribed_to_channel", channel=channel)

            return self.pubsub

        except Exception as e:
            logger.error("subscribe_failed", error=str(e))
            return None

    # ==================== Buffering ====================

    async def get_buffer_size(self) -> int:
        """
        Get current buffer size

        Returns:
            int: Number of buffered events
        """
        try:
            length = await self.redis.xlen(self.buffer_stream)
            return length
        except Exception:
            return 0

    async def sync_buffer_to_stream(self) -> int:
        """
        Sync buffered events to main stream

        Returns:
            int: Number of events synced
        """
        try:
            # Get all buffered messages
            messages = await self.redis.xrange(self.buffer_stream)

            synced = 0
            for msg_id, data in messages:
                # Copy to main stream
                await self.redis.xadd(
                    self.face_events_stream,
                    data,
                    maxlen=100000,
                )

                # Remove from buffer
                await self.redis.xdel(self.buffer_stream, msg_id)

                synced += 1

            if synced > 0:
                logger.info("buffer_synced", count=synced)

            return synced

        except Exception as e:
            logger.error("buffer_sync_failed", error=str(e))
            return 0

    # ==================== Health Check ====================

    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False
