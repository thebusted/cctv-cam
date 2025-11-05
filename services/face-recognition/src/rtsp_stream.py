"""
RTSP Stream Handler with Resilient Connection Management

Handles RTSP stream from cameras with:
- Exponential backoff reconnection
- Frame buffering
- Thread-safe operations
- Error handling and recovery
"""
import cv2
import asyncio
import structlog
from threading import Thread, Lock
from typing import Optional, Tuple
from datetime import datetime
from .config import settings

logger = structlog.get_logger()


class RTSPStreamError(Exception):
    """RTSP Stream specific errors"""
    pass


class ResilientRTSPStream:
    """
    Resilient RTSP Stream Handler with exponential backoff

    Features:
    - Automatic reconnection with exponential backoff (30s → 300s max)
    - Thread-safe frame access
    - Error counting and alerting
    - Connection status tracking
    """

    def __init__(
        self,
        camera_id: str,
        rtsp_url: str,
        buffer_size: int = 2,
        initial_retry_delay: int = 30,
        max_retry_delay: int = 300,
    ):
        """
        Initialize RTSP Stream Handler

        Args:
            camera_id: Unique camera identifier
            rtsp_url: RTSP stream URL
            buffer_size: Frame buffer size (default: 2)
            initial_retry_delay: Initial reconnection delay in seconds (default: 30)
            max_retry_delay: Maximum reconnection delay in seconds (default: 300)
        """
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.buffer_size = buffer_size
        self.retry_delay = initial_retry_delay
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay

        # Connection state
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[any] = None
        self.frame_lock = Lock()
        self.running = False
        self.connected = False

        # Statistics
        self.frame_count = 0
        self.error_count = 0
        self.retry_count = 0
        self.last_frame_time: Optional[datetime] = None
        self.connection_start_time: Optional[datetime] = None

        # Thread
        self.capture_thread: Optional[Thread] = None

        logger.info(
            "rtsp_stream_initialized",
            camera_id=camera_id,
            resolution=settings.CAMERA_RESOLUTION,
            rtsp_url=rtsp_url[:50] + "..." if len(rtsp_url) > 50 else rtsp_url,
        )

    def connect(self) -> bool:
        """
        Connect to RTSP stream

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            logger.info("connecting_to_rtsp", camera_id=self.camera_id)

            self.cap = cv2.VideoCapture(self.rtsp_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)

            # Test connection by reading one frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise RTSPStreamError("Failed to read initial frame")

            self.connected = True
            self.connection_start_time = datetime.now()
            self.retry_count = 0
            self.retry_delay = self.initial_retry_delay  # Reset delay on success

            # Get stream properties
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.cap.get(cv2.CAP_PROP_FPS)

            logger.info(
                "rtsp_connected",
                camera_id=self.camera_id,
                width=width,
                height=height,
                fps=fps,
            )

            return True

        except Exception as e:
            self.connected = False
            logger.error(
                "rtsp_connection_failed",
                camera_id=self.camera_id,
                error=str(e),
                retry_count=self.retry_count,
            )
            return False

    def start(self):
        """Start capture thread"""
        if self.running:
            logger.warning("capture_already_running", camera_id=self.camera_id)
            return

        self.running = True
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        logger.info("capture_thread_started", camera_id=self.camera_id)

    def stop(self):
        """Stop capture thread and release resources"""
        self.running = False

        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)

        self._release_capture()

        logger.info(
            "capture_stopped",
            camera_id=self.camera_id,
            total_frames=self.frame_count,
            total_errors=self.error_count,
        )

    def _capture_loop(self):
        """Main capture loop with automatic reconnection"""
        while self.running:
            try:
                # Connect if not connected
                if not self.connected:
                    if not self.connect():
                        self._handle_connection_failure()
                        continue

                # Read frame
                ret, frame = self.cap.read()

                if not ret or frame is None:
                    raise RTSPStreamError("Failed to read frame")

                # Update frame (thread-safe)
                with self.frame_lock:
                    self.frame = frame
                    self.frame_count += 1
                    self.last_frame_time = datetime.now()

                # Reset error count on successful read
                if self.error_count > 0:
                    logger.info(
                        "stream_recovered",
                        camera_id=self.camera_id,
                        previous_errors=self.error_count,
                    )
                    self.error_count = 0

            except Exception as e:
                self.error_count += 1
                self.connected = False

                logger.error(
                    "frame_read_error",
                    camera_id=self.camera_id,
                    error=str(e),
                    error_count=self.error_count,
                )

                self._release_capture()
                self._handle_connection_failure()

    def _handle_connection_failure(self):
        """
        Handle connection failure with exponential backoff

        Exponential backoff: 30s → 45s → 67s → 101s → 151s → 227s → 300s (max)
        Alert escalation: Warning at 3 attempts, Critical at 10 attempts
        """
        self.retry_count += 1

        # TODO: Send alerts via Redis Pub/Sub
        if self.retry_count == 3:
            logger.warning(
                "camera_offline_warning",
                camera_id=self.camera_id,
                retry_count=self.retry_count,
                message=f"Camera {self.camera_id} offline for 3 attempts",
            )
        elif self.retry_count == 10:
            logger.critical(
                "camera_offline_critical",
                camera_id=self.camera_id,
                retry_count=self.retry_count,
                message=f"Camera {self.camera_id} CRITICAL - offline for 10 attempts",
            )

        # Exponential backoff: delay *= 1.5
        import time
        time.sleep(self.retry_delay)
        self.retry_delay = min(int(self.retry_delay * 1.5), self.max_retry_delay)

        logger.info(
            "retry_scheduled",
            camera_id=self.camera_id,
            retry_count=self.retry_count,
            next_retry_delay=self.retry_delay,
        )

    def _release_capture(self):
        """Release video capture resources"""
        if self.cap:
            self.cap.release()
            self.cap = None

    def read_frame(self) -> Tuple[bool, Optional[any]]:
        """
        Read the latest frame (thread-safe)

        Returns:
            Tuple[bool, Optional[np.ndarray]]: (success, frame)
        """
        with self.frame_lock:
            if self.frame is not None:
                return True, self.frame.copy()
            return False, None

    def get_status(self) -> dict:
        """
        Get current stream status

        Returns:
            dict: Status information
        """
        return {
            "camera_id": self.camera_id,
            "connected": self.connected,
            "running": self.running,
            "frame_count": self.frame_count,
            "error_count": self.error_count,
            "retry_count": self.retry_count,
            "last_frame_time": self.last_frame_time.isoformat() if self.last_frame_time else None,
            "connection_start_time": self.connection_start_time.isoformat()
            if self.connection_start_time
            else None,
            "current_retry_delay": self.retry_delay,
        }
