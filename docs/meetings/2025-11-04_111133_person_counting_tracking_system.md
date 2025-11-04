# Meeting Notes: Person Counting & Tracking System

**Date:** 2025-11-04
**Time:** 11:11 AM
**Duration:** ~60 minutes
**Meeting Type:** System Design Discussion
**Project:** CCTV Face Recognition System (4 Cameras)

---

## Attendees
- Development Team
- Technical Lead (Claude)

---

## Meeting Agenda
1. Person Detection vs Face Recognition - Understanding the Difference
2. Counting Requirements Per Camera
3. Real-time Dashboard Design
4. Restricted Zone Monitoring & Alerts
5. Historical Data & Reporting
6. Counting Line Configuration (UI-based)
7. Alert System Design
8. Complete System Architecture

---

## 1. Person Detection vs Face Recognition

### Key Distinction

**Person Detection (People Counting/Tracking):**
```
Purpose: Count and track ALL people (no identity required)
Speed: Very fast (30-40 FPS)
Limitations: None (works with masks, sunglasses, any person)
Registration: Not required
Output: Anonymous tracking (Track ID only)

Use Cases:
✅ Traffic counting (in/out)
✅ Occupancy monitoring
✅ Movement pattern analysis
✅ Queue management
✅ Crowd density monitoring
```

**Face Recognition (Identity Detection):**
```
Purpose: Identify WHO the person is
Speed: Slower (processed every 30 frames)
Limitations: Affected by masks, sunglasses, angles
Registration: Required (database of faces)
Output: Identity + confidence score

Use Cases:
✅ Access control
✅ Attendance tracking
✅ VIP recognition
✅ Security watchlist
✅ Personalized services
```

### Combined Approach for This Project

```
┌────────────────────────────────────────────────┐
│  CCTV System - Dual Processing                │
├────────────────────────────────────────────────┤
│                                                │
│  Layer 1: Person Detection (Every frame)      │
│  - Track ALL people                            │
│  - Count in/out                                │
│  - Monitor zones                               │
│  - Generate statistics                         │
│                                                │
│  Layer 2: Face Recognition (Every 30 frames)  │
│  - Identify registered people                  │
│  - Log entry/exit times                        │
│  - Access control                              │
│  - Security alerts                             │
│                                                │
│  Result: Complete people analytics + identity │
└────────────────────────────────────────────────┘
```

---

## 2. Counting Requirements Per Camera

### Decision: All 4 Cameras Count IN / OUT / TOTAL

**Camera Configuration:**

| Camera | Location | Primary Function | Counting Type | Additional Features |
|--------|----------|------------------|---------------|---------------------|
| CAM 1 | Main Entrance | Entry/Exit point | Bidirectional | Face recognition priority |
| CAM 2 | Lobby | Traffic monitoring | Bidirectional | Zone-based counting |
| CAM 3 | Floor 2 | Area monitoring | Bidirectional | Restricted zone alerts |
| CAM 4 | Exit | Exit point | Bidirectional | Optional face recognition |

### Data Collected Per Camera

```python
camera_metrics = {
    'camera_id': 'CAM001',
    'camera_name': 'Main Entrance',

    # Real-time counts
    'count_in': 150,        # Total people entered
    'count_out': 145,       # Total people exited
    'current_count': 5,     # People in area now

    # Tracking statistics
    'active_tracks': 3,     # Currently tracking
    'total_unique': 150,    # Unique people (by Track ID)

    # Performance
    'fps': 28.5,
    'detection_rate': 0.98,

    # Timestamp
    'last_update': '2025-11-04 11:11:33'
}
```

### Counting Logic

**Line Crossing Detection:**

