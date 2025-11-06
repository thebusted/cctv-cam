# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CCTV Face Recognition and Building Management System with real-time face recognition, person counting, and IoT integration.

**Tech Stack**: Python, FastAPI, YOLO11n, ArcFace, TimescaleDB, Redis, Docker

## Project Status

**Phase 1: Face Recognition Service - IMPLEMENTED ✅**

The Face Recognition Service is fully implemented with:
- RTSP stream processing (3264x1840 @ 30 FPS)
- YOLO11n person detection + YOLO-Face detection
- ArcFace embeddings (512-dim) with voting mechanism (60% threshold)
- Multi-frame verification (3 frames, 1 second apart)
- Redis Streams + Pub/Sub integration
- Prometheus metrics + structured logging
- Docker deployment with GPU support

**Next Phases - TODO:**
- Person Counting Service
- 6 IoT Adapter Services (HVAC, Pump, Lighting, Gate, Lift, Power)
- Auth Service (JWT + Redis Session)
- User Management Service
- Alert Service
- WebSocket Service
- Database schema implementation
- Frontend dashboard

## Development Workflow

### Quick Start
```bash
# 1. Download models (see QUICKSTART.md)
# 2. Configure environment
cp .env.example .env
# Edit RTSP_URL_CAMERA_01 in .env

# 3. Start services
docker-compose up -d

# 4. Check health
curl http://localhost:8003/health
```

### Local Development (Face Recognition Service)
```bash
cd services/face-recognition

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit RTSP_URL and other settings

# Run service
python -m uvicorn src.main:app --reload --port 8003
```

### Testing
```bash
# Unit tests (TODO)
pytest services/face-recognition/tests/

# Integration tests (TODO)
pytest tests/integration/
```

### Build & Deploy
```bash
# Build specific service
docker-compose build face-recognition

# Deploy with GPU support
docker-compose up -d face-recognition

# View logs
docker-compose logs -f face-recognition
```

## Architecture

### Microservices Architecture (13 services planned)

**Implemented:**
1. ✅ Face Recognition Service (`services/face-recognition/`)

**Planned:**
2. ⏳ Person Counting Service
3. ⏳ Auth Service
4. ⏳ User Management Service
5. ⏳ Alert Service
6-11. ⏳ IoT Adapters (6 systems)
12. ⏳ WebSocket Service
13. ⏳ API Gateway

### Data Flow

```
RTSP Camera (3264x1840)
  ↓
Face Recognition Service
  ├─ Person Detection (YOLO11n) → Redis Stream → Person Counting Service
  └─ Face Recognition (ArcFace) → Redis Stream → TimescaleDB
                                 ↓
                            Redis Pub/Sub → WebSocket → Frontend
```

### Technology Stack

- **Backend**: Python 3.10, FastAPI
- **AI/ML**: YOLO11n, YOLO-Face, ArcFace (InsightFace)
- **Database**: TimescaleDB (PostgreSQL + time-series)
- **Message Queue**: Redis Streams (reliable) + Pub/Sub (fast)
- **Monitoring**: Prometheus, Grafana, Loki
- **Deployment**: Docker Compose (not Kubernetes)

### Key Design Decisions

1. **Camera Resolution**: 3264x1840 for long-range cameras (configurable)
2. **Face Recognition Threshold**: 0.35 similarity, 60% voting
3. **Processing Frequency**: Face recognition every 30 frames (~1 second)
4. **Reliability**: Exponential backoff (30s → 300s), Redis buffering
5. **Monitoring**: Prometheus metrics on port 9003

## File Structure

