"""
Configuration for Face Recognition Service
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Face Recognition Service Configuration"""

    # Service
    SERVICE_NAME: str = "face-recognition-service"
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False

    # Camera Configuration
    RTSP_URL: str  # Must be provided via environment
    CAMERA_ID: str = "camera_01"
    CAMERA_RESOLUTION: str = "3264x1840"  # High resolution for long-range
    CAMERA_FPS: float = 29.97

    # Face Detection Settings
    FACE_DETECTION_MODEL: str = "yolov8n-face.pt"
    PERSON_DETECTION_MODEL: str = "yolo11n.pt"
    FACE_CONFIDENCE_THRESHOLD: float = 0.5
    PERSON_CONFIDENCE_THRESHOLD: float = 0.6

    # Face Recognition Settings
    FACE_RECOGNITION_MODEL: str = "buffalo_l"  # InsightFace model
    SIMILARITY_THRESHOLD: float = 0.35  # Lower threshold for better recall
    VOTING_THRESHOLD: float = 0.60  # 60% of embeddings must agree
    MIN_FACE_SIZE: int = 80  # Minimum face size in pixels (80x80)
    EMBEDDING_DIM: int = 512  # ArcFace embedding dimension

    # Multi-frame Verification
    VERIFICATION_FRAMES: int = 3  # Check 3 frames
    VERIFICATION_INTERVAL: float = 1.0  # 1 second apart

    # Processing Settings
    PROCESS_EVERY_N_FRAMES: int = 30  # Face recognition every 30 frames
    DETECTION_EVERY_N_FRAMES: int = 1  # Person detection every frame
    FRAME_BUFFER_SIZE: int = 2
    RECONNECT_DELAY: int = 30  # Start with 30 seconds
    MAX_RECONNECT_DELAY: int = 300  # Max 5 minutes

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Redis Streams
    FACE_EVENTS_STREAM: str = "stream:face_events"
    PERSON_COUNT_STREAM: str = "stream:person_count"
    VIDEO_FRAMES_STREAM: str = "stream:video_frames"
    BUFFER_STREAM: str = "buffer:face_events"
    MAX_BUFFER_SIZE: int = 10000

    # Redis Pub/Sub
    ALERTS_CHANNEL: str = "alerts"
    FACE_DETECTION_CHANNEL: str = "face_detected"

    # Database Configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cctv_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_POOL_MIN_SIZE: int = 5
    DB_POOL_MAX_SIZE: int = 20

    # Monitoring
    METRICS_PORT: int = 9003
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