```python
class LineCounter:
    """
    Count people crossing virtual line
    """

    def __init__(self, line_y=400):
        self.line_y = line_y
        self.previous_positions = {}
        self.counted_ids = {
            'in': set(),
            'out': set()
        }
        self.count_in = 0
        self.count_out = 0

    def update(self, persons):
        """
        Update counts based on tracked persons

        Args:
            persons: List of tracked person objects
                     [{track_id, center, bbox, ...}, ...]
        """
        for person in persons:
            track_id = person['track_id']
            current_y = person['center'][1]  # Y-coordinate

            # Check if we've seen this person before
            if track_id in self.previous_positions:
                prev_y = self.previous_positions[track_id]

                # Crossing from top to bottom (ENTERING)
                if prev_y < self.line_y and current_y >= self.line_y:
                    if track_id not in self.counted_ids['in']:
                        self.count_in += 1
                        self.counted_ids['in'].add(track_id)
                        self.log_event(track_id, 'in')

                # Crossing from bottom to top (EXITING)
                elif prev_y > self.line_y and current_y <= self.line_y:
                    if track_id not in self.counted_ids['out']:
                        self.count_out += 1
                        self.counted_ids['out'].add(track_id)
                        self.log_event(track_id, 'out')

            # Update position
            self.previous_positions[track_id] = current_y

        return {
            'count_in': self.count_in,
            'count_out': self.count_out,
            'current': self.count_in - self.count_out
        }
```

**Key Feature: Avoid Double Counting**

```
Problem: Person hovers near line
┌────────────────────────────┐
│  Frame 1: y=398 (above)    │
│  Frame 2: y=402 (below)    │ ✅ Count +1
│  Frame 3: y=399 (above)    │ ❌ Don't count again!
│  Frame 4: y=403 (below)    │ ❌ Don't count again!
└────────────────────────────┘

Solution: Track counted IDs
counted_ids = {12, 15, 23, ...}
Only count each Track ID once per direction
```

---

## 3. Real-time Dashboard Design

### Decision: Live Dashboard with Delay Tolerance

**Dashboard Requirements:**
- ✅ Real-time updates (acceptable delay: 1-2 seconds)
- ✅ Display all 4 cameras simultaneously
- ✅ Live counts (in/out/current)
- ✅ Visual alerts for violations
- ✅ Real-time graphs
- ✅ Status indicators

### Dashboard Layout

```
╔═══════════════════════════════════════════════════════════════╗
║  CCTV People Counting System          🔴 LIVE  11:11:33      ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       ║
║  │ 📹 CAM 1     │  │ 📹 CAM 2     │  │ 📹 CAM 3     │       ║
║  │ Entrance     │  │ Lobby        │  │ Floor 2      │       ║
║  ├──────────────┤  ├──────────────┤  ├──────────────┤       ║
║  │ ↑ IN:  150   │  │ ↑ IN:  120   │  │ ↑ IN:  80    │       ║
║  │ ↓ OUT: 145   │  │ ↓ OUT: 118   │  │ ↓ OUT: 75    │       ║
║  │ 👥 NOW: 5    │  │ 👥 NOW: 2    │  │ 👥 NOW: 5    │       ║
║  │              │  │              │  │              │       ║
║  │ ✅ Normal    │  │ ✅ Normal    │  │ ⚠️ WARNING   │       ║
║  │ FPS: 28      │  │ FPS: 30      │  │ FPS: 27      │       ║
║  └──────────────┘  └──────────────┘  └──────────────┘       ║
║                                                               ║
║  ┌──────────────┐  ┌─────────────────────────────────────┐  ║
║  │ 📹 CAM 4     │  │  🚨 ACTIVE ALERTS                   │  ║
║  │ Exit         │  ├─────────────────────────────────────┤  ║
║  ├──────────────┤  │ 🔴 11:11 - CAM3: Server Room       │  ║
║  │ ↑ IN:  148   │  │         Unauthorized person!       │  ║
║  │ ↓ OUT: 147   │  │         [View Camera] [Dismiss]    │  ║
║  │ 👥 NOW: 1    │  │                                     │  ║
║  │              │  │ 🟡 11:05 - CAM2: Meeting Room      │  ║
║  │ ✅ Normal    │  │         Overcrowding (12/10)        │  ║
║  │ FPS: 29      │  │         [View Camera] [Dismiss]    │  ║
║  └──────────────┘  └─────────────────────────────────────┘  ║
║                                                               ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │  📈 Traffic Trend (Last Hour)                        │   ║
║  │                                                       │   ║
║  │   50│        ╱╲                                      │   ║
║  │   40│       ╱  ╲     ╱╲                              │   ║
║  │   30│      ╱    ╲   ╱  ╲                             │   ║
║  │   20│     ╱      ╲ ╱    ╲╱                           │   ║
║  │   10│    ╱        ╲╱                                 │   ║
║  │    0└─────────────────────────────────               │   ║
║  │     10:15  10:30  10:45  11:00  11:15                │   ║
║  │                                                       │   ║
║  │     CAM1 ━━  CAM2 ━━  CAM3 ━━  CAM4 ━━             │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                               ║
║  Building Status: 🟢 Normal | Total People: 13               ║
║  Peak Today: 85 (09:00-10:00) | Alerts: 2 Active             ║
╚═══════════════════════════════════════════════════════════════╝
```