```
cctv-cam/
├── services/
│   └── face-recognition/          # Face Recognition Service ✅
│       ├── src/
│       │   ├── main.py            # FastAPI app + processing loop
│       │   ├── rtsp_stream.py     # RTSP handler with reconnection
│       │   ├── detector.py        # YOLO detection
│       │   ├── recognizer.py      # ArcFace recognition
│       │   ├── voting.py          # Multi-frame verification
│       │   ├── redis_client.py    # Redis Streams + Pub/Sub
│       │   └── config.py          # Configuration
│       ├── models/                # Pre-trained models
│       ├── Dockerfile
│       ├── requirements.txt
│       └── README.md
├── docs/                          # Comprehensive documentation
│   ├── research/                  # Market research, YOLO research
│   ├── meetings/                  # Meeting notes (4 meetings)
│   └── planning/                  # System design recommendations
├── monitoring/                    # Prometheus, Grafana, Loki configs
├── docker-compose.yml             # Full stack deployment
├── QUICKSTART.md                  # Quick start guide
└── CLAUDE.md                      # This file
```

## Important Implementation Details

### Face Recognition Service (`services/face-recognition/`)

**Key Files:**
- `src/main.py`: Main FastAPI app with processing loop (see `processing_loop()` and `process_frame()`)
- `src/rtsp_stream.py`: Resilient RTSP handler with exponential backoff (see `ResilientRTSPStream`)
- `src/recognizer.py`: ArcFace recognition with voting (see `recognize_face()`)
- `src/voting.py`: Multi-frame verification (see `verify_identity()`)

**Configuration:**
- All settings in `src/config.py` (loaded from `.env`)
- Camera RTSP URL: Required environment variable `RTSP_URL`
- Resolution: Set via `CAMERA_RESOLUTION` (default: 3264x1840)

**Metrics Endpoints:**
- Health: `GET /health`
- Status: `GET /status`
- Metrics: `GET /metrics` (Prometheus format)

**Database Integration:**
- Currently uses in-memory cache for registered persons
- TODO: Implement TimescaleDB integration (see Meeting 3 docs)

## Testing Strategy

**Current Status**: No tests implemented yet

**TODO:**
- Unit tests for each module (detector, recognizer, voting)
- Integration tests for RTSP stream handling
- E2E tests for face recognition pipeline
- Performance tests (FPS, latency benchmarks)

## Security Considerations

**Implemented:**
- Non-root Docker user
- Environment-based secrets management
- Structured logging (no sensitive data in logs)

**TODO:**
- JWT + Redis Session authentication (Auth Service)
- Row-Level Security (RLS) in database
- SSL/TLS for RTSP streams
- API rate limiting
- Audit logging

## Deployment

**Current**: Docker Compose (single-host)

**Production Considerations:**
- GPU requirement: NVIDIA CUDA-capable GPU
- Memory: Minimum 8GB RAM
- Storage: SSD recommended for TimescaleDB
- Network: Low latency to cameras (<100ms RTT)

**Scaling:**
- Horizontal: Add more Face Recognition Service instances (1 per camera)
- Vertical: Larger GPU for multiple cameras on single instance

## Documentation

**Comprehensive docs in `docs/` directory:**
- Market Research: Cost analysis (88k-116k THB Year 1)
- YOLO Research: Complete technical research on face recognition
- Meeting 1: Face Recognition decisions (3-5 photos, 0.35 threshold)
- Meeting 2: Person Counting vs Recognition
- Meeting 3: Database architecture (TimescaleDB + pgvector)
- Meeting 4: System architecture (13 microservices)

**Quick references:**
- QUICKSTART.md: Get running in 5 minutes
- services/face-recognition/README.md: Service-specific documentation

## Contributing

**Code Style:**
- Python: Follow PEP 8
- Docstrings: Google style
- Type hints: Required for all functions
- Logging: Use structlog with JSON format

**Before Committing:**
```bash
# Format
black services/face-recognition/src/

# Lint
pylint services/face-recognition/src/

# Type check
mypy services/face-recognition/src/
```

## Support & Issues

- Check logs: `docker-compose logs -f face-recognition`
- Review documentation in `docs/` directory
- See troubleshooting in QUICKSTART.md
- Create GitHub issue with logs and configuration
