"""
Face Recognition Service - Main Application

FastAPI service for real-time face recognition from RTSP streams.

Features:
- RTSP stream processing (3264x1840 @ 30 FPS)
- YOLO11n person detection + YOLO-Face detection
- ArcFace embeddings (512-dim) with voting mechanism
- Multi-frame verification
- Redis Streams for event publishing
- Prometheus metrics
"""
import asyncio
import cv2
import structlog
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, List, Optional
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi.responses import Response

from .config import settings
from .rtsp_stream import ResilientRTSPStream
from .detector import FacePersonDetector
from .recognizer import ArcFaceRecognizer
from .voting import MultiFrameVerifier
from .redis_client import RedisClient

# Setup structured logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

# ==================== Prometheus Metrics ====================

# Camera metrics
camera_status = Gauge(
    "camera_status",
    "Camera online status (1=online, 0=offline)",
    ["camera_id"],
)

frames_processed = Counter(
    "frames_processed_total",
    "Total frames processed",
    ["camera_id"],
)

# Detection metrics
persons_detected = Counter(
    "persons_detected_total",
    "Total persons detected",
    ["camera_id"],
)

faces_detected = Counter(
    "faces_detected_total",
    "Total faces detected",
    ["camera_id"],
)

faces_recognized = Counter(
    "faces_recognized_total",
    "Total faces recognized",
    ["camera_id", "person_id"],
)