### Technology Stack for Dashboard

**Backend (Python):**
```python
# FastAPI for REST API + WebSocket
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

# Store real-time data
realtime_data = {}
websocket_clients = []

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket for real-time updates
    """
    await websocket.accept()
    websocket_clients.append(websocket)

    try:
        while True:
            # Send updates every 1 second
            await websocket.send_json(realtime_data)
            await asyncio.sleep(1)
    except:
        websocket_clients.remove(websocket)

@app.get("/api/cameras")
async def get_all_cameras():
    """
    REST API: Get all camera data
    """
    return realtime_data

@app.get("/api/camera/{camera_id}")
async def get_camera_data(camera_id: str):
    """
    REST API: Get specific camera data
    """
    return realtime_data.get(camera_id, {})

# Update function (called from counting system)
async def broadcast_update(camera_id, data):
    """
    Broadcast updates to all connected clients
    """
    realtime_data[camera_id] = data

    # Send to all WebSocket clients
    for client in websocket_clients:
        try:
            await client.send_json({
                'camera_id': camera_id,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
        except:
            websocket_clients.remove(client)
```

**Frontend (HTML + JavaScript):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>CCTV Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div id="dashboard">
        <!-- Camera grids -->
        <div class="camera-grid">
            <div id="cam1" class="camera-card"></div>
            <div id="cam2" class="camera-card"></div>
            <div id="cam3" class="camera-card"></div>
            <div id="cam4" class="camera-card"></div>
        </div>

        <!-- Alerts -->
        <div id="alerts" class="alert-panel"></div>

        <!-- Graph -->
        <canvas id="trafficChart"></canvas>
    </div>

    <script>
        // WebSocket connection
        const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // Update camera cards
            for (const [cameraId, cameraData] of Object.entries(data)) {
                const card = document.getElementById(cameraId.toLowerCase());
                if (card) {
                    card.innerHTML = `
                        <h3>📹 ${cameraData.name}</h3>
                        <div class="counts">
                            <p>↑ IN: ${cameraData.count_in}</p>
                            <p>↓ OUT: ${cameraData.count_out}</p>
                            <p>👥 NOW: ${cameraData.current_count}</p>
                        </div>
                        <div class="status ${cameraData.status}">
                            ${cameraData.status_text}
                        </div>
                    `;
                }
            }

            // Update graph
            updateChart(data);
        }

        // Chart.js for real-time graph
        const ctx = document.getElementById('trafficChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {label: 'CAM1', data: [], borderColor: 'blue'},
                    {label: 'CAM2', data: [], borderColor: 'green'},
                    {label: 'CAM3', data: [], borderColor: 'orange'},
                    {label: 'CAM4', data: [], borderColor: 'red'}
                ]
            },
            options: {
                responsive: true,
                animation: {duration: 500}
            }
        });

        function updateChart(data) {
            // Add new data point
            const now = new Date().toLocaleTimeString();
            chart.data.labels.push(now);

            // Keep only last 60 points (1 hour if updating every minute)
            if (chart.data.labels.length > 60) {
                chart.data.labels.shift();
            }

            // Update each camera's data
            for (let i = 1; i <= 4; i++) {
                const cameraData = data[`cam${i}`];
                if (cameraData) {
                    chart.data.datasets[i-1].data.push(cameraData.current_count);

                    if (chart.data.datasets[i-1].data.length > 60) {
                        chart.data.datasets[i-1].data.shift();
                    }
                }
            }

            chart.update();
        }
    </script>
