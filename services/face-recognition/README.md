# Face Recognition Service

Real-time face recognition service using ArcFace embeddings with voting mechanism.

## Features

- **RTSP Stream Processing**: Handles high-resolution streams (3264x1840 @ 30 FPS)
- **Person Detection**: YOLO11n for fast person detection (30-40 FPS)
- **Face Detection**: YOLO-Face for accurate face detection
- **Face Recognition**: ArcFace embeddings (512-dim, 99.82% accuracy on LFW)
- **Voting Mechanism**: 60% of embeddings must agree for positive match
- **Multi-frame Verification**: Verify across 3 frames, 1 second apart
- **Resilient Connection**: Exponential backoff reconnection (30s → 300s max)
- **Redis Integration**: Streams for reliable events, Pub/Sub for real-time notifications
- **Prometheus Metrics**: Full observability with metrics export

## Architecture

```
RTSP Stream (3264x1840)
    ↓
Person Detection (YOLO11n) → Person Count → Redis Stream
    ↓
Face Detection (YOLO-Face) (every 30 frames)
    ↓
Face Recognition (ArcFace)
    ↓
Voting Mechanism (60% threshold)
    ↓
Multi-frame Verification (3 frames)
    ↓
Redis Stream + Pub/Sub → WebSocket → Frontend
```

## Technical Specifications

### Face Recognition

- **Model**: InsightFace buffalo_l
- **Accuracy**: 99.82% on LFW benchmark
- **Embedding Dimension**: 512
- **Similarity Threshold**: 0.35 (configurable)
- **Voting Threshold**: 60% of embeddings must agree

### Processing

- **Person Detection**: Every frame (30-40 FPS)
- **Face Recognition**: Every 30 frames (~1 second)
- **Minimum Face Size**: 80x80 pixels
- **Multi-frame Verification**: 3 frames, 1 second apart

### Reliability

- **Camera Offline**: Exponential backoff (30s → 45s → 67s → ... → 300s)
- **Alert Escalation**: Warning at 3 attempts, Critical at 10 attempts
- **Database Outage**: Redis buffering (max 10,000 events)

## Installation

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended)
- Redis
- TimescaleDB (optional, for persistence)

### Setup

1. **Clone repository**:
```bash
git clone <repository-url>
cd services/face-recognition
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Download models**:
```bash
# YOLO11n (person detection)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11n.pt -P models/

# YOLO-Face (face detection)
wget https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov8n-face.pt -P models/

# ArcFace model will be downloaded automatically on first run
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings (especially RTSP_URL)
```

5. **Run service**:
```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8003
```

## Docker Deployment

### Build Image

```bash
docker build -t face-recognition-service:latest .
```

### Run Container

```bash
docker run -d \
  --name face-recognition \
  --gpus all \
  -p 8003:8003 \
  -p 9003:9003 \
  --env-file .env \
  face-recognition-service:latest
```

### Docker Compose

See `docker-compose.yml` in the project root for full stack deployment.

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "face-recognition-service",
  "camera_id": "camera_01",
  "camera_connected": true,
  "redis_connected": true,
  "frames_processed": 12345
}
```

### Readiness Check

```bash
GET /ready
```

### Service Status

```bash
GET /status
```

Response:
```json
{
  "service": "face-recognition-service",
  "running": true,
  "camera": {
    "camera_id": "camera_01",
    "connected": true,
    "frame_count": 12345,
    "error_count": 0,
    "retry_count": 0
  },
  "verifier": {
    "active_tracks": 3,
    "verification_frames": 3
  },
  "registered_persons": 150,
  "buffer_size": 0
}
```

### Prometheus Metrics

```bash
GET /metrics
```

## Configuration

### Key Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `RTSP_URL` | - | RTSP stream URL (required) |
| `CAMERA_RESOLUTION` | 3264x1840 | Camera resolution |
| `SIMILARITY_THRESHOLD` | 0.35 | Face similarity threshold |
| `VOTING_THRESHOLD` | 0.60 | Voting mechanism threshold (60%) |
| `MIN_FACE_SIZE` | 80 | Minimum face size (pixels) |
| `VERIFICATION_FRAMES` | 3 | Multi-frame verification count |
| `PROCESS_EVERY_N_FRAMES` | 30 | Face recognition interval |

### Camera Resolution Selection

For **long-range cameras** (>10 meters):
- ✅ Use **3264x1840** for clear face recognition
- ❌ Avoid 768x432 unless faces are large enough (>80x80 pixels)

For **close-range cameras** (<5 meters):
- ✅ Use **768x432** for better performance
- 30-40 FPS achievable

## Monitoring

### Prometheus Metrics

- `camera_status`: Camera online status (1=online, 0=offline)
- `frames_processed_total`: Total frames processed
- `persons_detected_total`: Total persons detected
- `faces_detected_total`: Total faces detected
- `faces_recognized_total`: Total faces recognized (by person_id)
- `frame_processing_latency_seconds`: Frame processing latency
- `face_detection_latency_seconds`: Face detection latency
- `face_recognition_latency_seconds`: Face recognition latency

### Example Prometheus Queries

**Average frame processing time (last 5 minutes)**:
```promql
rate(frame_processing_latency_seconds_sum[5m]) / rate(frame_processing_latency_seconds_count[5m])
```

**Face recognition rate (per minute)**:
```promql
rate(faces_recognized_total[1m]) * 60
```

## Troubleshooting

### Camera Not Connecting

1. Check RTSP URL format:
```bash
rtsp://username:password@camera-ip:554/stream1
```

2. Test RTSP stream:
```bash
ffplay rtsp://username:password@camera-ip:554/stream1
```

3. Check logs:
```bash
docker logs face-recognition
```

### Low FPS

1. Reduce resolution (768x432)
2. Increase `PROCESS_EVERY_N_FRAMES` (e.g., 60)
3. Check GPU availability:
```python
import torch
print(torch.cuda.is_available())
```

### Face Not Recognized

1. Check minimum face size (must be ≥80x80 pixels)
2. Lower similarity threshold (e.g., 0.30)
3. Check registered person embeddings in database
4. Review logs for quality scores

## Development

### Project Structure

```
services/face-recognition/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + processing loop
│   ├── config.py            # Configuration
│   ├── rtsp_stream.py       # RTSP handler
│   ├── detector.py          # YOLO detection
│   ├── recognizer.py        # ArcFace recognition
│   ├── voting.py            # Multi-frame verification
│   └── redis_client.py      # Redis integration
├── models/                  # Pre-trained models
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Linting
pylint src/

# Formatting
black src/

# Type checking
mypy src/
```

## License

See project root LICENSE file.

## References

- [YOLO11 Documentation](https://docs.ultralytics.com/)
- [InsightFace](https://github.com/deepinsight/insightface)
- [ArcFace Paper](https://arxiv.org/abs/1801.07698)