# Performance metrics
frame_processing_latency = Histogram(
    "frame_processing_latency_seconds",
    "Frame processing latency",
    ["camera_id"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

face_detection_latency = Histogram(
    "face_detection_latency_seconds",
    "Face detection processing time",
    ["camera_id"],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0],
)

face_recognition_latency = Histogram(
    "face_recognition_latency_seconds",
    "Face recognition processing time",
    ["camera_id"],
    buckets=[0.1, 0.2, 0.5, 1.0, 2.0],
)

# ==================== Global State ====================

class ServiceState:
    """Global service state"""

    def __init__(self):
        self.rtsp_stream: Optional[ResilientRTSPStream] = None
        self.detector: Optional[FacePersonDetector] = None
        self.recognizer: Optional[ArcFaceRecognizer] = None
        self.verifier: Optional[MultiFrameVerifier] = None
        self.redis_client: Optional[RedisClient] = None
        self.processing_task: Optional[asyncio.Task] = None
        self.running: bool = False

        # Database connection pool (placeholder)
        self.db_pool = None
        self.db_healthy: bool = True

        # Registered persons cache (placeholder - should load from DB)
        self.registered_persons: List[Dict] = []

        # Frame counter
        self.frame_counter: int = 0


state = ServiceState()


# ==================== Lifespan Management ====================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan manager"""
    # Startup
    logger.info("face_recognition_service_starting", version="0.1.0")

    try:
        # Initialize components
        await startup_event()

        yield

    finally:
        # Shutdown
        await shutdown_event()
        logger.info("face_recognition_service_stopped")


# ==================== FastAPI App ====================

app = FastAPI(
    title="Face Recognition Service",
    description="Real-time face recognition from RTSP streams",
    version="0.1.0",
    lifespan=lifespan,
)


# ==================== Startup / Shutdown ====================


async def startup_event():
    """Initialize service on startup"""
    logger.info("initializing_service")

    # 1. Connect to Redis
    state.redis_client = RedisClient()
    await state.redis_client.connect()

    # 2. Initialize RTSP Stream
    state.rtsp_stream = ResilientRTSPStream(
        camera_id=settings.CAMERA_ID,
        rtsp_url=settings.RTSP_URL,
        buffer_size=settings.FRAME_BUFFER_SIZE,
        initial_retry_delay=settings.RECONNECT_DELAY,
        max_retry_delay=settings.MAX_RECONNECT_DELAY,
    )
    state.rtsp_stream.start()

    # 3. Initialize Detector
    state.detector = FacePersonDetector(device="cuda:0")

    # 4. Initialize Recognizer
    state.recognizer = ArcFaceRecognizer(
        model_name=settings.FACE_RECOGNITION_MODEL,
        device="cuda",
    )

    # 5. Initialize Multi-frame Verifier
    state.verifier = MultiFrameVerifier()

    # 6. Load registered persons (placeholder)
    # TODO: Load from database
    state.registered_persons = []

    # 7. Start processing loop
    state.running = True
    state.processing_task = asyncio.create_task(processing_loop())

    logger.info("service_initialized")


async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("shutting_down_service")

    # Stop processing
    state.running = False

    if state.processing_task:
        state.processing_task.cancel()
        try:
            await state.processing_task
        except asyncio.CancelledError:
            pass

    # Stop RTSP stream
    if state.rtsp_stream:
        state.rtsp_stream.stop()

    # Disconnect Redis
    if state.redis_client:
        await state.redis_client.disconnect()

    logger.info("shutdown_complete")


# ==================== Processing Loop ====================


async def processing_loop():
    """
    Main processing loop

    Flow:
    1. Read frame from RTSP stream
    2. Detect persons (every frame) for counting
    3. Detect faces (every 30 frames) for recognition
    4. Extract embeddings and recognize faces
    5. Verify across multiple frames
    6. Publish events to Redis
    """
    logger.info("processing_loop_started")

    while state.running:
        try:
            await asyncio.sleep(0.001)  # Small sleep to prevent CPU spinning

            # Read frame
            ret, frame = state.rtsp_stream.read_frame()

            if not ret or frame is None:
                camera_status.labels(camera_id=settings.CAMERA_ID).set(0)
                await asyncio.sleep(0.1)
                continue

            camera_status.labels(camera_id=settings.CAMERA_ID).set(1)
            state.frame_counter += 1

            # Process frame
            start_time = asyncio.get_event_loop().time()
            await process_frame(frame, state.frame_counter)
            elapsed = asyncio.get_event_loop().time() - start_time

            frame_processing_latency.labels(camera_id=settings.CAMERA_ID).observe(elapsed)
            frames_processed.labels(camera_id=settings.CAMERA_ID).inc()

        except Exception as e:
            logger.error("processing_loop_error", error=str(e))
            await asyncio.sleep(1.0)


async def process_frame(frame: np.ndarray, frame_number: int):
    """
    Process a single frame

    Args:
        frame: Input frame (BGR)
        frame_number: Frame number
    """
    # Always detect persons for counting (every frame)
    persons = state.detector.detect_persons(frame)
    persons_detected.labels(camera_id=settings.CAMERA_ID).inc(len(persons))

    # Publish person count
    await state.redis_client.publish_person_count(
        {
            "camera_id": settings.CAMERA_ID,
            "timestamp": datetime.now().isoformat(),
            "count": len(persons),
            "frame_number": frame_number,
        }
    )

    # Face recognition (every N frames)
    if frame_number % settings.PROCESS_EVERY_N_FRAMES != 0:
        return

    # Detect faces
    detection_start = asyncio.get_event_loop().time()
    faces = state.detector.detect_faces(frame)
    detection_elapsed = asyncio.get_event_loop().time() - detection_start

    face_detection_latency.labels(camera_id=settings.CAMERA_ID).observe(detection_elapsed)
    faces_detected.labels(camera_id=settings.CAMERA_ID).inc(len(faces))

    if len(faces) == 0:
        return

    # Process each detected face
    for face in faces:
        await process_face(frame, face, frame_number)


async def process_face(frame: np.ndarray, face, frame_number: int):
    """
    Process a detected face

    Args:
        frame: Input frame (BGR)
        face: Face detection
        frame_number: Frame number
    """
    try:
        # Crop face
        face_crop = state.detector.crop_face(frame, face)

        # Extract embedding
        recognition_start = asyncio.get_event_loop().time()
        embedding_result = state.recognizer.extract_embedding(face_crop)

        if embedding_result is None:
            logger.warning("embedding_extraction_failed", frame=frame_number)
            return

        # Recognize face
        if len(state.registered_persons) == 0:
            # No registered persons - skip recognition
            logger.debug("no_registered_persons")
            return

        result = state.recognizer.recognize_face(
            query_embedding=embedding_result.embedding,
            registered_embeddings=state.registered_persons,
        )

        recognition_elapsed = asyncio.get_event_loop().time() - recognition_start
        face_recognition_latency.labels(camera_id=settings.CAMERA_ID).observe(
            recognition_elapsed
        )

        # Log recognition result
        logger.info(
            "face_recognized",
            frame=frame_number,
            person_id=result.person_id,
            decision=result.decision,
            similarity=result.similarity,
            vote_percentage=result.vote_percentage,
        )

        # TODO: Add multi-frame verification
        # tracking_id = generate_tracking_id(face)
        # state.verifier.add_verification(tracking_id, result)
        # verified_result = state.verifier.verify_identity(tracking_id)

        # Publish face event
        if result.decision == "MATCH":
            faces_recognized.labels(
                camera_id=settings.CAMERA_ID, person_id=result.person_id or "unknown"
            ).inc()

            event_data = {
                "camera_id": settings.CAMERA_ID,
                "timestamp": datetime.now().isoformat(),
                "frame_number": frame_number,
                "person_id": result.person_id,
                "full_name": result.full_name,
                "similarity": result.similarity,
                "vote_percentage": result.vote_percentage,
                "decision": result.decision,
                "bbox": face.bbox,
            }

            # Try to publish to stream
            try:
                await state.redis_client.publish_face_event(event_data)

                # Also broadcast via Pub/Sub for real-time updates
                await state.redis_client.publish_face_detection(event_data)

            except Exception as e:
                logger.error("event_publish_failed", error=str(e))

                # Fallback: use buffer
                await state.redis_client.publish_face_event(event_data, use_buffer=True)

    except Exception as e:
        logger.error("face_processing_error", error=str(e), frame=frame_number)


# ==================== API Endpoints ====================


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_healthy = await state.redis_client.health_check() if state.redis_client else False

    return JSONResponse(
        {
            "status": "healthy" if state.running else "unhealthy",
            "service": settings.SERVICE_NAME,
            "camera_id": settings.CAMERA_ID,
            "camera_connected": state.rtsp_stream.connected if state.rtsp_stream else False,
            "redis_connected": redis_healthy,
            "frames_processed": state.frame_counter,
        }
    )


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    ready = (
        state.running
        and state.rtsp_stream is not None
        and state.rtsp_stream.connected
        and state.redis_client is not None
    )

    if ready:
        return JSONResponse({"status": "ready"})
    else:
        raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/status")
async def get_status():
    """Get detailed service status"""
    stream_status = state.rtsp_stream.get_status() if state.rtsp_stream else {}
    verifier_status = state.verifier.get_status() if state.verifier else {}

    buffer_size = (
        await state.redis_client.get_buffer_size() if state.redis_client else 0
    )

    return JSONResponse(
        {
            "service": settings.SERVICE_NAME,
            "running": state.running,
            "camera": stream_status,
            "verifier": verifier_status,
            "registered_persons": len(state.registered_persons),
            "buffer_size": buffer_size,
            "frame_counter": state.frame_counter,
        }
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type="text/plain")


@app.post("/sync-buffer")
async def sync_buffer():
    """Manually sync buffered events to main stream"""
    if not state.redis_client:
        raise HTTPException(status_code=503, detail="Redis not connected")

    count = await state.redis_client.sync_buffer_to_stream()

    return JSONResponse({"synced": count})


# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
    )