</body>
</html>
```

---

## 4. Restricted Zone Monitoring

### Zone Types and Configuration

**Zone Classifications:**

```python
ZONE_TYPES = {
    'restricted': {
        'max_people': 0,           # No entry allowed
        'color': 'red',
        'alert_level': 'critical',
        'notification': ['email', 'line', 'sms'],
        'action': 'immediate_response'
    },
    'limited': {
        'max_people': 10,          # Capacity limit
        'color': 'yellow',
        'alert_level': 'warning',
        'notification': ['line'],
        'action': 'monitor'
    },
    'monitored': {
        'max_people': 50,          # Watch only
        'color': 'blue',
        'alert_level': 'info',
        'notification': ['log'],
        'action': 'track'
    }
}
```

### Zone Definition

**Visual Configuration:**

```
Camera 3 Layout:
┌─────────────────────────────────────────┐
│                                         │
│  ┌────────────┐  ← Server Room          │
│  │ 🚫 Zone 1  │     (Restricted)        │
│  │ Max: 0     │     Red overlay         │
│  └────────────┘                         │
│                                         │
│         ┌──────────────────┐            │
│         │ ⚠️ Zone 2        │            │
│         │ VIP Meeting      │            │
│         │ Max: 10 people   │            │
│         └──────────────────┘            │
│                  ↑                      │
│         Yellow overlay                  │
│                                         │
│  👥👥  ← Normal area (no limit)         │
│                                         │
└─────────────────────────────────────────┘
```

### Zone Violation Detection

```python
class ZoneMonitor:
    """
    Monitor restricted zones for violations
    """

    def __init__(self, zones):
        self.zones = zones
        self.active_violations = {}

    def check_violations(self, persons):
        """
        Check if any person entered restricted zone

        Returns:
            List of violations
        """
        violations = []

        for zone in self.zones:
            if not zone['enabled']:
                continue

            # Count people in this zone
            people_in_zone = []

            for person in persons:
                center_x, center_y = person['center']

                # Check if person is inside polygon
                if self.point_in_polygon(
                    (center_x, center_y),
                    zone['polygon']
                ):
                    people_in_zone.append(person)

            count = len(people_in_zone)

            # Check for violations
            if zone['type'] == 'restricted' and count > 0:
                # CRITICAL: Someone in restricted area!
                violation = {
                    'zone_id': zone['zone_id'],
                    'zone_name': zone['name'],
                    'type': 'unauthorized_access',
                    'severity': 'critical',
                    'count': count,
                    'people': people_in_zone,
                    'timestamp': datetime.now(),
                    'camera_id': zone['camera_id']
                }
                violations.append(violation)

            elif zone['type'] == 'limited' and count > zone['max_people']:
                # WARNING: Overcrowding
                violation = {
                    'zone_id': zone['zone_id'],
                    'zone_name': zone['name'],
                    'type': 'overcrowding',
                    'severity': 'warning',
                    'count': count,
                    'max_allowed': zone['max_people'],
                    'exceeded_by': count - zone['max_people'],
                    'timestamp': datetime.now(),
                    'camera_id': zone['camera_id']
                }
                violations.append(violation)

        return violations

    def point_in_polygon(self, point, polygon):
        """
        Ray casting algorithm to check if point is inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
```

### Alert System

**Multi-channel Notification:**

```python
class AlertManager:
    """
    Send alerts through multiple channels
    """

    def __init__(self, config):
        self.line_notifier = LineNotifier(config['line_token'])
        self.email_notifier = EmailNotifier(config['smtp'])
        self.sms_notifier = SMSNotifier(config['sms'])

    def send_violation_alert(self, violation, snapshot=None):
        """
        Send alert based on severity
        """
        if violation['severity'] == 'critical':
            # CRITICAL: All channels
            self.line_notifier.send_critical(violation)
            self.email_notifier.send_with_snapshot(violation, snapshot)
            self.sms_notifier.send_urgent(violation)

            # Log to database
            self.log_incident(violation)

        elif violation['severity'] == 'warning':
            # WARNING: Line + Log
            self.line_notifier.send_warning(violation)
            self.log_event(violation)

        elif violation['severity'] == 'info':
            # INFO: Log only
            self.log_event(violation)

# Line Notify Example
class LineNotifier:
    def send_critical(self, violation):
        message = f"""
