# Quick Start Guide - CCTV Face Recognition System

Get the Face Recognition Service running in **5 minutes**!

## Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with CUDA support
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- RTSP camera stream URL

## Step 1: Download Models

Download pre-trained models before starting:

```bash
# Create models directory
mkdir -p services/face-recognition/models

# Download YOLO11n (person detection)
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolo11n.pt \
  -O services/face-recognition/models/yolo11n.pt

# Download YOLO-Face (face detection)
wget https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov8n-face.pt \
  -O services/face-recognition/models/yolov8n-face.pt
```

**Note**: ArcFace model (`buffalo_l`) will be downloaded automatically on first run.

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set your RTSP URL
nano .env
```

**Required: Update your camera RTSP URL**:
```bash
RTSP_URL_CAMERA_01=rtsp://username:password@192.168.1.100:554/stream1
```

**Format Examples**:
```bash
# Dahua
rtsp://admin:password@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0

# Hikvision
rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101

# Generic
rtsp://admin:password@192.168.1.100:554/stream1
```

## Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f face-recognition
```

## Step 4: Verify

### Check Health
```bash
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "camera_id": "camera_01",
  "camera_connected": true,
  "redis_connected": true,
  "frames_processed": 123
}
```

### View Metrics
```bash
curl http://localhost:8003/metrics
```

### Access Grafana
Open browser: http://localhost:3000

- Username: `admin`
- Password: `admin` (change in `.env`)

### Access Prometheus
Open browser: http://localhost:9090

## Architecture Overview

```
┌─────────────────┐
│   RTSP Camera   │ (3264x1840 @ 30 FPS)
│  192.168.1.100  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│   Face Recognition Service (GPU)        │
│  - YOLO11n (Person Detection)           │
│  - YOLO-Face (Face Detection)           │
│  - ArcFace (Face Recognition)           │
│  - Voting Mechanism (60% threshold)     │
└────────┬────────────────────────────────┘
         │
         ▼
┌────────────────┐     ┌──────────────┐
│  Redis Streams │────▶│ TimescaleDB  │
│    + Pub/Sub   │     │  (Storage)   │
└────────────────┘     └──────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│  Monitoring Stack                      │
│  - Prometheus (Metrics)                │
│  - Grafana (Dashboards)                │
│  - Loki (Logs)                         │
└────────────────────────────────────────┘
```

## Troubleshooting

### Camera Not Connecting

**Check RTSP URL**:
```bash
# Test with FFmpeg
docker run --rm -it jrottenberg/ffmpeg:latest \
  -rtsp_transport tcp \
  -i "rtsp://username:password@192.168.1.100:554/stream1" \
  -frames:v 1 -f image2 - > test.jpg
```

**Check logs**:
```bash
docker-compose logs face-recognition | grep rtsp
```

### GPU Not Available

**Check NVIDIA runtime**:
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**If GPU not detected**:
1. Install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
2. Restart Docker daemon
3. Verify: `nvidia-smi`

### Low FPS / High Latency

**Option 1: Use Lower Resolution**
- Edit `.env`: Change camera stream to 768x432
- Restart: `docker-compose restart face-recognition`

**Option 2: Reduce Processing Frequency**
- Edit `services/face-recognition/.env`
- Change `PROCESS_EVERY_N_FRAMES=30` to `60` (process every 2 seconds)

### Memory Issues

**Reduce Redis Memory**:
```yaml
# In docker-compose.yml
redis:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

**Reduce Buffer Size**:
```bash
# In .env
MAX_BUFFER_SIZE=5000
```

## Next Steps

1. **Register Persons**: Add faces to database (see Database Schema docs)
2. **Configure Alerts**: Set up alert rules in Prometheus
3. **Create Dashboards**: Import Grafana dashboards
4. **Add More Cameras**: Scale to 4 cameras (see Scaling docs)
5. **Integrate IoT**: Connect HVAC, Gates, etc. (see IoT Integration docs)

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f face-recognition

# Restart service
docker-compose restart face-recognition

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build face-recognition

# Check resource usage
docker stats
```

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| Face Recognition API | http://localhost:8003 | Main service |
| Health Check | http://localhost:8003/health | Health status |
| Metrics | http://localhost:8003/metrics | Prometheus metrics |
| Prometheus | http://localhost:9090 | Metrics database |
| Grafana | http://localhost:3000 | Dashboards |
| TimescaleDB | localhost:5432 | Database |
| Redis | localhost:6379 | Message queue |

## Support

- Documentation: See `docs/` directory
- Issues: Create GitHub issue
- Logs: Check `docker-compose logs`

## Configuration Reference

### Key Settings (in `.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `RTSP_URL_CAMERA_01` | - | Camera RTSP URL (**required**) |
| `DB_PASSWORD` | postgres | Database password |
| `GRAFANA_USER` | admin | Grafana username |
| `GRAFANA_PASSWORD` | admin | Grafana password |

### Advanced Settings (in `services/face-recognition/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CAMERA_RESOLUTION` | 3264x1840 | Camera resolution |
| `SIMILARITY_THRESHOLD` | 0.35 | Face matching threshold |
| `VOTING_THRESHOLD` | 0.60 | Voting mechanism (60%) |
| `MIN_FACE_SIZE` | 80 | Minimum face size (pixels) |
| `PROCESS_EVERY_N_FRAMES` | 30 | Recognition interval |
| `VERIFICATION_FRAMES` | 3 | Multi-frame verification |

---

**You're all set! 🎉**

The system is now processing video streams and ready for face recognition.
