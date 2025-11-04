# Meeting Note 4: System Architecture & Integration Design
**Date:** November 4, 2025
**Topic:** Complete System Architecture for CCTV & Building Management System
**Duration:** 180 minutes (3 hours) - Interactive Technical Discussion
**Attendees:** Development Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Part 1: Overall Architecture](#2-part-1-overall-architecture)
   - 2.1 Architecture Pattern Selection
   - 2.2 Service Breakdown
   - 2.3 Communication Infrastructure
   - 2.4 Deployment Platform
3. [Part 2: API & Integration Design](#3-part-2-api--integration-design)
   - 3.1 Authentication Strategy
   - 3.2 REST API Specifications
   - 3.3 WebSocket Real-Time Communication
   - 3.4 IoT Integration Patterns
4. [Part 3: Reliability & Operations](#4-part-3-reliability--operations)
   - 4.1 Error Handling Strategy
   - 4.2 Monitoring & Observability
   - 4.3 Logging Infrastructure
   - 4.4 Health Checks & Circuit Breakers
5. [Part 4: DevOps & Deployment](#5-part-4-devops--deployment)
   - 5.1 Docker Compose Configuration
   - 5.2 Environment Management
   - 5.3 Deployment Strategy
   - 5.4 Backup & Security
6. [Implementation Roadmap](#6-implementation-roadmap)
7. [Resource Planning](#7-resource-planning)
8. [Next Steps](#8-next-steps)

---

## 1. Executive Summary

This meeting established the complete system architecture for the integrated CCTV and Building Management System, building upon the foundation laid in Meetings 1-3 (AI models, person counting, and database design).

### Key Decisions Made

**Architecture Pattern:**
- ✅ **Microservices Architecture** (13 independent services)
- ✅ **Docker Compose** for deployment (simple, cost-effective)
- ✅ **Nginx + FastAPI** hybrid API Gateway
- ✅ **Redis Hybrid** messaging (Streams for data, Pub/Sub for events)

**Communication Infrastructure:**
- ✅ **REST APIs** for synchronous operations (CRUD, queries)
- ✅ **WebSocket Native** (FastAPI built-in) for real-time updates
- ✅ **Redis Streams** for video frames and IoT data (reliable processing)
- ✅ **Redis Pub/Sub** for events and notifications (fast broadcasting)

**Reliability & Operations:**
- ✅ **Exponential backoff** for camera reconnection (30s → 300s max)
- ✅ **Redis buffering** for database outages (auto-sync when recovered)
- ✅ **Prometheus + Grafana** for monitoring (light setup: 0.5 vCPU, 500 MB)
- ✅ **Loki** for centralized logging (7 days hot + 30 days archive)
- ✅ **Circuit breakers** for IoT API resilience

**Integration Strategy:**
- ✅ **6 IoT Adapter Services** (HVAC, Pump, Lighting, Gate, Lift, Power)
- ✅ **Polling + Webhook** support (flexible integration)
- ✅ **Retry 3x with exponential backoff** → Alert on failure
- ✅ **No ETL tools** (Mage AI unnecessary for real-time streaming)

**Security & Authentication:**
- ✅ **JWT + Redis Session** hybrid (revocable tokens)
- ✅ **Role-based expiry**: Admin/Operator (3 hours), Viewer (7 days)
- ✅ **SSL/TLS** via Let's Encrypt
- ✅ **Internal network isolation** (services trust each other)

**Resource Optimization:**
- ✅ **Light monitoring setup** (reduce Prometheus footprint)
- ✅ **Future: Separate monitoring VPS** (300 THB/month for dedicated monitoring)
- ✅ **Docker resource limits** to prevent resource exhaustion

### Business Impact

**Operational Benefits:**
- **24/7 Reliability**: Auto-recovery, circuit breakers, health monitoring
- **Scalability**: Microservices can scale independently
- **Maintainability**: Clear service boundaries, standardized APIs
- **Observability**: Full metrics, logs, and tracing capabilities

**Cost Efficiency:**
- **Server Cost**: 2,000-2,500 THB/month (main server 4-6 vCPU, 8-12 GB RAM)
- **Optional Monitoring**: +300 THB/month (separate VPS for production)
- **Development Time**: 6-8 weeks (clear architecture reduces uncertainty)

**Technical Excellence:**
- Industry-standard patterns (microservices, REST, WebSocket)
- Battle-tested technologies (PostgreSQL, Redis, Docker)
- Production-ready from day one (monitoring, logging, backups)

---

## 2. Part 1: Overall Architecture

### 2.1 Architecture Pattern Selection

#### Decision: Microservices Architecture

**Context:** We evaluated 3 architectural patterns:

| Pattern | Pros | Cons | Verdict |
|---------|------|------|---------|
| **Monolithic** | Simple deployment, low latency | Hard to scale, single point of failure | ❌ Rejected |
| **Microservices** | Independent scaling, fault isolation, tech flexibility | More complex, network overhead | ✅ **Selected** |
| **Modular Monolith** | Balance of simplicity and modularity | Still limited scalability | ⚠️ Future migration path |

**Why Microservices?**

1. **6 IoT Systems Integration Requirement**
   - Each IoT system (HVAC, Pump, Lighting, Gate, Lift, Power) has different:
     - API patterns (REST, SOAP, custom protocols)
     - Sampling rates (1 min to 15 min)
     - Reliability characteristics (some APIs are more stable than others)
   - **Microservices allow independent adapters** for each system
   - If HVAC API is down, other systems continue working

2. **Small Server Philosophy**
   - User explicitly wanted "เซิฟเวอร์เล็ก ๆ แล้วให้เชื่อมข้อมูลเข้าหากัน"
   - Microservices = small, focused services
   - Can run on modest hardware (4-6 vCPU, 8-12 GB RAM)

3. **Scaling Flexibility**
   - Face Recognition (CPU/GPU intensive) can scale independently
   - Video Stream (I/O intensive) can scale independently
   - IoT adapters (lightweight) run with minimal resources

4. **Fault Isolation**
   - If Person Counting service crashes → Face Recognition still works
   - If one IoT adapter fails → other 5 systems continue

5. **Technology Flexibility**
   - Core services: Python (FastAPI) for YOLO/AI integration
   - Can add Go/Node.js services if needed in future
   - Each service chooses best technology for its task

---

### 2.2 Service Breakdown

#### Complete Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                          │
│           CCTV + Building Management Integration                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard (React/Vue)                                      │
│  - Real-time monitoring                                         │
│  - Face recognition management                                  │
│  - IoT data visualization                                       │
│  - Alerts & notifications                                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌────────────────────────┐               │
│  │    Nginx     │───▶│  FastAPI Auth Gateway  │               │
│  │              │    │  - JWT verification     │               │
│  │ - SSL/TLS    │    │  - Service routing      │               │
│  │ - IP rate    │    │  - Rate limiting        │               │
│  │   limiting   │    │  - Request logging      │               │
│  └──────────────┘    └────────────────────────┘               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌────────▼────────┐  ┌──────▼──────┐
│ Support Layer │  │  Core Layer     │  │ Integration │
└───────────────┘  └─────────────────┘  └─────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SUPPORT SERVICES LAYER                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ Auth Service  │  │  User Management │  │ Alert Service  │ │
│  │               │  │     Service      │  │                │ │
│  │ - Login/      │  │                  │  │ - Email alerts │ │
│  │   Logout      │  │ - CRUD users     │  │ - SMS (future) │ │
│  │ - JWT issue   │  │ - Roles          │  │ - Webhooks     │ │
│  │ - Token       │  │ - Permissions    │  │ - Slack/Line   │ │
│  │   refresh     │  │                  │  │   integration  │ │
│  └───────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  CORE PROCESSING LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ Video Stream     │  │ Face Recognition │  │ Person       ││
│  │    Service       │  │     Service      │  │ Counting     ││
│  │                  │  │                  │  │  Service     ││
│  │ - RTSP connect   │  │ - YOLO detect    │  │              ││
│  │ - 4 cameras      │  │ - ArcFace embed  │  │ - DeepSORT   ││
│  │ - Frame extract  │  │ - pgvector match │  │ - Tracking   ││
│  │ - Health check   │  │ - Voting mech.   │  │ - Line cross ││
│  │ - Auto-reconnect │  │ - Event publish  │  │ - Count      ││
│  └─────────┬────────┘  └─────────┬────────┘  └──────┬───────┘│
│            │                     │                   │        │
│            └─────────────────────┼───────────────────┘        │
└──────────────────────────────────┼────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  IoT INTEGRATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   HVAC   │  │   Pump   │  │ Lighting │  │   Gate   │      │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │  │ Adapter  │      │
│  │          │  │          │  │          │  │          │      │
│  │ Poll/    │  │ Poll/    │  │ Poll/    │  │ Poll/    │      │
│  │ Webhook  │  │ Webhook  │  │ Webhook  │  │ Webhook  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│                                                                 │
│  ┌──────────┐  ┌──────────┐                                   │
│  │   Lift   │  │  Power   │                                   │
│  │ Adapter  │  │ Adapter  │                                   │
│  │          │  │          │                                   │
│  │ Poll/    │  │ Poll/    │                                   │
│  │ Webhook  │  │ Webhook  │                                   │
│  └──────────┘  └──────────┘                                   │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                 REAL-TIME LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │           WebSocket Service                              │ │
│  │                                                          │ │
│  │  - Subscribe to Redis Pub/Sub                           │ │
│  │  - Broadcast to connected clients                       │ │
│  │  - 11 channels (face_events, person_count, 6 IoT, etc.) │ │
│  │  - Native WebSocket (FastAPI)                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   MESSAGE BUS & CACHE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐│
│  │                  Redis (Hybrid Mode)                       ││
│  │                                                            ││
│  │  Redis Streams (Reliable Processing):                     ││
│  │  ├─ stream:frames:CAM001-004  (video frames)             ││
│  │  ├─ stream:iot:hvac           (HVAC data)                ││
│  │  ├─ stream:iot:pump           (pump data)                ││
│  │  ├─ stream:iot:lighting       (lighting data)            ││
│  │  ├─ stream:iot:gate           (gate events)              ││
│  │  ├─ stream:iot:lift           (lift data)                ││
│  │  └─ stream:iot:power          (power readings)           ││
│  │                                                            ││
│  │  Redis Pub/Sub (Fast Broadcasting):                       ││
│  │  ├─ channel:face_events       (recognition events)       ││
│  │  ├─ channel:person_count      (counting updates)         ││
│  │  ├─ channel:alerts            (system alerts)            ││
│  │  ├─ channel:hvac              (HVAC updates)             ││
│  │  ├─ channel:pump              (pump updates)             ││
│  │  ├─ channel:lighting          (lighting updates)         ││
│  │  ├─ channel:gate              (gate events)              ││
│  │  ├─ channel:lift              (lift updates)             ││
│  │  └─ channel:power             (power updates)            ││
│  │                                                            ││
│  │  Cache:                                                    ││
│  │  ├─ session:{session_id}      (user sessions)            ││
│  │  ├─ api_cache:{key}           (API response cache)       ││
│  │  └─ buffer:face_events        (DB outage buffer)         ││
│  └───────────────────────────────────────────────────────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     DATA STORAGE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │               TimescaleDB (PostgreSQL 15)                │ │
│  │                                                          │ │
│  │  Hypertables:                                           │ │
│  │  ├─ power_readings          (1-5 min sampling)         │ │
│  │  ├─ lighting_readings       (5-15 min sampling)        │ │
│  │  ├─ lift_events             (event-based)              │ │
│  │  ├─ access_control_events   (event-based)              │ │
│  │  ├─ fire_system_readings    (1 min sampling)           │ │
│  │  ├─ person_counting         (event-based)              │ │
│  │  ├─ face_recognition_events (event-based)              │ │
│  │  └─ line_crossing_events    (event-based)              │ │
│  │                                                          │ │
│  │  pgvector:                                              │ │
│  │  └─ face_embeddings (512-dim, HNSW index)              │ │
│  │                                                          │ │
│  │  Continuous Aggregates: 9+ views                        │ │
│  │  Compression: 90%+ after 7 days                         │ │
│  │  Retention: 30-90 days raw, 2-5 years aggregated        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              MONITORING & OBSERVABILITY (Optional)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ Prometheus │  │  Grafana   │  │    Loki    │              │
│  │            │  │            │  │            │              │
│  │ - Metrics  │  │ - Dashbds  │  │ - Logs     │              │
│  │ - 30s scrp │  │ - Alerts   │  │ - 7d hot   │              │
│  │ - 7d ret   │  │ - Notifs   │  │ - 30d arc  │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│                                                                 │
│  Resource: 0.5 vCPU, 500 MB RAM (light setup)                  │
│  Production: Move to Grafana Cloud or separate VPS             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Service Inventory (13 Services Total)

| # | Service Name | Responsibility | Tech Stack | Resources |
|---|--------------|----------------|------------|-----------|
| **Support Layer (3)** |
| 1 | Auth Service | Login, JWT issue/refresh, session management | FastAPI, Redis | 0.3 vCPU, 256 MB |
| 2 | User Management | CRUD users, roles, permissions | FastAPI, PostgreSQL | 0.2 vCPU, 256 MB |
| 3 | Alert Service | Email/SMS/Slack notifications, alert routing | FastAPI, SMTP | 0.2 vCPU, 256 MB |
| **Core Processing (3)** |
| 4 | Video Stream Service | RTSP connection, frame extraction, health monitoring | FastAPI, OpenCV | 1 vCPU, 2 GB |
| 5 | Face Recognition Service | YOLO detection, ArcFace embedding, pgvector matching | FastAPI, PyTorch, OpenCV | 2 vCPU, 2 GB |
| 6 | Person Counting Service | DeepSORT tracking, line crossing detection | FastAPI, DeepSORT | 1 vCPU, 2 GB |
| **IoT Integration (6)** |
| 7 | HVAC Adapter | Poll/webhook from HVAC API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| 8 | Pump Adapter | Poll/webhook from pump API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| 9 | Lighting Adapter | Poll/webhook from lighting API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| 10 | Gate Adapter | Poll/webhook from gate API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| 11 | Lift Adapter | Poll/webhook from lift API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| 12 | Power Adapter | Poll/webhook from power API, transform data | FastAPI | 0.2 vCPU, 256 MB |
| **Real-Time (1)** |
| 13 | WebSocket Service | Subscribe Redis Pub/Sub, broadcast to clients | FastAPI WebSocket | 0.5 vCPU, 512 MB |
| **Infrastructure** |
| - | TimescaleDB | Time-series database + pgvector | PostgreSQL 15 + extensions | 1 vCPU, 2 GB |
| - | Redis | Message bus (Streams + Pub/Sub) + cache | Redis 7 | 0.5 vCPU, 512 MB |
| - | Nginx | Reverse proxy, SSL termination, rate limiting | Nginx | 0.3 vCPU, 256 MB |
| - | Auth Gateway | JWT verification, service routing | FastAPI | 0.3 vCPU, 256 MB |
| **Total** | | | | **~8.5 vCPU, ~11 GB** |

**Note:** Total exceeds recommended server spec (4-6 vCPU, 8-12 GB). See Section 7 for resource optimization strategies.

---

### 2.3 Communication Infrastructure

#### 2.3.1 Technology Selection: Redis Hybrid Approach

**Decision:** Use Redis for both message bus and cache, with two distinct patterns:

1. **Redis Streams** - For data processing (frames, IoT readings)
2. **Redis Pub/Sub** - For event broadcasting (notifications, alerts)

**Why Hybrid Instead of Single Pattern?**

| Use Case | Requirement | Redis Streams | Redis Pub/Sub | Winner |
|----------|-------------|---------------|---------------|--------|
| Video frames → multiple processors | Consumer groups (load balancing) | ✅ Yes | ❌ No (all subscribers get all messages) | **Streams** |
| Face event → Alert + WebSocket + Analytics | Broadcast (all subscribers need event) | ❌ No (one consumer per group) | ✅ Yes | **Pub/Sub** |
| IoT data → Database | Persistence (don't lose data) | ✅ Yes (stored in stream) | ❌ No (fire-and-forget) | **Streams** |
| Dashboard update | Low latency | ⚠️ Medium | ✅ Very low | **Pub/Sub** |

**Redis Streams Pattern (Data Processing):**

```python
# Producer: Video Stream Service
await redis.xadd(
    'stream:frames:CAM001',
    {
        'frame': frame_bytes,
        'timestamp': datetime.utcnow().isoformat(),
        'camera_id': 'CAM001'
    },
    maxlen=100  # Keep last 100 frames only
)

# Consumer Group Setup (run once)
await redis.xgroup_create(
    'stream:frames:CAM001',
    'face-recognition-workers',  # Group name
    id='0',
    mkstream=True
)

# Consumer: Face Recognition Service (Worker 1)
messages = await redis.xreadgroup(
    'face-recognition-workers',  # Group
    'worker-1',                   # Consumer ID
    {'stream:frames:CAM001': '>'},  # Read new messages
    count=1,
    block=1000  # Wait 1 second
)

for stream_name, msg_list in messages:
    for msg_id, fields in msg_list:
        frame_bytes = fields['frame']
        # Process frame...

        # Acknowledge (remove from pending)
        await redis.xack(stream_name, 'face-recognition-workers', msg_id)
```

**Benefits:**
- ✅ **Load balancing**: Multiple workers share workload
- ✅ **At-least-once delivery**: Message not deleted until acknowledged
- ✅ **Persistence**: Messages stored until processed
- ✅ **Consumer tracking**: Can see pending messages per consumer

**Redis Pub/Sub Pattern (Event Broadcasting):**

```python
# Publisher: Face Recognition Service
await redis.publish(
    'channel:face_events',
    json.dumps({
        'event_id': 12345,
        'person_id': 42,
        'camera_id': 'CAM001',
        'confidence': 0.95,
        'timestamp': datetime.utcnow().isoformat()
    })
)

# Subscriber 1: Alert Service
pubsub = redis.pubsub()
await pubsub.subscribe('channel:face_events')

async for message in pubsub.listen():
    if message['type'] == 'message':
        event = json.loads(message['data'])
        if event['person_id'] in high_priority_persons:
            await send_alert(event)

# Subscriber 2: WebSocket Service
pubsub2 = redis.pubsub()
await pubsub2.subscribe('channel:face_events')

async for message in pubsub2.listen():
    if message['type'] == 'message':
        # Broadcast to all connected WebSocket clients
        await broadcast_to_clients(message['data'])

# Subscriber 3: Analytics Service (future)
# All subscribers receive the same event simultaneously
```

**Benefits:**
- ✅ **Broadcast**: All subscribers get the message
- ✅ **Low latency**: In-memory, very fast
- ✅ **Simple**: No consumer groups, no acknowledgment
- ✅ **Fire-and-forget**: Perfect for notifications

**Trade-off:**
- ❌ **No persistence**: If subscriber offline, misses message
- ✅ **But acceptable**: Notifications can be missed (not critical data)

---

#### 2.3.2 WebSocket Technology: Native FastAPI

**Decision:** Use FastAPI built-in WebSocket support (not Socket.IO)

**Comparison:**

| Feature | WebSocket Native | Socket.IO |
|---------|------------------|-----------|
| Protocol | RFC 6455 standard | Custom protocol |
| Performance | High (binary framing) | Medium (extra wrapping) |
| Client compatibility | All modern browsers | Needs socket.io-client library |
| Auto-reconnect | Manual implementation | Built-in |
| Fallback | None (requires WebSocket) | Long-polling fallback |
| Dependencies | None (FastAPI built-in) | python-socketio, python-engineio |
| Complexity | Low | Medium |

**Why WebSocket Native?**

1. **Use Case Analysis:**
   - Our use case: **Server → Client** broadcasting (90% of traffic)
   - Client → Server: Minimal (just channel subscriptions)
   - No need for complex bi-directional features

2. **Performance:**
   - 4 cameras + 6 IoT systems = lots of real-time data
   - WebSocket native = lower overhead
   - Tested: ~10-20% faster than Socket.IO for broadcast use case

3. **Simplicity:**
   - No extra dependencies
   - Straightforward integration with Redis Pub/Sub
   - Easy debugging (standard protocol)

4. **Auto-reconnect Not Critical:**
   - Can implement client-side reconnect in ~10 lines JS
   - Most dashboards are on stable WiFi/LAN
   - Mobile apps can handle reconnect logic

**WebSocket Implementation:**

```python
# realtime_service/websocket.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import asyncio
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self, redis):
        self.redis = redis
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channels: list[str]):
        await websocket.accept()

        for channel in channels:
            if channel not in self.active_connections:
                self.active_connections[channel] = set()
            self.active_connections[channel].add(websocket)

        # Start listening to Redis for this client
        asyncio.create_task(self._listen_redis(websocket, channels))

    async def _listen_redis(self, websocket: WebSocket, channels: list[str]):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)

        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    await websocket.send_json({
                        'channel': message['channel'],
                        'data': json.loads(message['data']),
                        'timestamp': datetime.utcnow().isoformat()
                    })
        except WebSocketDisconnect:
            await pubsub.unsubscribe(*channels)

    def disconnect(self, websocket: WebSocket):
        for channel_conns in self.active_connections.values():
            channel_conns.discard(websocket)

manager = ConnectionManager(redis_client)

@app.websocket("/ws/subscribe")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),  # JWT for auth
    channels: str = Query(...)  # "face_events,hvac,power"
):
    # Verify JWT
    user = await verify_jwt_token(token)
    if not user:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    # Parse channels
    channel_list = channels.split(',')

    # Connect
    await manager.connect(websocket, channel_list)

    try:
        # Keep connection alive
        while True:
            # Wait for client ping (or any message)
            data = await websocket.receive_text()

            # Client can send commands
            if data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**Client Implementation (JavaScript):**

```javascript
// dashboard/src/services/websocket.js

class RealtimeService {
    constructor(channels) {
        this.channels = channels;
        this.ws = null;
        this.reconnectDelay = 3000;
        this.callbacks = {};
    }

    connect(token) {
        const url = `ws://api.example.com/ws/subscribe?token=${token}&channels=${this.channels.join(',')}`;
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectDelay = 3000;  // Reset delay
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            const { channel, data } = message;

            // Trigger callbacks
            if (this.callbacks[channel]) {
                this.callbacks[channel].forEach(cb => cb(data));
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed, reconnecting...');
            // Auto-reconnect with exponential backoff
            setTimeout(() => this.connect(token), this.reconnectDelay);
            this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30000);
        };

        // Heartbeat to keep connection alive
        setInterval(() => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
            }
        }, 30000);
    }

    on(channel, callback) {
        if (!this.callbacks[channel]) {
            this.callbacks[channel] = [];
        }
        this.callbacks[channel].push(callback);
    }
}

// Usage
const realtime = new RealtimeService(['face_events', 'power', 'hvac']);
realtime.connect(jwt_token);

realtime.on('face_events', (event) => {
    console.log('Person recognized:', event.person_id);
    updateDashboard(event);
});

realtime.on('power', (data) => {
    console.log('Power update:', data.total_kw);
    updatePowerChart(data);
});
```

**11 WebSocket Channels:**

| Channel | Data Type | Update Frequency | Use Case |
|---------|-----------|------------------|----------|
| `face_events` | Recognition events | Real-time (on detect) | Security dashboard, alerts |
| `person_count` | Current count per camera | Every 5 seconds | Occupancy monitoring |
| `alerts` | System alerts | Real-time | Critical notifications |
| `camera:CAM001-004` | Camera-specific events | Real-time | Camera monitoring page |
| `hvac` | Temperature, status, power | Every 5 minutes | HVAC dashboard |
| `pump` | Flow rate, pressure | Every 5 minutes | Water system monitoring |
| `lighting` | On/off, power | Every 5 minutes | Lighting control |
| `gate` | Open/close events | Real-time | Access control |
| `lift` | Floor, status | Real-time | Elevator monitoring |
| `power` | kW, voltage, current | Every 1 minute | Energy dashboard |

---

### 2.4 Deployment Platform

#### Decision: Docker Compose (Not Kubernetes)

**Why Docker Compose?**

1. **Project Scale:**
   - 4 cameras (not 100 cameras)
   - Single building (not multi-tenant)
   - 1-2 servers (not cloud cluster)

2. **Complexity vs Benefit:**
   - Kubernetes: High complexity, overkill for this scale
   - Docker Compose: Simple, sufficient for single-server deployment

3. **Cost:**
   - K8s requires: Control plane, multiple nodes, load balancers
   - Docker Compose: Single server, no orchestration overhead

4. **Operational Simplicity:**
   - Team familiarity: Docker Compose easier to learn
   - Debugging: Simpler logs (`docker-compose logs`)
   - Updates: `docker-compose up -d --build`

**Migration Path:**
- Start: Docker Compose (1-10 cameras)
- If scale grows (50+ cameras, multiple buildings): Migrate to Kubernetes

---

#### API Gateway: Nginx + FastAPI Hybrid

**Decision:** Nginx as reverse proxy + FastAPI service for authentication

**Why Not Kong or Traefik?**

| Feature | Nginx + FastAPI | Kong | Traefik |
|---------|-----------------|------|---------|
| Complexity | Low | High (needs DB/config) | Medium |
| Performance | Very high | High | Medium |
| Auth flexibility | Python code (easy) | Plugins (limited) | Plugins |
| Team familiarity | ✅ User knows Nginx | ❌ Learning curve | ❌ Learning curve |
| Docker Compose | ✅ Simple | ⚠️ Needs DB | ✅ OK |
| Cost | Free | Free (but complex) | Free |

**Architecture:**

```
Client Request
     │
     ▼
┌─────────────────┐
│  Nginx          │  ← SSL termination, rate limiting, static files
│  Port 80/443    │
└────────┬────────┘
         │
         ├─ /api/* ────────▶ FastAPI Auth Gateway (JWT verify + route)
         │                          │
         │                          ├─ /api/v1/persons → Face Recognition Service
         │                          ├─ /api/v1/cameras → Video Stream Service
         │                          └─ /api/v1/iot/*   → IoT Services
         │
         ├─ /ws/* ─────────▶ WebSocket Service
         │
         └─ / (static) ────▶ Web Dashboard (React build)
```

**Nginx Configuration:**

```nginx
# nginx/nginx.conf

upstream auth_gateway {
    server auth-gateway:8000;
}

upstream websocket_service {
    server websocket-service:8000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=ws_limit:10m rate=10r/m;

server {
    listen 80;
    server_name api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://auth_gateway;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # WebSocket
    location /ws/ {
        limit_req zone=ws_limit burst=5 nodelay;

        proxy_pass http://websocket_service;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # WebSocket timeouts (longer)
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # Static files (dashboard)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Health check (no auth)
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
```

**FastAPI Auth Gateway:**

```python
# auth_gateway/main.py

from fastapi import FastAPI, Request, HTTPException
import httpx
import jwt

app = FastAPI()
http_client = httpx.AsyncClient(timeout=30.0)

# Service routing table
SERVICES = {
    '/api/v1/auth': 'http://auth-service:8000',
    '/api/v1/users': 'http://user-service:8000',
    '/api/v1/persons': 'http://face-recognition:8000',
    '/api/v1/cameras': 'http://video-stream:8000',
    '/api/v1/counting': 'http://person-counting:8000',
    '/api/v1/iot/hvac': 'http://iot-hvac:8000',
    '/api/v1/iot/pump': 'http://iot-pump:8000',
    '/api/v1/iot/lighting': 'http://iot-lighting:8000',
    '/api/v1/iot/gate': 'http://iot-gate:8000',
    '/api/v1/iot/lift': 'http://iot-lift:8000',
    '/api/v1/iot/power': 'http://iot-power:8000',
}

# Public endpoints (no auth)
PUBLIC_ENDPOINTS = [
    '/api/v1/auth/login',
    '/api/v1/auth/refresh',
]

async def verify_jwt(request: Request):
    """Verify JWT token and extract user info"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET_KEY'),
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    """Proxy requests to appropriate service with authentication"""

    full_path = f"/{path}"

    # Check if public endpoint
    if full_path not in PUBLIC_ENDPOINTS:
        user = await verify_jwt(request)
        # Add user info to headers for downstream services
        extra_headers = {
            'X-User-ID': str(user['user_id']),
            'X-User-Role': user['role']
        }
    else:
        extra_headers = {}

    # Find target service
    target_service = None
    for prefix, service_url in SERVICES.items():
        if full_path.startswith(prefix):
            target_service = service_url
            break

    if not target_service:
        raise HTTPException(404, f"No service found for path: {full_path}")

    # Forward request
    try:
        response = await http_client.request(
            method=request.method,
            url=f"{target_service}/{path}",
            headers={**dict(request.headers), **extra_headers},
            content=await request.body(),
            params=dict(request.query_params)
        )

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except httpx.TimeoutException:
        raise HTTPException(504, "Service timeout")
    except httpx.ConnectError:
        raise HTTPException(503, "Service unavailable")
```

**Benefits of This Approach:**

1. **Nginx handles:**
   - ✅ SSL/TLS termination
   - ✅ Static file serving
   - ✅ IP-based rate limiting
   - ✅ Request buffering
   - ✅ High performance (C-based)

2. **FastAPI handles:**
   - ✅ JWT verification (Python = easy to code)
   - ✅ Service routing (flexible logic)
   - ✅ User-based rate limiting (future)
   - ✅ Request transformation
   - ✅ Easy debugging (Python logs)

3. **Combined:**
   - ✅ Best of both worlds
   - ✅ User already knows Nginx
   - ✅ No new infrastructure (Kong DB, etc.)
   - ✅ Docker Compose friendly

---

## 3. Part 2: API & Integration Design

### 3.1 Authentication Strategy

#### 3.1.1 Decision: JWT + Redis Session (Hybrid)

**Why Hybrid Instead of Pure JWT?**

| Requirement | Pure JWT | JWT + Redis Session | Winner |
|-------------|----------|---------------------|--------|
| Stateless (scale easily) | ✅ Yes | ⚠️ Semi-stateless | JWT |
| Instant revoke (logout, security breach) | ❌ No (need blacklist) | ✅ Yes | **Hybrid** |
| Track active sessions | ❌ No | ✅ Yes | **Hybrid** |
| Low latency | ✅ No DB lookup | ⚠️ Redis lookup (very fast) | Tie |
| Force logout all devices | ❌ Can't | ✅ Delete sessions | **Hybrid** |

**Verdict:** JWT + Redis Session provides **security benefits** with minimal performance cost.

---

#### 3.1.2 Token Structure

**Access Token (JWT):**

```json
{
  "user_id": 42,
  "username": "john.doe",
  "role": "admin",
  "session_id": "sess_abc123xyz",
  "iat": 1730721600,
  "exp": 1730732400
}
```

**Payload Fields:**
- `user_id`: Numeric user ID (for DB queries)
- `username`: Display name
- `role`: `admin`, `operator`, or `viewer`
- `session_id`: Reference to Redis session (for revocation)
- `iat`: Issued at (Unix timestamp)
- `exp`: Expiration (Unix timestamp)

**Refresh Token (JWT):**

```json
{
  "user_id": 42,
  "session_id": "sess_abc123xyz",
  "type": "refresh",
  "iat": 1730721600,
  "exp": 1731326400
}
```

---

#### 3.1.3 Role-Based Token Expiry

**Decision:** Different expiration based on role privilege level

| Role | Permissions | Access Token | Refresh Token | Rationale |
|------|------------|--------------|---------------|-----------|
| **Admin** | Full CRUD, config, user management | **3 hours** | 7 days | High privilege = short session for security |
| **Operator** | Read/write data, no config changes | **3 hours** | 7 days | Similar privilege to admin, same security level |
| **Viewer** | Read-only | **7 days** | 7 days | Low privilege, convenience for dashboard viewers |

**Why Different Expiry?**

1. **Admin/Operator (3 hours):**
   - Can modify critical settings
   - Can add/delete users
   - Can change face registrations
   - **Security risk if token stolen** → Short expiry

2. **Viewer (7 days):**
   - Can only view dashboards
   - Cannot modify anything
   - **Convenience for executives** (mobile app won't logout frequently)
   - **Low security risk** even if token stolen

**Example:**
```python
def create_access_token(user: User) -> str:
    """Create access token with role-based expiry"""

    # Role-based expiration
    if user.role in ['admin', 'operator']:
        expiry_hours = 3
    else:  # viewer
        expiry_hours = 24 * 7  # 7 days

    payload = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'session_id': user.current_session_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=expiry_hours)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

---

#### 3.1.4 Session Management (Redis)

**Session Storage:**

```python
# Login flow
async def login(username: str, password: str, redis: Redis):
    # 1. Verify credentials
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(401, "Invalid credentials")

    # 2. Create session ID
    session_id = f"sess_{secrets.token_urlsafe(16)}"

    # 3. Store session in Redis
    session_data = {
        'user_id': user.user_id,
        'username': user.username,
        'role': user.role,
        'ip_address': request.client.host,
        'user_agent': request.headers.get('user-agent'),
        'created_at': datetime.utcnow().isoformat(),
        'last_activity': datetime.utcnow().isoformat(),
        'revoked': False
    }

    # TTL based on role (7 days for all, but access token expires earlier)
    await redis.setex(
        f"session:{session_id}",
        7 * 24 * 3600,  # 7 days
        json.dumps(session_data)
    )

    # 4. Create tokens
    access_token = create_access_token(user, session_id)
    refresh_token = create_refresh_token(user, session_id)

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'expires_in': 3600 * (3 if user.role in ['admin', 'operator'] else 168)
    }
```

**Token Verification:**

```python
async def verify_token(token: str, redis: Redis) -> dict:
    """Verify JWT and check session validity"""

    # 1. Decode JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")

    # 2. Check session in Redis
    session_id = payload['session_id']
    session_data = await redis.get(f"session:{session_id}")

    if not session_data:
        raise HTTPException(401, "Session not found or expired")

    session = json.loads(session_data)

    # 3. Check if revoked
    if session.get('revoked'):
        raise HTTPException(401, "Session revoked")

    # 4. Update last activity
    session['last_activity'] = datetime.utcnow().isoformat()
    await redis.setex(
        f"session:{session_id}",
        7 * 24 * 3600,
        json.dumps(session)
    )

    return payload
```

**Logout (Revoke Session):**

```python
async def logout(session_id: str, redis: Redis):
    """Revoke session immediately"""

    session_data = await redis.get(f"session:{session_id}")
    if session_data:
        session = json.loads(session_data)
        session['revoked'] = True
        session['revoked_at'] = datetime.utcnow().isoformat()

        # Keep session for audit trail (but marked revoked)
        await redis.setex(
            f"session:{session_id}",
            7 * 24 * 3600,
            json.dumps(session)
        )
```

**Benefits:**
- ✅ **Instant logout**: Session revoked immediately
- ✅ **Security incident response**: Can revoke all sessions for user
- ✅ **Audit trail**: Track when sessions created/revoked
- ✅ **Device tracking**: Know which devices logged in

---

### 3.2 REST API Specifications

#### 3.2.1 Authentication Endpoints

```python
# POST /api/v1/auth/login
# Login and receive tokens

Request:
{
  "username": "john.doe",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 10800  # seconds (3 hours for admin)
}

Errors:
- 401: Invalid credentials
- 429: Too many login attempts
```

```python
# POST /api/v1/auth/refresh
# Refresh access token using refresh token

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 10800
}

Errors:
- 401: Invalid or expired refresh token
- 401: Session revoked
```

```python
# POST /api/v1/auth/logout
# Revoke current session

Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "message": "Logged out successfully"
}

Errors:
- 401: Invalid token
```

```python
# GET /api/v1/auth/me
# Get current user info

Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "user_id": 42,
  "username": "john.doe",
  "email": "john.doe@example.com",
  "role": "admin",
  "created_at": "2025-01-01T00:00:00Z",
  "last_login": "2025-11-04T10:30:00Z"
}

Errors:
- 401: Invalid token
```

---

#### 3.2.2 Face Recognition Endpoints

```python
# GET /api/v1/persons
# List all registered persons

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- search (string, optional): Search by name or employee ID
- department (string, optional): Filter by department
- verified (boolean, optional): Filter by verification status
- limit (int, default=50, max=200): Results per page
- offset (int, default=0): Pagination offset

Response (200 OK):
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "person_id": 42,
      "full_name": "John Doe",
      "employee_id": "EMP001",
      "department": "IT",
      "email": "john.doe@company.com",
      "photo_count": 5,
      "verified": true,
      "registered_at": "2025-10-15T09:00:00Z",
      "registered_by": "admin"
    },
    ...
  ]
}
```

```python
# POST /api/v1/persons
# Register a new person (without photos)

Headers:
Authorization: Bearer <access_token>
Content-Type: application/json

Required Roles: admin, operator

Request:
{
  "full_name": "Jane Smith",
  "employee_id": "EMP002",
  "department": "HR",
  "email": "jane.smith@company.com"
}

Response (201 Created):
{
  "person_id": 43,
  "full_name": "Jane Smith",
  "employee_id": "EMP002",
  "department": "HR",
  "email": "jane.smith@company.com",
  "photo_count": 0,
  "verified": false,
  "registered_at": "2025-11-04T10:30:00Z",
  "registered_by": "john.doe"
}

Errors:
- 400: employee_id already exists
- 403: Insufficient permissions (viewer role)
```

```python
# POST /api/v1/persons/{person_id}/photos
# Upload photos for face enrollment (3-5 photos required)

Headers:
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Required Roles: admin, operator

Request:
Form Data:
- photos: file[] (3-5 image files, JPEG/PNG, max 5MB each)

Response (201 Created):
{
  "person_id": 43,
  "photos_uploaded": 5,
  "photos_processed": 5,
  "photos_failed": 0,
  "verified": true,
  "quality_scores": [0.92, 0.88, 0.95, 0.87, 0.91],
  "message": "Person verified with 5 photos"
}

Errors:
- 400: Less than 3 photos
- 400: More than 10 photos
- 400: No face detected in photo
- 400: Multiple faces detected in photo
- 400: Photo quality too low
- 404: Person not found
```

```python
# GET /api/v1/persons/{person_id}
# Get person details with recent recognition events

Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "person_id": 42,
  "full_name": "John Doe",
  "employee_id": "EMP001",
  "department": "IT",
  "email": "john.doe@company.com",
  "photo_count": 5,
  "verified": true,
  "registered_at": "2025-10-15T09:00:00Z",
  "recent_events": [
    {
      "event_id": 12345,
      "time": "2025-11-04T10:30:00Z",
      "camera_id": "CAM001",
      "camera_name": "Main Entrance",
      "confidence": 0.95
    },
    ...
  ]
}

Errors:
- 404: Person not found
```

```python
# GET /api/v1/events/recognition
# List face recognition events with filtering

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- camera_id (string, optional): Filter by camera
- person_id (int, optional): Filter by person
- start_time (ISO 8601, optional): Filter from this time
- end_time (ISO 8601, optional): Filter until this time
- min_confidence (float 0-1, default=0.0): Minimum confidence score
- limit (int, default=100, max=500): Results per page
- offset (int, default=0): Pagination offset

Response (200 OK):
{
  "total": 1500,
  "limit": 100,
  "offset": 0,
  "data": [
    {
      "event_id": 12345,
      "time": "2025-11-04T10:30:15Z",
      "camera_id": "CAM001",
      "camera_name": "Main Entrance",
      "person_id": 42,
      "full_name": "John Doe",
      "employee_id": "EMP001",
      "confidence": 0.95,
      "snapshot_url": "/api/v1/events/12345/snapshot.jpg"
    },
    ...
  ]
}
```

---

#### 3.2.3 Camera Management Endpoints

```python
# GET /api/v1/cameras
# List all cameras with status

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- status (string, optional): Filter by status (online, offline, error)
- location (string, optional): Filter by location

Response (200 OK):
{
  "total": 4,
  "data": [
    {
      "camera_id": "CAM001",
      "name": "Main Entrance",
      "location": "Building A - Ground Floor",
      "rtsp_url": "rtsp://192.168.1.101:554/stream1",
      "status": "online",
      "fps": 5,
      "resolution": "1920x1080",
      "last_seen": "2025-11-04T10:30:00Z",
      "uptime_seconds": 86400,
      "frames_processed_today": 43200,
      "detections_today": 150
    },
    ...
  ]
}
```

```python
# GET /api/v1/cameras/{camera_id}/health
# Get detailed camera health status

Headers:
Authorization: Bearer <access_token>

Response (200 OK):
{
  "camera_id": "CAM001",
  "status": "online",
  "connection": {
    "connected": true,
    "last_seen": "2025-11-04T10:30:45Z",
    "uptime_seconds": 86400,
    "connection_failures_count": 2,
    "last_failure": "2025-11-03T15:20:00Z"
  },
  "performance": {
    "current_fps": 5.0,
    "target_fps": 5,
    "frames_processed_last_minute": 300,
    "avg_processing_time_ms": 120
  },
  "detections": {
    "faces_detected_today": 150,
    "persons_counted_today": 450,
    "last_detection": "2025-11-04T10:28:30Z"
  }
}
```

```python
# GET /api/v1/cameras/{camera_id}/stream
# Get live MJPEG stream

Headers:
Authorization: Bearer <access_token>

Response (200 OK):
Content-Type: multipart/x-mixed-replace; boundary=frame

[MJPEG stream data]

Notes:
- Opens persistent HTTP connection
- Streams JPEG frames continuously
- Use with <img src="/api/v1/cameras/CAM001/stream"> in browser
```

---

#### 3.2.4 Person Counting Endpoints

```python
# GET /api/v1/counting/current
# Get current person count per camera

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- camera_id (string, optional): Filter by specific camera

Response (200 OK):
{
  "timestamp": "2025-11-04T10:30:00Z",
  "cameras": [
    {
      "camera_id": "CAM001",
      "camera_name": "Main Entrance",
      "current_count": 12,
      "in_today": 245,
      "out_today": 233,
      "peak_count_today": 45,
      "peak_time_today": "2025-11-04T09:00:00Z"
    },
    ...
  ],
  "total_current": 35,
  "total_in_today": 890,
  "total_out_today": 855
}
```

```python
# GET /api/v1/counting/history
# Get historical person counting data

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- camera_id (string, optional): Filter by camera
- start_time (ISO 8601, required): Start time
- end_time (ISO 8601, required): End time
- interval (string, default=1h): Aggregation interval (1m, 5m, 15m, 1h, 1d)
- limit (int, default=1000, max=10000): Max data points

Response (200 OK):
{
  "camera_id": "CAM001",
  "start_time": "2025-11-04T00:00:00Z",
  "end_time": "2025-11-04T23:59:59Z",
  "interval": "1h",
  "data": [
    {
      "time": "2025-11-04T00:00:00Z",
      "avg_count": 2.5,
      "max_count": 8,
      "in_count": 15,
      "out_count": 12
    },
    {
      "time": "2025-11-04T01:00:00Z",
      "avg_count": 1.2,
      "max_count": 3,
      "in_count": 5,
      "out_count": 7
    },
    ...
  ]
}
```

---

#### 3.2.5 IoT System Endpoints

All 6 IoT systems follow the same pattern:

```python
# GET /api/v1/iot/{system}/current
# Get current readings for IoT system

Systems: hvac, pump, lighting, gate, lift, power

Headers:
Authorization: Bearer <access_token>

Example: GET /api/v1/iot/hvac/current

Response (200 OK):
{
  "system": "hvac",
  "timestamp": "2025-11-04T10:30:00Z",
  "zones": [
    {
      "zone_id": "HVAC_ZONE_1",
      "zone_name": "Floor 1 Office",
      "temperature": 24.5,
      "humidity": 55.0,
      "set_point": 25.0,
      "status": "cooling",
      "power_kw": 12.3,
      "mode": "auto"
    },
    ...
  ]
}

Example: GET /api/v1/iot/power/current

Response (200 OK):
{
  "system": "power",
  "timestamp": "2025-11-04T10:30:00Z",
  "meters": [
    {
      "meter_id": "METER_001",
      "meter_name": "Main Incomer",
      "power_kw": 150.5,
      "voltage_v": 220.3,
      "current_a": 205.1,
      "power_factor": 0.95,
      "energy_kwh": 12345.67,
      "demand_kw": 155.2
    },
    ...
  ],
  "total_power_kw": 150.5,
  "total_energy_kwh_today": 1234.5
}
```

```python
# GET /api/v1/iot/{system}/history
# Get historical data for IoT system

Headers:
Authorization: Bearer <access_token>

Query Parameters:
- zone_id or meter_id (string, optional): Filter by specific zone/meter
- start_time (ISO 8601, required): Start time
- end_time (ISO 8601, required): End time
- interval (string, default=5m): Aggregation interval
- limit (int, default=1000, max=10000): Max data points

Example: GET /api/v1/iot/power/history?start_time=2025-11-04T00:00:00Z&end_time=2025-11-04T23:59:59Z&interval=1h

Response (200 OK):
{
  "system": "power",
  "meter_id": "METER_001",
  "start_time": "2025-11-04T00:00:00Z",
  "end_time": "2025-11-04T23:59:59Z",
  "interval": "1h",
  "data": [
    {
      "time": "2025-11-04T00:00:00Z",
      "avg_power_kw": 120.5,
      "max_power_kw": 145.2,
      "min_power_kw": 95.3,
      "energy_kwh": 120.5
    },
    ...
  ]
}
```

---

### 3.3 WebSocket Real-Time Communication

See Section 2.3.2 for WebSocket implementation details.

**11 Channels Available:**

| # | Channel | Update Frequency | Payload Example |
|---|---------|------------------|-----------------|
| 1 | `face_events` | Real-time | `{"person_id": 42, "camera_id": "CAM001", "confidence": 0.95}` |
| 2 | `person_count` | Every 5 seconds | `{"camera_id": "CAM001", "current_count": 12, "in": 245, "out": 233}` |
| 3 | `alerts` | Real-time | `{"severity": "warning", "message": "Camera CAM002 offline"}` |
| 4-7 | `camera:CAM001-004` | Real-time | `{"event": "detection", "type": "face", "count": 2}` |
| 8 | `hvac` | Every 5 minutes | `{"zone_id": "HVAC_ZONE_1", "temperature": 24.5, "status": "cooling"}` |
| 9 | `pump` | Every 5 minutes | `{"pump_id": "PUMP_001", "flow_rate": 120.5, "pressure": 3.5}` |
| 10 | `lighting` | Every 5 minutes | `{"zone_id": "LIGHT_ZONE_1", "status": "on", "brightness": 80, "power_kw": 2.3}` |
| 11 | `gate` | Real-time (events) | `{"gate_id": "GATE_001", "event": "opened", "card_id": "CARD_12345"}` |
| 12 | `lift` | Real-time | `{"lift_id": "LIFT_01", "current_floor": 5, "direction": "up", "passengers": 4}` |
| 13 | `power` | Every 1 minute | `{"meter_id": "METER_001", "power_kw": 150.5, "energy_kwh": 12345.67}` |

---

### 3.4 IoT Integration Patterns

#### 3.4.1 Adapter Architecture

**Pattern:** One adapter service per IoT system, supporting both Polling and Webhook

```python
# iot_adapters/base_adapter.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

class IoTAdapter(ABC):
    """Base class for all IoT adapters"""

    def __init__(self, system_name: str, config: dict, redis, db_pool):
        self.system_name = system_name
        self.config = config
        self.redis = redis
        self.db_pool = db_pool
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.is_polling = config.get('mode') == 'polling'
        self.polling_interval = config.get('polling_interval', 300)  # 5 min default

    async def start(self):
        """Start the adapter (polling or webhook receiver)"""
        if self.is_polling:
            asyncio.create_task(self._polling_loop())
        else:
            # Webhook mode - adapter exposes HTTP endpoint
            # Customer POSTs data to /webhook endpoint
            pass

    async def _polling_loop(self):
        """Poll customer API at regular intervals"""
        while True:
            try:
                data = await self.fetch_data()
                if data:
                    await self.process_data(data)
            except Exception as e:
                logger.error(f"{self.system_name} polling error: {e}")

            await asyncio.sleep(self.polling_interval)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=5, max=60)
    )
    async def fetch_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from customer API with retry"""
        try:
            response = await self.http_client.get(
                self.config['api_url'],
                headers={'Authorization': f"Bearer {self.config['api_key']}"}
            )
            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            logger.warning(f"{self.system_name} API timeout")
            return await self._get_cached_data()

        except httpx.HTTPStatusError as e:
            logger.error(f"{self.system_name} API error {e.response.status_code}")
            if e.response.status_code >= 500:
                # Server error - use cache
                return await self._get_cached_data()
            raise

        except Exception as e:
            logger.error(f"{self.system_name} fetch error: {e}")
            # After 3 retries failed → alert
            await self._send_alert(f"{self.system_name} API unreachable")
            return await self._get_cached_data()

    async def process_data(self, raw_data: Dict[str, Any]):
        """Process and store data"""
        # 1. Transform to standard format
        transformed = await self.transform_data(raw_data)

        # 2. Validate
        if not await self.validate_data(transformed):
            logger.warning(f"{self.system_name} data validation failed")
            return

        # 3. Store in Redis Stream (for reliability)
        await self.redis.xadd(
            f'stream:iot:{self.system_name}',
            {
                'data': json.dumps(transformed),
                'timestamp': datetime.utcnow().isoformat()
            },
            maxlen=1000  # Keep last 1000 readings
        )

        # 4. Store in TimescaleDB
        await self.store_in_db(transformed)

        # 5. Publish to Redis Pub/Sub for real-time dashboard
        await self.redis.publish(
            f'channel:{self.system_name}',
            json.dumps(transformed)
        )

        # 6. Cache for fallback
        await self.redis.setex(
            f'cache:iot:{self.system_name}:latest',
            600,  # 10 minutes
            json.dumps(transformed)
        )

    async def _get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get cached data when API fails"""
        cached = await self.redis.get(f'cache:iot:{self.system_name}:latest')
        if cached:
            logger.info(f"{self.system_name} using cached data")
            return json.loads(cached)
        return None

    async def _send_alert(self, message: str):
        """Send alert via Redis Pub/Sub"""
        await self.redis.publish(
            'channel:alerts',
            json.dumps({
                'severity': 'warning',
                'source': self.system_name,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })
        )

    @abstractmethod
    async def transform_data(self, raw_data: Dict) -> Dict:
        """Transform customer API format to our standard format"""
        pass

    @abstractmethod
    async def validate_data(self, data: Dict) -> bool:
        """Validate data before storing"""
        pass

    @abstractmethod
    async def store_in_db(self, data: Dict):
        """Store in TimescaleDB"""
        pass
```

---

#### 3.4.2 Example: Power System Adapter

```python
# iot_adapters/power_adapter.py

class PowerSystemAdapter(IoTAdapter):
    """Adapter for main power system"""

    def __init__(self, config, redis, db_pool):
        super().__init__('power', config, redis, db_pool)
        self.polling_interval = 60  # 1 minute for power

    async def transform_data(self, raw_data: Dict) -> Dict:
        """
        Transform customer API format to our standard format

        Customer API format (example):
        {
            "timestamp": "2025-11-04T10:30:00+07:00",
            "meters": [
                {
                    "id": "MTR001",
                    "name": "Main Incomer",
                    "kw": 150.5,
                    "v": 220.3,
                    "a": 205.1,
                    "pf": 0.95,
                    "kwh": 12345.67,
                    "demand": 155.2
                }
            ]
        }

        Our standard format:
        {
            "timestamp": "2025-11-04T10:30:00Z",
            "meters": [
                {
                    "meter_id": "METER_001",
                    "meter_name": "Main Incomer",
                    "power_kw": 150.5,
                    "voltage_v": 220.3,
                    "current_a": 205.1,
                    "power_factor": 0.95,
                    "energy_kwh": 12345.67,
                    "demand_kw": 155.2
                }
            ]
        }
        """

        # Parse timestamp (handle timezone)
        dt = datetime.fromisoformat(raw_data['timestamp'])
        timestamp = dt.astimezone(timezone.utc).isoformat()

        # Transform meters
        meters = []
        for meter in raw_data['meters']:
            meters.append({
                'meter_id': meter['id'],
                'meter_name': meter['name'],
                'power_kw': float(meter['kw']),
                'voltage_v': float(meter['v']),
                'current_a': float(meter['a']),
                'power_factor': float(meter['pf']),
                'energy_kwh': float(meter['kwh']),
                'demand_kw': float(meter['demand'])
            })

        return {
            'timestamp': timestamp,
            'meters': meters
        }

    async def validate_data(self, data: Dict) -> bool:
        """Validate power readings"""
        for meter in data['meters']:
            # Basic sanity checks
            if meter['power_kw'] < 0 or meter['power_kw'] > 10000:
                logger.warning(f"Invalid power_kw: {meter['power_kw']}")
                return False

            if meter['voltage_v'] < 100 or meter['voltage_v'] > 500:
                logger.warning(f"Invalid voltage_v: {meter['voltage_v']}")
                return False

            if meter['power_factor'] < 0 or meter['power_factor'] > 1:
                logger.warning(f"Invalid power_factor: {meter['power_factor']}")
                return False

        return True

    async def store_in_db(self, data: Dict):
        """Store in TimescaleDB power_readings hypertable"""
        async with self.db_pool() as db:
            for meter in data['meters']:
                await db.execute(
                    text("""
                        INSERT INTO power_readings
                        (time, meter_id, power_kw, voltage_v, current_a,
                         power_factor, energy_kwh, demand_kw)
                        VALUES (
                            :time, :meter_id, :power_kw, :voltage_v,
                            :current_a, :power_factor, :energy_kwh, :demand_kw
                        )
                        ON CONFLICT (time, meter_id) DO UPDATE
                        SET power_kw = EXCLUDED.power_kw,
                            voltage_v = EXCLUDED.voltage_v,
                            current_a = EXCLUDED.current_a,
                            power_factor = EXCLUDED.power_factor,
                            energy_kwh = EXCLUDED.energy_kwh,
                            demand_kw = EXCLUDED.demand_kw
                    """),
                    {
                        'time': data['timestamp'],
                        'meter_id': meter['meter_id'],
                        'power_kw': meter['power_kw'],
                        'voltage_v': meter['voltage_v'],
                        'current_a': meter['current_a'],
                        'power_factor': meter['power_factor'],
                        'energy_kwh': meter['energy_kwh'],
                        'demand_kw': meter['demand_kw']
                    }
                )

            await db.commit()
```

---

#### 3.4.3 Webhook Support

```python
# iot_adapters/webhook_handler.py

from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook/{system_name}")
async def receive_webhook(
    system_name: str,
    request: Request,
    api_key: str = Header(...)
):
    """
    Receive webhook from customer IoT system

    Example:
    POST /webhook/power
    Headers:
        X-API-Key: customer_secret_key
        Content-Type: application/json
    Body:
        {customer's data format}
    """

    # 1. Verify API key
    expected_key = os.getenv(f'{system_name.upper()}_WEBHOOK_KEY')
    if api_key != expected_key:
        raise HTTPException(403, "Invalid API key")

    # 2. Get raw data
    raw_data = await request.json()

    # 3. Get adapter for this system
    adapter = get_adapter(system_name)
    if not adapter:
        raise HTTPException(404, f"System {system_name} not found")

    # 4. Process data (same flow as polling)
    try:
        await adapter.process_data(raw_data)
        return {"status": "ok", "message": "Data received"}

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(500, "Processing failed")
```

---

## 4. Part 3: Reliability & Operations

### 4.1 Error Handling Strategy

#### 4.1.1 Camera Offline Handling

**Decision:** Exponential backoff with alert escalation

**Implementation:**

```python
class ResilientCameraConnection:
    """Auto-reconnecting camera connection with exponential backoff"""

    def __init__(self, camera_id: str, rtsp_url: str, redis, db_pool):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.redis = redis
        self.db_pool = db_pool

        self.retry_delay = 30  # Start with 30 seconds
        self.max_delay = 300   # Max 5 minutes
        self.retry_count = 0
        self.cap: Optional[cv2.VideoCapture] = None

    async def start(self):
        """Main connection loop with exponential backoff"""
        while True:
            try:
                await self._connect()
                await self._process_frames()

            except CameraConnectionError as e:
                await self._handle_failure(e)

    async def _connect(self):
        """Connect to RTSP stream"""
        logger.info(f"Connecting to camera {self.camera_id}: {self.rtsp_url}")

        self.cap = cv2.VideoCapture(self.rtsp_url)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Low latency

        if not self.cap.isOpened():
            raise CameraConnectionError("Failed to open RTSP stream")

        # Test read
        ret, frame = self.cap.read()
        if not ret:
            raise CameraConnectionError("Failed to read first frame")

        # Success
        self.retry_count = 0
        self.retry_delay = 30

        await self._update_status('online')
        logger.info(f"Camera {self.camera_id} connected successfully")

        # Send recovery alert if was down
        if self.retry_count > 0:
            await self._send_alert('info', f"Camera {self.camera_id} recovered")

    async def _process_frames(self):
        """Process frames from camera"""
        frame_interval = 1.0 / 5  # 5 FPS
        last_frame_time = 0
        consecutive_failures = 0

        while True:
            current_time = asyncio.get_event_loop().time()

            if current_time - last_frame_time >= frame_interval:
                ret, frame = self.cap.read()

                if not ret:
                    consecutive_failures += 1
                    if consecutive_failures >= 5:
                        raise CameraConnectionError(f"Failed to read {consecutive_failures} consecutive frames")
                    await asyncio.sleep(0.5)
                    continue

                # Reset failure counter
                consecutive_failures = 0

                # Publish frame to Redis Stream
                await self._publish_frame(frame)

                last_frame_time = current_time

            await asyncio.sleep(0.01)

    async def _handle_failure(self, error: CameraConnectionError):
        """Handle connection failure with escalating alerts"""
        self.retry_count += 1

        logger.error(f"Camera {self.camera_id} connection failed (attempt {self.retry_count}): {error}")

        # Update status
        await self._update_status('offline')

        # Alert escalation
        if self.retry_count == 3:
            await self._send_alert('warning', f"Camera {self.camera_id} offline for 3 attempts")

        elif self.retry_count == 10:
            await self._send_alert('critical', f"Camera {self.camera_id} CRITICAL - offline for 10 attempts")

        # Exponential backoff
        logger.info(f"Retrying camera {self.camera_id} in {self.retry_delay} seconds")
        await asyncio.sleep(self.retry_delay)

        self.retry_delay = min(self.retry_delay * 1.5, self.max_delay)
        # Progression: 30s → 45s → 67s → 101s → 151s → 227s → 300s (max)

    async def _update_status(self, status: str):
        """Update camera status in Redis and database"""
        await self.redis.hset(
            f'camera:{self.camera_id}:status',
            mapping={
                'status': status,
                'last_updated': datetime.utcnow().isoformat(),
                'retry_count': str(self.retry_count)
            }
        )

        async with self.db_pool() as db:
            await db.execute(
                text("""
                    UPDATE cameras
                    SET status = :status,
                        last_seen = NOW(),
                        consecutive_failures = :failures
                    WHERE camera_id = :camera_id
                """),
                {
                    'status': status,
                    'failures': self.retry_count,
                    'camera_id': self.camera_id
                }
            )
            await db.commit()

    async def _send_alert(self, severity: str, message: str):
        """Send alert via Redis Pub/Sub"""
        await self.redis.publish(
            'channel:alerts',
            json.dumps({
                'severity': severity,
                'source': 'video_stream_service',
                'camera_id': self.camera_id,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })
        )

    async def _publish_frame(self, frame: np.ndarray):
        """Publish frame to Redis Stream"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

        await self.redis.xadd(
            f'stream:frames:{self.camera_id}',
            {
                'frame': buffer.tobytes(),
                'timestamp': datetime.utcnow().isoformat()
            },
            maxlen=100
        )


class CameraConnectionError(Exception):
    """Camera connection error"""
    pass
```

**Backoff Progression:**
| Attempt | Delay | Cumulative Time |
|---------|-------|-----------------|
| 1 | 30s | 30s |
| 2 | 45s | 1m 15s |
| 3 | 67s | 2m 22s (⚠️ Warning alert) |
| 4 | 101s | 4m 3s |
| 5 | 151s | 6m 34s |
| 6 | 227s | 10m 21s |
| 7+ | 300s | (🔴 Critical alert at attempt 10) |

---

#### 4.1.2 Database Outage Handling

**Decision:** Buffer in Redis Streams, auto-sync when DB recovers

**Implementation:**

```python
class ResilientDatabaseService:
    """Database service with Redis buffering for outages"""

    def __init__(self, db_pool, redis):
        self.db_pool = db_pool
        self.redis = redis
        self.is_db_healthy = True

        # Start background sync task
        asyncio.create_task(self._sync_buffered_data())

    async def save_face_event(self, event: Dict):
        """Save face recognition event with buffering"""
        try:
            # Try to save to TimescaleDB
            await self._save_to_db(event)
            self.is_db_healthy = True

        except DatabaseError as e:
            logger.error(f"Database unavailable: {e}")
            self.is_db_healthy = False

            # Fallback: Buffer in Redis Stream
            await self.redis.xadd(
                'buffer:face_events',
                {
                    'data': json.dumps(event),
                    'timestamp': datetime.utcnow().isoformat()
                },
                maxlen=10000  # Max 10,000 buffered events
            )

            logger.warning(f"Event buffered in Redis (buffer size: {await self._get_buffer_size()})")

            # Alert if buffer is filling up
            buffer_size = await self._get_buffer_size()
            if buffer_size > 5000:
                await self._send_alert('warning', f"Buffer size: {buffer_size}/10000")
            elif buffer_size >= 10000:
                await self._send_alert('critical', "Buffer full! Old events being dropped")

    async def _save_to_db(self, event: Dict):
        """Save event to TimescaleDB"""
        async with self.db_pool() as db:
            await db.execute(
                text("""
                    INSERT INTO face_recognition_events
                    (time, camera_id, person_id, confidence_score, bounding_box)
                    VALUES (:time, :camera_id, :person_id, :confidence, :box)
                """),
                event
            )
            await db.commit()

    async def _sync_buffered_data(self):
        """Background task: Sync buffered data when DB recovers"""
        while True:
            try:
                if not self.is_db_healthy:
                    # Check if DB is back
                    if await self._check_db_health():
                        logger.info("Database recovered, syncing buffered data...")
                        await self._flush_buffer()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Sync error: {e}")
                await asyncio.sleep(60)

    async def _check_db_health(self) -> bool:
        """Check if database is healthy"""
        try:
            async with self.db_pool() as db:
                await db.execute(text("SELECT 1"))
                return True
        except:
            return False

    async def _flush_buffer(self):
        """Flush all buffered events to database"""
        synced_count = 0

        while True:
            # Read 100 events at a time
            messages = await self.redis.xread(
                {'buffer:face_events': '0'},
                count=100
            )

            if not messages:
                break

            for stream_name, msg_list in messages:
                for msg_id, fields in msg_list:
                    try:
                        event = json.loads(fields['data'])
                        await self._save_to_db(event)

                        # Delete from buffer
                        await self.redis.xdel(stream_name, msg_id)
                        synced_count += 1

                    except Exception as e:
                        logger.error(f"Failed to sync event {msg_id}: {e}")
                        # Keep event in buffer for retry

        if synced_count > 0:
            logger.info(f"Synced {synced_count} buffered events to database")
            await self._send_alert('info', f"Database recovered, synced {synced_count} events")

        self.is_db_healthy = True

    async def _get_buffer_size(self) -> int:
        """Get current buffer size"""
        info = await self.redis.xinfo_stream('buffer:face_events')
        return info['length']

    async def _send_alert(self, severity: str, message: str):
        """Send alert"""
        await self.redis.publish(
            'channel:alerts',
            json.dumps({
                'severity': severity,
                'source': 'database_service',
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })
        )
```

**Benefits:**
- ✅ **No data loss**: Events buffered during outage
- ✅ **Auto-recovery**: Syncs automatically when DB returns
- ✅ **Bounded buffer**: Max 10,000 events (prevent memory overflow)
- ✅ **Monitoring**: Alerts when buffer fills up

---

#### 4.1.3 Redis Down Handling

**Decision:** Fail fast (critical dependency)

**Rationale:**
- Redis is the message bus - if down, services can't communicate
- Better to fail fast and alert immediately
- Redis downtime should be rare (use Redis Cluster/Sentinel for HA)

```python
class ServiceHealthCheck:
    """Health check for critical dependencies"""

    async def startup_check(self, redis, db_pool):
        """Check all critical dependencies on startup"""

        # Check Redis
        try:
            await redis.ping()
            logger.info("✅ Redis connected")
        except:
            logger.critical("❌ Redis unavailable - cannot start service")
            raise RuntimeError("Redis is required for service operation")

        # Check Database
        try:
            async with db_pool() as db:
                await db.execute(text("SELECT 1"))
            logger.info("✅ Database connected")
        except Exception as e:
            logger.warning(f"⚠️ Database unavailable: {e}")
            logger.info("Service will start but with degraded functionality")

    async def runtime_check(self, redis):
        """Runtime check for Redis"""
        try:
            await redis.ping()
            return True
        except:
            logger.critical("Redis connection lost - service cannot operate")
            await self._send_emergency_alert("Redis down - CRITICAL")
            raise RuntimeError("Redis connection lost")
```

---

### 4.2 Monitoring & Observability

#### 4.2.1 Metrics Collection (Prometheus)

**Light Configuration for Resource Efficiency:**

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 30s      # Scrape every 30s (default 15s) - 50% reduction
  evaluation_interval: 30s
  external_labels:
    cluster: 'cctv-production'

# Storage optimization
storage:
  tsdb:
    retention.time: 7d      # Keep 7 days (default 15d) - 50% reduction
    wal_compression: true   # Enable compression

scrape_configs:
  # Service discovery from Docker
  - job_name: 'docker-services'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock

    relabel_configs:
      # Only scrape containers with prometheus.scrape=true label
      - source_labels: [__meta_docker_container_label_prometheus_scrape]
        action: keep
        regex: true

      # Get port from label
      - source_labels: [__meta_docker_container_label_prometheus_port]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: $1:__meta_docker_container_label_prometheus_port

      # Get service name
      - source_labels: [__meta_docker_container_name]
        target_label: service

# Alerting
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/alerts/*.yml'
```

**Docker Compose Labels (for service discovery):**

```yaml
# docker-compose.yml

services:
  face-recognition:
    build: ./services/face-recognition
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
      prometheus.path: "/metrics"
```

**Prometheus Metrics in FastAPI:**

```python
# services/common/metrics.py

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Camera metrics
camera_status = Gauge(
    'camera_status',
    'Camera online status (1=online, 0=offline)',
    ['camera_id', 'location']
)

frames_processed = Counter(
    'frames_processed_total',
    'Total frames processed',
    ['camera_id']
)

# Face recognition metrics
face_detection_latency = Histogram(
    'face_detection_latency_seconds',
    'Face detection processing time',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

faces_detected = Counter(
    'faces_detected_total',
    'Total faces detected',
    ['camera_id']
)

face_matches = Counter(
    'face_matches_total',
    'Successful face matches',
    ['person_id', 'camera_id']
)

# Database metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type='text/plain'
    )

# Middleware to track HTTP metrics
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

---

#### 4.2.2 Alert Rules

```yaml
# monitoring/prometheus/alerts/camera-alerts.yml

groups:
  - name: camera_alerts
    interval: 30s
    rules:
      # Camera offline (warning)
      - alert: CameraOfflineWarning
        expr: camera_status == 0
        for: 2m
        labels:
          severity: warning
          component: video_stream
        annotations:
          summary: "Camera {{ $labels.camera_id }} is offline"
          description: "Camera {{ $labels.camera_id }} at {{ $labels.location }} has been offline for 2 minutes"

      # Camera offline (critical)
      - alert: CameraOfflineCritical
        expr: camera_status == 0
        for: 10m
        labels:
          severity: critical
          component: video_stream
        annotations:
          summary: "CRITICAL: Camera {{ $labels.camera_id }} offline >10 min"
          description: "Camera {{ $labels.camera_id }} requires immediate attention"

      # Low frame rate
      - alert: CameraLowFPS
        expr: rate(frames_processed_total[1m]) < 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Camera {{ $labels.camera_id }} low FPS"
          description: "FPS is {{ $value | humanize }}"

  - name: system_alerts
    interval: 1m
    rules:
      # High CPU
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.service }}"
          description: "CPU usage is {{ $value | humanize }}%"

      # High memory
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 3000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.service }}"
          description: "Memory usage is {{ $value | humanize }} MB"

      # Database slow queries
      - alert: DatabaseSlowQueries
        expr: histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Database queries are slow"
          description: "95th percentile query time is {{ $value | humanize }}s"
```

---

### 4.3 Logging Infrastructure

#### 4.3.1 Structured Logging with Loki

**Log Format (JSON):**

```python
# services/common/logging_config.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for Loki"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'service': os.getenv('SERVICE_NAME', 'unknown'),
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'camera_id'):
            log_data['camera_id'] = record.camera_id

        # Add exception info
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }

        return json.dumps(log_data)

# Setup logging
def setup_logging(service_name: str):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)

    return logger
```

**Loki Configuration:**

```yaml
# monitoring/loki/loki-config.yaml

auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2025-01-01
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb:
    directory: /loki/index
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

# Retention (7 days hot + 30 days archive)
chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h  # 30 days total
```

**Promtail (Log Shipper) Configuration:**

```yaml
# monitoring/promtail/promtail-config.yaml

server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # Scrape Docker container logs
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock

    relabel_configs:
      # Get container name
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'

      # Get service name from label
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'

      # Get project name
      - source_labels: ['__meta_docker_container_label_com_docker_compose_project']
        target_label: 'project'

    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            level: level
            timestamp: timestamp
            message: message
            camera_id: camera_id
            user_id: user_id

      # Set log level label
      - labels:
          level:
          camera_id:
          user_id:
```

---

### 4.4 Health Checks & Circuit Breakers

#### 4.4.1 Health Check Endpoints

```python
# services/common/health.py

from fastapi import APIRouter, Response
from sqlalchemy import text

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Quick health check (< 100ms)
    Used by Docker, load balancers
    """
    return {"status": "healthy"}

@router.get("/ready")
async def readiness_check(
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_db)
):
    """
    Readiness check - verify dependencies
    Used by Kubernetes, orchestration
    """
    checks = {}

    # Check Redis
    try:
        await redis.ping()
        checks['redis'] = 'healthy'
    except Exception as e:
        checks['redis'] = f'unhealthy: {str(e)}'

    # Check Database
    try:
        await db.execute(text("SELECT 1"))
        checks['database'] = 'healthy'
    except Exception as e:
        checks['database'] = f'unhealthy: {str(e)}'

    # Check Camera connections (for video service)
    if hasattr(app.state, 'stream_manager'):
        online_count = sum(1 for cam in app.state.stream_manager.streams.values() if cam.is_connected)
        total_count = len(app.state.stream_manager.streams)
        checks['cameras'] = f'{online_count}/{total_count} online'

    # Determine overall status
    all_healthy = all('healthy' in str(status) for status in checks.values())
    status_code = 200 if all_healthy else 503

    return Response(
        content=json.dumps({
            'status': 'ready' if all_healthy else 'not_ready',
            'checks': checks
        }),
        status_code=status_code,
        media_type='application/json'
    )
```

---

#### 4.4.2 Circuit Breaker for IoT APIs

```python
# services/common/circuit_breaker.py

from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for external API calls"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None

    def is_open(self) -> bool:
        """Check if circuit is open"""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).seconds
                if elapsed > self.recovery_timeout:
                    logger.info("Circuit breaker entering half-open state")
                    self.state = CircuitState.HALF_OPEN
                    return False
            return True
        return False

    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.last_success_time = datetime.utcnow()

        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker recovered, closing")
            self.state = CircuitState.CLOSED

    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.warning(f"Circuit breaker opening after {self.failure_count} failures")
                self.state = CircuitState.OPEN

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.is_open():
            raise CircuitBreakerOpenError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result

        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Usage in IoT adapter
class IoTAdapterWithCircuitBreaker:
    def __init__(self):
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )

    async def fetch_data(self):
        """Fetch data with circuit breaker protection"""
        try:
            return await self.circuit_breaker.call(self._call_api)

        except CircuitBreakerOpenError:
            logger.warning("Circuit breaker open, using cached data")
            return await self._get_cached_data()

    async def _call_api(self):
        """Actual API call"""
        response = await self.http_client.get(self.api_url)
        response.raise_for_status()
        return response.json()
```

**Benefits:**
- ✅ **Prevents cascade failures**: Don't hammer failing APIs
- ✅ **Automatic recovery**: Tests every 60 seconds
- ✅ **Fast failure**: Return cached data immediately when open
- ✅ **Gradual recovery**: Half-open state tests before full recovery

---

## 5. Part 4: DevOps & Deployment

### 5.1 Docker Compose Configuration

```yaml
# docker-compose.yml

version: '3.8'

services:
  # ─────────────────────────────────────────
  # Infrastructure Services
  # ─────────────────────────────────────────

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: cctv-timescaledb
    environment:
      POSTGRES_DB: ${DB_NAME:-cctv_production}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
      POSTGRES_INITDB_ARGS: --auth-host=scram-sha-256
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "127.0.0.1:5432:5432"  # Only localhost (security)
    networks:
      - cctv-network
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: cctv-redis
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - cctv-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  # ─────────────────────────────────────────
  # API Gateway
  # ─────────────────────────────────────────

  nginx:
    image: nginx:alpine
    container_name: cctv-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./dashboard/build:/usr/share/nginx/html:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - cctv-network
    depends_on:
      - auth-gateway
      - websocket-service
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M
    restart: unless-stopped

  auth-gateway:
    build:
      context: ./services/auth-gateway
      dockerfile: Dockerfile
    container_name: cctv-auth-gateway
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
    restart: unless-stopped

  # ─────────────────────────────────────────
  # Core Services
  # ─────────────────────────────────────────

  video-stream:
    build:
      context: ./services/video-stream
      dockerfile: Dockerfile
    container_name: cctv-video-stream
    environment:
      - REDIS_URL=redis://redis:6379/0
      - CAM001_RTSP_URL=${CAM001_RTSP_URL}
      - CAM002_RTSP_URL=${CAM002_RTSP_URL}
      - CAM003_RTSP_URL=${CAM003_RTSP_URL}
      - CAM004_RTSP_URL=${CAM004_RTSP_URL}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - cctv-network
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
    restart: unless-stopped

  face-recognition:
    build:
      context: ./services/face-recognition
      dockerfile: Dockerfile
    container_name: cctv-face-recognition
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - MODEL_PATH=/models
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - model-data:/models:ro
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
      - video-stream
    deploy:
      replicas: 2  # 2 workers for load balancing
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
    restart: unless-stopped

  person-counting:
    build:
      context: ./services/person-counting
      dockerfile: Dockerfile
    container_name: cctv-person-counting
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
      - video-stream
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
    labels:
      prometheus.scrape: "true"
      prometheus.port: "8000"
    restart: unless-stopped

  # ─────────────────────────────────────────
  # IoT Adapter Services
  # ─────────────────────────────────────────

  iot-hvac:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-hvac
    command: python -m adapters.hvac
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - HVAC_API_URL=${HVAC_API_URL}
      - HVAC_API_KEY=${HVAC_API_KEY}
      - HVAC_MODE=${HVAC_MODE:-polling}
      - HVAC_INTERVAL=${HVAC_INTERVAL:-300}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  iot-pump:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-pump
    command: python -m adapters.pump
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - PUMP_API_URL=${PUMP_API_URL}
      - PUMP_API_KEY=${PUMP_API_KEY}
      - PUMP_MODE=${PUMP_MODE:-polling}
      - PUMP_INTERVAL=${PUMP_INTERVAL:-300}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  iot-lighting:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-lighting
    command: python -m adapters.lighting
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - LIGHTING_API_URL=${LIGHTING_API_URL}
      - LIGHTING_API_KEY=${LIGHTING_API_KEY}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  iot-gate:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-gate
    command: python -m adapters.gate
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - GATE_API_URL=${GATE_API_URL}
      - GATE_API_KEY=${GATE_API_KEY}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  iot-lift:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-lift
    command: python -m adapters.lift
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - LIFT_API_URL=${LIFT_API_URL}
      - LIFT_API_KEY=${LIFT_API_KEY}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  iot-power:
    build:
      context: ./services/iot-adapters
      dockerfile: Dockerfile
    container_name: cctv-iot-power
    command: python -m adapters.power
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=redis://redis:6379/0
      - POWER_API_URL=${POWER_API_URL}
      - POWER_API_KEY=${POWER_API_KEY}
      - POWER_INTERVAL=${POWER_INTERVAL:-60}
    networks:
      - cctv-network
    depends_on:
      - timescaledb
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.2'
          memory: 256M
    restart: unless-stopped

  # ─────────────────────────────────────────
  # Real-Time Service
  # ─────────────────────────────────────────

  websocket-service:
    build:
      context: ./services/websocket
      dockerfile: Dockerfile
    container_name: cctv-websocket
    environment:
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - cctv-network
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped

  # ─────────────────────────────────────────
  # Monitoring Stack (Optional - Light Setup)
  # ─────────────────────────────────────────

  prometheus:
    image: prom/prometheus:latest
    container_name: cctv-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'
      - '--web.enable-lifecycle'
    volumes:
      - ./monitoring/prometheus:/etc/prometheus:ro
      - prometheus-data:/prometheus
    ports:
      - "127.0.0.1:9090:9090"
    networks:
      - cctv-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: cctv-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning:ro
    ports:
      - "127.0.0.1:3000:3000"
    networks:
      - cctv-network
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M
    restart: unless-stopped

  loki:
    image: grafana/loki:latest
    container_name: cctv-loki
    command: -config.file=/etc/loki/loki-config.yaml
    volumes:
      - ./monitoring/loki:/etc/loki:ro
      - loki-data:/loki
    ports:
      - "127.0.0.1:3100:3100"
    networks:
      - cctv-network
    deploy:
      resources:
        limits:
          cpus: '0.3'
          memory: 256M
    restart: unless-stopped

  promtail:
    image: grafana/promtail:latest
    container_name: cctv-promtail
    command: -config.file=/etc/promtail/promtail-config.yaml
    volumes:
      - ./monitoring/promtail:/etc/promtail:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock
    networks:
      - cctv-network
    depends_on:
      - loki
    restart: unless-stopped

networks:
  cctv-network:
    driver: bridge

volumes:
  db-data:
  redis-data:
  model-data:
  prometheus-data:
  grafana-data:
  loki-data:
```

---

### 5.2 Environment Management

**Three Environments:**

1. **Development** (`.env.dev`)
2. **Staging** (`.env.staging`)
3. **Production** (`.env.production`)

```bash
# .env.production

# Database
DATABASE_URL=postgresql://cctv_user:SecurePassword123@timescaledb:5432/cctv_production
DB_NAME=cctv_production
DB_USER=cctv_user
DB_PASSWORD=SecurePassword123

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars-long
SECRET_KEY=your-app-secret-key

# Camera RTSP URLs
CAM001_RTSP_URL=rtsp://192.168.1.101:554/stream1
CAM002_RTSP_URL=rtsp://192.168.1.102:554/stream1
CAM003_RTSP_URL=rtsp://192.168.1.103:554/stream1
CAM004_RTSP_URL=rtsp://192.168.1.104:554/stream1

# IoT System APIs
HVAC_API_URL=https://customer-iot.com/api/hvac
HVAC_API_KEY=customer_provided_key_hvac
HVAC_MODE=polling
HVAC_INTERVAL=300

PUMP_API_URL=https://customer-iot.com/api/pump
PUMP_API_KEY=customer_provided_key_pump

LIGHTING_API_URL=https://customer-iot.com/api/lighting
LIGHTING_API_KEY=customer_provided_key_lighting

GATE_API_URL=https://customer-iot.com/api/gate
GATE_API_KEY=customer_provided_key_gate

LIFT_API_URL=https://customer-iot.com/api/lift
LIFT_API_KEY=customer_provided_key_lift

POWER_API_URL=https://customer-iot.com/api/power
POWER_API_KEY=customer_provided_key_power
POWER_INTERVAL=60

# Monitoring
GRAFANA_PASSWORD=admin_secure_password

# Application
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

### 5.3 Deployment Strategy

**Manual Deployment Procedure:**

```bash
#!/bin/bash
# deploy.sh - Manual deployment script

set -e  # Exit on error

echo "🚀 Starting deployment..."

# 1. Pull latest code
echo "📦 Pulling latest code from git..."
git pull origin main

# 2. Backup database
echo "💾 Backing up database..."
./scripts/backup-database.sh

# 3. Stop services
echo "⏸️  Stopping services..."
docker-compose down

# 4. Build images
echo "🔨 Building Docker images..."
docker-compose build --no-cache

# 5. Run database migrations
echo "🗄️  Running database migrations..."
docker-compose run --rm face-recognition python -m alembic upgrade head

# 6. Start services
echo "▶️  Starting services..."
docker-compose up -d

# 7. Health check
echo "🏥 Checking service health..."
sleep 30  # Wait for services to start

for service in timescaledb redis video-stream face-recognition; do
    if docker-compose ps | grep $service | grep -q "Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
        docker-compose logs $service
        exit 1
    fi
done

# 8. Check endpoints
echo "🔍 Testing endpoints..."
curl -f http://localhost/health || { echo "❌ Health check failed"; exit 1; }
echo "✅ Health check passed"

echo "🎉 Deployment completed successfully!"
echo "📊 View logs: docker-compose logs -f"
echo "📈 View metrics: http://localhost:3000 (Grafana)"
```

---

### 5.4 Backup & Security

#### 5.4.1 Database Backup Script

```bash
#!/bin/bash
# scripts/backup-database.sh

set -e

# Configuration
BACKUP_DIR="/backups/timescaledb"
RETENTION_DAYS=30
DB_CONTAINER="cctv-timescaledb"
DB_NAME="cctv_production"
DB_USER="postgres"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/cctv_${TIMESTAMP}.sql.gz"

echo "Starting database backup: $BACKUP_FILE"

# Backup with pg_dump (custom format, compressed)
docker exec -t $DB_CONTAINER pg_dump \
    -U $DB_USER \
    -d $DB_NAME \
    --format=custom \
    --compress=9 \
    --verbose \
    | gzip > "$BACKUP_FILE"

echo "Backup completed: $(du -h $BACKUP_FILE | cut -f1)"

# Clean up old backups
echo "Cleaning up backups older than $RETENTION_DAYS days"
find "$BACKUP_DIR" -name "cctv_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup
echo "Verifying backup..."
gunzip -t "$BACKUP_FILE"
echo "✅ Backup verified successfully"

# Optional: Upload to cloud storage
# aws s3 cp "$BACKUP_FILE" s3://company-backups/cctv-db/

echo "✅ Backup complete!"
```

**Cron Setup (Daily 2 AM):**

```bash
# /etc/cron.d/cctv-backup

0 2 * * * /app/scripts/backup-database.sh >> /var/log/cctv-backup.log 2>&1
```

---

#### 5.4.2 Security Checklist

```markdown
# Security Checklist

## Before Deployment

### Secrets Management
- [ ] All secrets in .env files (not in code)
- [ ] .env files added to .gitignore
- [ ] Strong JWT secret (min 32 characters)
- [ ] Strong database password (min 16 characters)
- [ ] Strong Grafana admin password
- [ ] All API keys stored in environment variables

### Network Security
- [ ] SSL/TLS certificates installed (Let's Encrypt)
- [ ] Database port NOT exposed to public (127.0.0.1:5432 only)
- [ ] Redis port NOT exposed to public (127.0.0.1:6379 only)
- [ ] Firewall configured (allow only 80, 443)
- [ ] Docker network isolated (internal communication only)

### Authentication & Authorization
- [ ] JWT token expiration configured (3h for admin, 7d for viewer)
- [ ] Session management in Redis working
- [ ] Role-based access control tested
- [ ] API rate limiting enabled (Nginx + FastAPI)

### Database Security
- [ ] PostgreSQL password authentication (scram-sha-256)
- [ ] Database user with minimal privileges (not superuser)
- [ ] SSL/TLS for database connections (production)
- [ ] Regular backups configured (daily 2 AM)
- [ ] Backup verification automated

### Application Security
- [ ] No sensitive data logged (passwords, tokens)
- [ ] SQL injection protection (parameterized queries)
- [ ] XSS protection (sanitized inputs)
- [ ] CORS configured correctly (allowed origins)
- [ ] Security headers in Nginx (X-Frame-Options, etc.)

### Monitoring & Alerts
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards configured
- [ ] Alert rules defined (camera offline, high CPU, etc.)
- [ ] Alert notifications configured (email/Slack)
- [ ] Log aggregation working (Loki + Promtail)

## After Deployment

### Verification
- [ ] All services running (docker-compose ps)
- [ ] Health checks passing (/health, /ready)
- [ ] No errors in logs (docker-compose logs)
- [ ] Cameras connecting successfully
- [ ] Face recognition working
- [ ] IoT data being collected
- [ ] WebSocket real-time updates working
- [ ] Metrics visible in Grafana
- [ ] Logs searchable in Grafana

### Testing
- [ ] Login with all roles (admin, operator, viewer)
- [ ] Upload test photos for face registration
- [ ] Verify face recognition events in database
- [ ] Check person counting accuracy
- [ ] Verify IoT data in dashboard
- [ ] Test alert notifications

### Documentation
- [ ] Deployment runbook updated
- [ ] API documentation current
- [ ] Monitoring dashboard URLs documented
- [ ] Emergency contact information documented
- [ ] Backup restore procedure tested

## Ongoing Security

### Weekly
- [ ] Review logs for suspicious activity
- [ ] Check failed login attempts
- [ ] Verify all cameras online
- [ ] Check disk space usage

### Monthly
- [ ] Update Docker images (security patches)
- [ ] Review user access (remove inactive users)
- [ ] Test backup restore procedure
- [ ] Review alert rules

### Quarterly
- [ ] Security audit
- [ ] Penetration testing (if required)
- [ ] Review and rotate API keys
- [ ] Update dependencies
```

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1:**
- ✅ Set up development environment
- ✅ Initialize Git repository
- ✅ Create project structure (13 services)
- ✅ Set up Docker Compose
- ✅ Deploy TimescaleDB + Redis locally
- ✅ Initialize database schema (from Meeting 3)
- ✅ Set up Prometheus + Grafana (light config)

**Week 2:**
- ✅ Implement base service template (FastAPI skeleton)
- ✅ Implement authentication service (JWT + Redis session)
- ✅ Implement API gateway (Nginx + FastAPI routing)
- ✅ Set up logging infrastructure (JSON logging)
- ✅ Test auth flow end-to-end

**Deliverable:** Working authentication + basic infrastructure

---

### Phase 2: Core Services (Weeks 3-6)

**Week 3:**
- ✅ Implement Video Stream Service
  - RTSP connection with exponential backoff
  - Frame extraction (5 FPS)
  - Publish to Redis Streams
  - Camera health monitoring
- ✅ Test with 1 camera

**Week 4:**
- ✅ Implement Face Recognition Service
  - YOLO face detection
  - ArcFace embedding generation
  - pgvector similarity search
  - Voting mechanism (Meeting 1)
- ✅ Test face registration (3-5 photos)
- ✅ Test face recognition accuracy

**Week 5:**
- ✅ Implement Person Counting Service
  - DeepSORT tracking
  - Line crossing detection
  - Count aggregation
- ✅ Configure counting lines for 4 cameras
- ✅ Test counting accuracy

**Week 6:**
- ✅ Implement REST APIs (all endpoints from Section 3.2)
- ✅ Implement WebSocket service (11 channels)
- ✅ Integration testing (all core services)

**Deliverable:** Fully functional CCTV + face recognition + counting

---

### Phase 3: IoT Integration (Weeks 7-9)

**Week 7:**
- ✅ Implement IoT adapter base class
- ✅ Implement 3 adapters: HVAC, Pump, Lighting
- ✅ Test polling mode
- ✅ Test webhook mode

**Week 8:**
- ✅ Implement 3 adapters: Gate, Lift, Power
- ✅ Configure all 6 IoT systems
- ✅ Test data collection
- ✅ Verify data in TimescaleDB

**Week 9:**
- ✅ Implement error handling (circuit breakers, retries)
- ✅ Implement caching for IoT API failures
- ✅ Set up alerts for IoT API downtime
- ✅ Integration testing (all services)

**Deliverable:** Complete IoT integration (6 systems)

---

### Phase 4: Operations & Deployment (Weeks 10-12)

**Week 10:**
- ✅ Finalize monitoring dashboards (Grafana)
- ✅ Configure alert rules (Prometheus)
- ✅ Set up log aggregation (Loki)
- ✅ Implement backup automation (daily 2 AM)
- ✅ Security hardening

**Week 11:**
- ✅ Staging deployment
- ✅ Load testing (simulate 4 cameras + 6 IoT)
- ✅ Performance tuning
- ✅ Bug fixes

**Week 12:**
- ✅ Production deployment
- ✅ Customer training
- ✅ Documentation handover
- ✅ Post-deployment monitoring (1 week)

**Deliverable:** Production-ready system

---

## 7. Resource Planning

### 7.1 Server Specifications

**Development/Testing:**
- **vCPU:** 4
- **RAM:** 8 GB
- **Disk:** 50 GB SSD
- **Cost:** ~1,500 THB/month

**Production (Recommended):**
- **vCPU:** 6 (to handle peak load)
- **RAM:** 12 GB (comfortable headroom)
- **Disk:** 100 GB SSD
- **Cost:** ~2,500-3,000 THB/month

**Production + Separate Monitoring:**
- **Main Server:** 4 vCPU, 8 GB RAM (~2,000 THB/month)
- **Monitoring VPS:** 1 vCPU, 2 GB RAM (~300 THB/month)
- **Total:** ~2,300 THB/month

---

### 7.2 Resource Allocation (Production)

**On 6 vCPU, 12 GB RAM Server:**

| Component | vCPU | RAM | Notes |
|-----------|------|-----|-------|
| **Core Services** |
| Face Recognition (x2) | 2.0 | 4 GB | 2 replicas for load balancing |
| Video Stream | 1.0 | 2 GB | 4 cameras |
| Person Counting | 1.0 | 2 GB | DeepSORT tracking |
| **Infrastructure** |
| TimescaleDB | 1.0 | 2 GB | With compression |
| Redis | 0.5 | 512 MB | Message bus + cache |
| Nginx + Auth Gateway | 0.3 | 512 MB | Combined |
| **IoT Adapters** |
| 6 adapters (HVAC, Pump, Lighting, Gate, Lift, Power) | 1.2 | 1.5 GB | Total for all 6 |
| **Support Services** |
| WebSocket + Auth + User + Alert | 0.5 | 512 MB | Combined |
| **Monitoring (Light)** |
| Prometheus + Grafana + Loki | 0.5 | 512 MB | Light config |
| **Total** | **8.0** | **13 GB** |

**Issue:** Exceeds 6 vCPU / 12 GB

---

### 7.3 Optimization Strategies

**Option 1: Reduce Service Count** (Recommended for MVP)

Consolidate services:
- **Combine IoT adapters** into single multi-adapter service (saves 1 vCPU, 1 GB)
- **Remove monitoring** initially (saves 0.5 vCPU, 512 MB)
- **Use Grafana Cloud** free tier (external monitoring)

**Result:** ~6.5 vCPU, 11.5 GB (fits in 6 vCPU / 12 GB)

---

**Option 2: Upgrade Server** (Recommended for Production)

- Upgrade to **6 vCPU, 12 GB** (adds ~1,000 THB/month)
- Or use **4 vCPU + 8 GB main + 1 vCPU + 2 GB monitoring** (adds ~300 THB/month)

---

**Option 3: Resource Limits** (Short-term)

Set strict Docker resource limits to prevent resource exhaustion.

---

## 8. Next Steps

### Immediate Actions

1. **Review & Approve Architecture**
   - Review this document with stakeholders
   - Approve technology choices
   - Confirm resource allocation

2. **Set Up Development Environment**
   - Provision development server
   - Install Docker + Docker Compose
   - Clone repository structure

3. **Initialize Database**
   - Deploy TimescaleDB
   - Run schema from Meeting 3
   - Test pgvector extension

4. **Begin Phase 1 Implementation**
   - Week 1 tasks from roadmap
   - Set up CI/CD (optional for MVP)

---

### Documentation To Create

1. **API Documentation**
   - OpenAPI/Swagger specs
   - Postman collections
   - API usage examples

2. **Runbooks**
   - Deployment procedure
   - Backup & restore procedure
   - Troubleshooting guide
   - Emergency contacts

3. **User Guides**
   - Admin guide (face registration, user management)
   - Operator guide (monitoring dashboards)
   - API integration guide (for customer)

---

### Future Enhancements

**Phase 5 (Post-Launch):**
- Mobile app (React Native)
- Advanced analytics (ML-based anomaly detection)
- Predictive maintenance (equipment failure prediction)
- Multi-building support
- Advanced reporting (custom BI queries)

**Scalability:**
- If cameras grow to 50+: Migrate to Kubernetes
- If buildings grow to 10+: Multi-tenancy architecture
- If data grows to TB+: Add data warehouse (ClickHouse)

---

## Meeting Summary

**Duration:** 180 minutes (3 hours)
**Decisions Made:** 50+ critical architectural decisions
**Services Designed:** 13 microservices
**APIs Specified:** 20+ REST endpoints + 11 WebSocket channels
**Error Scenarios Covered:** 5 major failure modes
**Monitoring Metrics:** 30+ tracked metrics

**This document, combined with:**
- Meeting 1 (Face Recognition - 12,000 words)
- Meeting 2 (Person Counting - 11,000 words)
- Meeting 3 (Database Architecture - 15,000 words)
- **Meeting 4 (System Architecture - This document)**

**Provides a complete, production-ready technical blueprint for implementation.**

---

**Document Version:** 1.0
**Last Updated:** November 4, 2025
**Status:** Complete - Ready for Implementation

---

**Next Meeting (If Needed):**
- Review implementation progress after Phase 1
- Address any technical blockers
- Refine based on real-world testing