🚨 CRITICAL ALERT!

Zone: {violation['zone_name']}
Type: Unauthorized Access
People: {violation['count']}
Time: {violation['timestamp'].strftime('%H:%M:%S')}

⚠️ IMMEDIATE ACTION REQUIRED!
Camera: {violation['camera_id']}
        """

        self.send(message)
```

---

## 5. Historical Data & Reporting

### Database Schema (PostgreSQL)

```sql
-- Counting events (every crossing)
CREATE TABLE counting_events (
    id BIGSERIAL PRIMARY KEY,
    camera_id VARCHAR(10) NOT NULL,
    track_id INTEGER NOT NULL,
    event_type VARCHAR(10) NOT NULL,  -- 'in' or 'out'
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    zone_id VARCHAR(10),
    confidence REAL,

    INDEX idx_camera_time (camera_id, timestamp),
    INDEX idx_time (timestamp)
);

-- Hourly aggregates
CREATE TABLE hourly_summary (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour < 24),
    count_in INTEGER DEFAULT 0,
    count_out INTEGER DEFAULT 0,
    peak_occupancy INTEGER DEFAULT 0,
    avg_occupancy REAL DEFAULT 0,

    UNIQUE(camera_id, date, hour)
);

-- Daily summary
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    total_in INTEGER DEFAULT 0,
    total_out INTEGER DEFAULT 0,
    peak_hour INTEGER,
    peak_count INTEGER,
    avg_count REAL DEFAULT 0,

    UNIQUE(camera_id, date)
);

-- Zone violations
CREATE TABLE zone_violations (
    id BIGSERIAL PRIMARY KEY,
    camera_id VARCHAR(10) NOT NULL,
    zone_id VARCHAR(10) NOT NULL,
    zone_name VARCHAR(100),
    violation_type VARCHAR(50),
    severity VARCHAR(20),
    person_count INTEGER,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP,
    snapshot_path TEXT,

    INDEX idx_zone_time (zone_id, timestamp),
    INDEX idx_severity (severity, timestamp)
);
```

### Report Types

**1. Daily Report**
```python
def generate_daily_report(camera_id, date):
    """
    Daily traffic report with hourly breakdown
    """
    query = """
        SELECT
            hour,
            count_in,
            count_out,
            peak_occupancy,
            avg_occupancy
        FROM hourly_summary
        WHERE camera_id = %s AND date = %s
        ORDER BY hour
    """

    hourly_data = db.execute(query, (camera_id, date))

    # Summary
    total_in = sum(h['count_in'] for h in hourly_data)
    total_out = sum(h['count_out'] for h in hourly_data)
    peak_hour = max(hourly_data, key=lambda x: x['count_in'])

    return {
        'date': date,
        'camera_id': camera_id,
        'total_in': total_in,
        'total_out': total_out,
        'current': total_in - total_out,
        'peak_hour': peak_hour['hour'],
        'peak_count': peak_hour['count_in'],
        'hourly_breakdown': hourly_data
    }
```

**2. Weekly Report**
```python
def generate_weekly_report(camera_id, start_date, end_date):
    """
    Weekly traffic analysis
    """
    query = """
        SELECT
            date,
            total_in,
            total_out,
            peak_count
        FROM daily_stats
        WHERE camera_id = %s
          AND date BETWEEN %s AND %s
        ORDER BY date
    """

    daily_data = db.execute(query, (camera_id, start_date, end_date))

    return {
        'period': f'{start_date} to {end_date}',
        'total_in': sum(d['total_in'] for d in daily_data),
        'total_out': sum(d['total_out'] for d in daily_data),
        'busiest_day': max(daily_data, key=lambda x: x['total_in']),
        'daily_breakdown': daily_data
    }
```

**3. Peak Hours Analysis**
```python
def analyze_peak_hours(camera_id, days=30):
    """
    Find busiest hours over period
    """
    query = """
        SELECT
            hour,
            AVG(count_in) as avg_traffic,
            MAX(count_in) as max_traffic,
            COUNT(*) as occurrences
        FROM hourly_summary
        WHERE camera_id = %s
          AND date >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY hour
        ORDER BY avg_traffic DESC
        LIMIT 10
    """

    return db.execute(query, (camera_id, days))
```

### Export Formats

**Excel Export:**
```python
import pandas as pd
from openpyxl.chart import LineChart

def export_to_excel(data, filename):
    """
    Export report to Excel with charts
    """
    df = pd.DataFrame(data)

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Raw data
        df.to_excel(writer, sheet_name='Data', index=False)

        # Summary
        summary = {
            'Total In': df['count_in'].sum(),
            'Total Out': df['count_out'].sum(),
            'Peak Hour': df.loc[df['count_in'].idxmax(), 'hour'],
            'Average': df['count_in'].mean()
        }
        pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary')

        # Add chart
        workbook = writer.book
        worksheet = writer.sheets['Data']

        chart = LineChart()
        chart.title = "Traffic Trend"
        chart.add_data(worksheet['B2:C100'], titles_from_data=True)
        worksheet.add_chart(chart, "F2")
```

---

## 6. Counting Line Configuration UI

### Decision: Adjustable via Web UI

**Configuration Interface:**

```python
# API Endpoints for Configuration
@app.get("/api/config/camera/{camera_id}")
async def get_camera_config(camera_id: str):
    """Get camera configuration"""
    return config_manager.load_camera_config(camera_id)

@app.post("/api/config/camera/{camera_id}/line")
async def add_counting_line(camera_id: str, line_data: dict):
    """Add new counting line"""
    config = config_manager.load_camera_config(camera_id)
    config['counting_lines'].append(line_data)
    config_manager.save_camera_config(camera_id, config)
    return {"status": "success"}

@app.put("/api/config/camera/{camera_id}/line/{line_id}")
async def update_counting_line(camera_id: str, line_id: str, line_data: dict):
    """Update existing line"""
    # Update logic
    pass

@app.post("/api/config/camera/{camera_id}/zone")
async def add_zone(camera_id: str, zone_data: dict):
    """Add restricted zone"""
    config = config_manager.load_camera_config(camera_id)
    config['zones'].append(zone_data)
    config_manager.save_camera_config(camera_id, config)
    return {"status": "success"}
```

**Configuration Storage Format:**

```json
{
  "camera_id": "CAM001",
  "camera_name": "Main Entrance",
  "counting_lines": [
    {
      "line_id": "L001",
      "name": "Main Door",
      "type": "line",
      "coordinates": {"x1": 0, "y1": 400, "x2": 1920, "y2": 400},
      "direction": "bidirectional",
      "enabled": true,
      "color": "blue"
    }
  ],
  "zones": [
    {
      "zone_id": "Z001",
      "name": "Server Room",
      "type": "restricted",
      "polygon": [[100, 50], [300, 50], [300, 200], [100, 200]],
      "max_people": 0,
      "enabled": true,
      "color": "red"
    }
  ]
}
```

### Interactive Drawing Tool

**HTML/JavaScript UI:**

```html
<div id="config-panel">
    <h3>Camera Configuration</h3>

    <!-- Camera preview -->
    <canvas id="camera-canvas" width="1920" height="1080"></canvas>

    <!-- Tools -->
    <div class="tools">
        <button onclick="addLine()">➕ Add Line</button>
        <button onclick="addZone()">➕ Add Zone</button>
        <button onclick="saveConfig()">💾 Save</button>
    </div>

    <!-- Line list -->
    <div id="line-list"></div>
</div>

<script>
    const canvas = document.getElementById('camera-canvas');
    const ctx = canvas.getContext('2d');

    let isDrawing = false;
    let currentTool = null;
    let points = [];

    function addLine() {
        currentTool = 'line';
        alert('Click two points to draw a line');
    }

    function addZone() {
        currentTool = 'zone';
        alert('Click points to draw a polygon. Double-click to finish.');
    }

    canvas.onclick = function(e) {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        points.push({x, y});

        if (currentTool === 'line' && points.length === 2) {
            // Draw line
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            ctx.lineTo(points[1].x, points[1].y);
            ctx.strokeStyle = 'blue';
            ctx.lineWidth = 3;
            ctx.stroke();

            // Save
            saveLine(points);
            points = [];
        }
    };

    function saveLine(points) {
        const lineData = {
            coordinates: {
                x1: points[0].x,
                y1: points[0].y,
                x2: points[1].x,
                y2: points[1].y
            },
            direction: 'bidirectional',
            enabled: true
        };

        fetch('/api/config/camera/CAM001/line', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(lineData)
        });
    }
</script>
```

---

## 7. Complete System Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Cloud Server (4 vCPU, 8GB RAM)            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐   │
│  │  RTSP Stream Manager (4 cameras)                   │   │
│  │  - Auto-reconnect                                  │   │
│  │  - Buffer management                               │   │
│  └──────────────────┬─────────────────────────────────┘   │
│                     │                                       │
│  ┌──────────────────▼─────────────────────────────────┐   │
│  │  Person Detection & Tracking (YOLO11n)             │   │
│  │  - Detect all people                               │   │
│  │  - Track with BoT-SORT                             │   │
│  │  - Maintain Track IDs                              │   │
│  └──────────────────┬─────────────────────────────────┘   │
│                     │                                       │
│           ┌─────────┴─────────┐                            │
│           │                   │                            │
│  ┌────────▼────────┐  ┌──────▼──────────┐                │
│  │ Line Counting   │  │ Zone Monitoring │                │
│  │ - In/Out detect │  │ - Violations    │                │
│  │ - Track counts  │  │ - Alerts        │                │
│  └────────┬────────┘  └──────┬──────────┘                │
│           │                   │                            │
│  ┌────────▼───────────────────▼────────┐                 │
│  │  Database (PostgreSQL)              │                 │
│  │  - Counting events                  │                 │
│  │  - Zone violations                  │                 │
│  │  - Historical data                  │                 │
│  └────────┬────────────────────────────┘                 │
│           │                                                │
│  ┌────────▼────────────────────────────┐                 │
│  │  API Server (FastAPI)                │                 │
│  │  - REST API                          │                 │
│  │  - WebSocket (real-time)             │                 │
│  │  - Configuration endpoints           │                 │
│  └────────┬────────────────────────────┘                 │
│           │                                                │
└───────────┼────────────────────────────────────────────────┘
            │
            │ HTTP/WebSocket
            │
   ┌────────▼─────────┐
   │  Web Dashboard   │
   │  - Live view     │
   │  - Statistics    │
   │  - Alerts        │
   │  - Reports       │
   │  - Config UI     │
   └──────────────────┘
```

### Performance Estimates

**For 4 Cameras (4 vCPU, 8GB RAM):**

| Metric | Target | Expected |
|--------|--------|----------|
| FPS per camera | 25-30 | ✅ Achievable |
| Person detection latency | <40ms | ✅ 30-35ms |
| Counting accuracy | >98% | ✅ 98-99% |
| Database write rate | 100 events/sec | ✅ No issue |
| WebSocket update rate | 1 update/sec | ✅ Smooth |
| Dashboard latency | <2 seconds | ✅ 1-1.5s |
| Concurrent users | 10-20 | ✅ Supported |

---

## 8. Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Counting per camera** | IN / OUT / CURRENT | Complete traffic analysis |
| **Counting method** | Line crossing | Simple, accurate, widely used |
| **Dashboard** | Real-time with 1-2s delay | Balance performance vs freshness |
| **Graphs** | Live updates (Chart.js) | Visual trend analysis |
| **Alerts** | Multi-channel (Line/Email/SMS) | Critical for security |
| **Zone types** | Restricted/Limited/Monitored | Flexible security levels |
| **Database** | PostgreSQL | Robust, scalable (vector support ready) |
| **Historical data** | All of: Daily/Weekly/Monthly | Complete analytics |
| **Configuration** | Web UI (adjustable) | User-friendly, no code needed |
| **Export formats** | Excel/PDF/CSV | Standard business formats |

---

## 9. Implementation Priorities

### Phase 1: Core Counting (Week 1-2)
- [ ] Person detection with YOLO11n
- [ ] Track ID assignment (BoT-SORT)
- [ ] Line crossing detection
- [ ] Basic counting logic
- [ ] PostgreSQL database setup

### Phase 2: Dashboard (Week 2-3)
- [ ] FastAPI backend
- [ ] WebSocket implementation
- [ ] HTML/JavaScript frontend
- [ ] Real-time updates
- [ ] Camera grid view

### Phase 3: Zones & Alerts (Week 3-4)
- [ ] Zone polygon definition
- [ ] Violation detection
- [ ] Line Notify integration
- [ ] Email alerts
- [ ] Alert dashboard

### Phase 4: Reports & Config (Week 4-5)
- [ ] Historical data aggregation
- [ ] Report generation
- [ ] Excel/PDF export
- [ ] Configuration UI
- [ ] Interactive drawing tools

### Phase 5: Testing & Deployment (Week 5-6)
- [ ] Integration testing
- [ ] Performance optimization
- [ ] Documentation
- [ ] Production deployment
- [ ] User training

---

## 10. Next Meeting Topics

### Meeting 3: Database Architecture & Performance Optimization

**Proposed Topics:**

#### 1. PostgreSQL + pgvector Setup
- Installing and configuring pgvector extension
- Face embeddings storage schema
- Vector similarity search optimization
- Index types (IVFFlat vs HNSW)
- Query performance tuning

#### 2. Database Design Deep Dive
- Complete schema design
- Partitioning strategies for large data
- Archiving old data
- Backup and recovery procedures
- Replication considerations

#### 3. Face Recognition Database Integration
- Storing 512-dimensional vectors
- Efficient similarity search queries
- Caching strategies
- Hybrid approach (file + database)
- Migration from file-based to database

#### 4. Performance Analysis
- Query optimization for counting events
- Index strategies
- Connection pooling
- Read replicas for reporting
- Monitoring and profiling

#### 5. Supabase vs Self-hosted Comparison
- Cost analysis (Supabase vs PostgreSQL)
- Feature comparison
- Ease of setup
- Real-time capabilities
- API auto-generation
- Decision framework

#### 6. Data Retention Policies
- How long to keep counting events?
- Aggregation vs raw data
- GDPR/PDPA compliance
- Storage cost optimization
- Data lifecycle management

#### 7. Scalability Planning
- Handling 10x data growth
- Multi-tenant considerations
- Cross-region deployment
- High availability setup
- Disaster recovery

**Preparation Tasks:**
- [ ] Research pgvector performance benchmarks
- [ ] Calculate storage requirements (1 year projection)
- [ ] Compare Supabase pricing tiers
- [ ] Draft migration plan from files to database
- [ ] Prepare database schema proposals

**Expected Outcome:**
- Final database architecture design
- Clear decision on Supabase vs self-hosted
- Performance optimization strategies
- Implementation roadmap for database layer

---

## Meeting Summary

**Duration:** 60 minutes
**Outcome:** ✅ Complete person counting system design

**Key Achievements:**
1. ✅ Clarified person detection vs face recognition
2. ✅ Defined counting requirements (IN/OUT/CURRENT for all cameras)
3. ✅ Designed real-time dashboard with acceptable delay
4. ✅ Created restricted zone monitoring system
5. ✅ Planned comprehensive historical reporting
6. ✅ Designed web-based configuration UI
7. ✅ Specified multi-channel alert system
8. ✅ Outlined complete system architecture

**Critical Decisions:**
- Use line crossing for counting (simple, accurate)
- Real-time dashboard with 1-2 second delay
- PostgreSQL for all data storage
- Multi-channel alerts (Line/Email/SMS) for violations
- Web UI for configuration (no coding required)
- Export to Excel/PDF/CSV for reports

**Next Steps:**
1. Begin Phase 1 implementation (Core counting)
2. Set up PostgreSQL database
3. Implement YOLO11n person detection
4. Schedule Meeting 3 for database architecture

**Next Meeting:** Database Architecture & Performance (Week 2)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-04 11:11:33
**Prepared By:** Technical Team
**Status:** ✅ Ready for Implementation
**Related Documents:**
- Meeting 1: Face Recognition Technical Discussion (2025-11-04)
- Comprehensive Research: YOLO Face Recognition (2025-11-04)
