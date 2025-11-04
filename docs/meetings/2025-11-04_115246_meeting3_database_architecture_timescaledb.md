# Meeting Note 3: Database Architecture & TimescaleDB Design
**Date:** November 4, 2025
**Topic:** Database Architecture for Building Management System with IoT Integration
**Duration:** Extended Technical Discussion
**Attendees:** Development Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Context & Requirements](#2-project-context--requirements)
3. [Database Technology Selection](#3-database-technology-selection)
4. [Core Schema Design (6 Systems)](#4-core-schema-design-6-systems)
5. [Continuous Aggregates](#5-continuous-aggregates)
6. [KPI Framework for Corporate Buildings](#6-kpi-framework-for-corporate-buildings)
7. [Cost & Carbon Calculations](#7-cost--carbon-calculations)
8. [Face Recognition with pgvector](#8-face-recognition-with-pgvector)
9. [Data Lifecycle Management](#9-data-lifecycle-management)
10. [Performance Optimization](#10-performance-optimization)
11. [Security & Compliance](#11-security--compliance)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Next Steps](#13-next-steps)

---

## 1. Executive Summary

This meeting focused on designing a comprehensive database architecture for a Building Management System (BMS) that integrates CCTV, face recognition, and 6 critical building systems (power, lighting, lifts/escalators, access control, fire safety, and CCTV).

### Key Decisions Made

**Technology Stack:**
- **Primary Database:** TimescaleDB (PostgreSQL extension)
- **Vector Search:** pgvector extension (for face recognition)
- **Time-Series Optimization:** Automatic partitioning, compression, continuous aggregates

**Why TimescaleDB:**
- Single database solution (no need for separate time-series DB)
- Native PostgreSQL compatibility (use pgvector for face recognition)
- Automatic data management (compression, retention policies)
- Cost-effective (90%+ storage reduction via compression)
- BI-ready (standard SQL, pre-computed aggregates)

**Critical Architecture Components:**

1. **Time-Series Data Storage** (Hypertables)
   - 6 system-specific hypertables with appropriate sampling rates
   - Automatic time-based partitioning (chunks)

2. **Continuous Aggregates** (9+ materialized views)
   - Pre-computed hourly/daily/monthly summaries
   - Auto-refresh policies for real-time dashboards

3. **KPI Configuration** (5 reference tables)
   - Configurable energy targets and cost rates
   - Carbon emission factors
   - Building metadata and equipment registry

4. **Face Recognition** (pgvector integration)
   - 512-dimensional embeddings (ArcFace compatible)
   - HNSW index for sub-second similarity search

5. **Data Lifecycle Management**
   - Compression after 7 days (90-95% storage savings)
   - Retention policies (30-90 days raw, 2-5 years aggregated)
   - Automated backup and archiving

**Business Impact:**

- **Cost Reduction:** Energy savings tracking with 10-20% annual reduction targets
- **Carbon Tax Preparation:** Automated CO2 emissions calculation for future carbon tax compliance
- **ESG Reporting:** Ready for LEED/TREES certification and CDP reporting
- **Operational Efficiency:** Real-time monitoring with configurable KPIs and alerts

---

## 2. Project Context & Requirements

### 2.1 Customer Background

The client is a **corporate entity with self-owned building(s)** requiring integrated building management and business intelligence dashboard. The primary objectives are:

1. **Cost Reduction** - Reduce electricity bills through monitoring and optimization
2. **Carbon Tax Preparation** - Track and reduce carbon emissions for upcoming carbon tax regulations
3. **ESG Compliance** - Meet sustainability reporting requirements
4. **Operational Efficiency** - Monitor and optimize building systems usage

### 2.2 Six Integrated Systems

Based on the market research document (`docs/research/2025-11-03_110000_summary_market_research.md`), the system must integrate:

| System | Data Type | Sampling Rate | Primary Metrics |
|--------|-----------|---------------|-----------------|
| **1. CCTV Camera** | Event-based | On detection | Person counting (IN/OUT), Face recognition, Zone violations |
| **2. Access Control** | Event-based | On card swipe | Door access logs, Successful/denied attempts, Employee tracking |
| **3. Lighting System** | Time-series | 5-15 minutes | Energy usage, On/off status, Brightness levels, Occupancy detection |
| **4. Lifts & Escalators** | Hybrid | Events + 5min status | Trip counts, Energy per trip, Floor destinations, Downtime |
| **5. Fire Safety System** | Time-series | 1 minute | Smoke detector status, Sprinkler pressure, Alarm events |
| **6. Main Power System** | Time-series | 1-5 minutes | Voltage, Current, Power (kW), Energy (kWh), Power factor, Peak demand |

### 2.3 Data Integration Approach

**Customer Commitment:**
- Customer will provide standardized APIs for each system
- No need for direct protocol integration (Modbus, BACnet, etc.)
- Focus on data ingestion, storage, and analytics

**Sampling Rate Standards:**

```python
SAMPLING_RATES = {
    'main_power': '1-5 minutes',      # Real-time energy monitoring
    'lighting': '5-15 minutes',        # Pattern detection sufficient
    'lifts_escalators': 'event-based', # Plus 5-minute status checks
    'access_control': 'event-based',   # Security audit trail
    'fire_system': '1 minute',         # Safety-critical
    'cctv_counting': 'event-based',    # Person detection events
    'face_recognition': 'event-based'  # Recognition events
}
```

### 2.4 Business Intelligence Requirements

**Primary Use Case:** Energy cost reduction and carbon footprint tracking

**Dashboard Requirements:**
1. **Executive Overview** - Total cost, savings %, carbon emissions, YoY comparison
2. **Energy Analysis** - Real-time consumption, peak demand, system breakdown
3. **ESG & Compliance** - Carbon footprint, energy intensity, certification progress
4. **Building Operations** - Occupancy vs energy, equipment performance, alerts

**KPI Categories:**
- Cost reduction targets (% savings, budget compliance)
- Carbon emissions (tCO2e, intensity metrics)
- Energy efficiency (EUI - Energy Use Intensity)
- Building performance (occupancy efficiency, after-hours waste)
- Compliance & certification (LEED/TREES scores)

---

## 3. Database Technology Selection

### 3.1 TimescaleDB vs Alternatives

| Feature | TimescaleDB | InfluxDB | MongoDB | Supabase |
|---------|-------------|----------|---------|----------|
| **Time-series optimization** | ✅ Native | ✅ Native | ❌ Manual | ⚠️ Via extensions |
| **SQL compatibility** | ✅ PostgreSQL | ❌ InfluxQL | ❌ NoSQL | ✅ PostgreSQL |
| **Vector search (faces)** | ✅ pgvector | ❌ No | ✅ With Atlas | ✅ pgvector |
| **Automatic compression** | ✅ 90%+ | ✅ Limited | ❌ No | ⚠️ Manual |
| **Continuous aggregates** | ✅ Auto-refresh | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual |
| **Data retention policies** | ✅ Automatic | ✅ Yes | ❌ Manual | ⚠️ Via policies |
| **BI tool compatibility** | ✅ Excellent | ⚠️ Limited | ⚠️ Moderate | ✅ Good |
| **Cost (self-hosted)** | ✅ Free (open) | ✅ Free (open) | ✅ Free (open) | ⚠️ Paid tiers |
| **Operational complexity** | ✅ Low | ⚠️ Moderate | ⚠️ High | ✅ Managed |

**Decision: TimescaleDB**

**Rationale:**
1. **Single Database Solution** - No need for separate time-series + relational + vector databases
2. **PostgreSQL Compatibility** - Standard SQL, mature ecosystem, extensive tooling
3. **pgvector Integration** - Native vector search for face recognition (512-dim embeddings)
4. **Automatic Optimization** - Compression (90%+ savings), retention, continuous aggregates
5. **Cost Effective** - Open source, no licensing costs, massive storage savings
6. **BI-Ready** - Standard SQL interface works with all BI tools (Grafana, Tableau, Power BI)

### 3.2 TimescaleDB Key Features

**3.2.1 Hypertables (Automatic Partitioning)**

```sql
-- Convert regular table to hypertable
CREATE TABLE power_readings (
    time TIMESTAMPTZ NOT NULL,
    meter_id VARCHAR(20),
    power_kw DECIMAL(10,3)
    -- ... other columns
);

-- Single command enables automatic time-based partitioning
SELECT create_hypertable('power_readings', 'time');
```

**What happens:**
- Data automatically partitioned into "chunks" (e.g., 1-day or 1-week chunks)
- Queries automatically optimized (only scan relevant chunks)
- Old chunks can be compressed or dropped independently

**3.2.2 Continuous Aggregates (Pre-computed Views)**

```sql
-- Materialized view that auto-updates
CREATE MATERIALIZED VIEW power_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    meter_id,
    AVG(power_kw) AS avg_power,
    MAX(power_kw) AS peak_power,
    SUM(energy_kwh) AS total_energy
FROM power_readings
GROUP BY hour, meter_id;

-- Auto-refresh every 10 minutes
SELECT add_continuous_aggregate_policy('power_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');
```

**Benefits:**
- Dashboard queries run on pre-computed data (milliseconds vs seconds)
- Automatic incremental updates (only new data processed)
- Can build aggregates on top of aggregates (hourly → daily → monthly)

**3.2.3 Compression (90%+ Storage Savings)**

```sql
-- Enable compression
ALTER TABLE power_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'meter_id',
    timescaledb.compress_orderby = 'time DESC'
);

-- Automatically compress data older than 7 days
SELECT add_compression_policy('power_readings', INTERVAL '7 days');
```

**Results:**
- Raw data: ~1000 bytes per row
- Compressed: ~50-100 bytes per row
- **Storage reduction: 90-95%**
- Queries still work normally (transparent decompression)

**3.2.4 Data Retention (Automatic Cleanup)**

```sql
-- Automatically drop raw data older than 90 days
SELECT add_retention_policy('power_readings', INTERVAL '90 days');
```

**Note:** Aggregated data (hourly/daily/monthly) remains available even after raw data is deleted.

---

## 4. Core Schema Design (6 Systems)

### 4.1 Main Power System

**Purpose:** Monitor building-wide electricity consumption, peak demand, power quality

**Sampling Rate:** 1-5 minutes (real-time energy monitoring standard)

**Schema:**

```sql
CREATE TABLE power_readings (
    time TIMESTAMPTZ NOT NULL,
    meter_id VARCHAR(20) NOT NULL,      -- 'MAIN_METER_01', 'SUB_METER_FLOOR_3'

    -- Three-phase voltage (V)
    voltage_r DECIMAL(8,2),              -- Phase R
    voltage_s DECIMAL(8,2),              -- Phase S
    voltage_t DECIMAL(8,2),              -- Phase T

    -- Three-phase current (A)
    current_r DECIMAL(8,2),              -- Current R
    current_s DECIMAL(8,2),              -- Current S
    current_t DECIMAL(8,2),              -- Current T

    -- Power metrics
    power_kw DECIMAL(10,3) NOT NULL,     -- Active Power (kW)
    reactive_power_kvar DECIMAL(10,3),   -- Reactive Power (kVAR)
    apparent_power_kva DECIMAL(10,3),    -- Apparent Power (kVA)
    power_factor DECIMAL(4,3),           -- 0.000-1.000 (ideal: 0.95+)

    -- Energy metrics
    energy_kwh DECIMAL(12,3),            -- Cumulative energy (kWh)
    demand_kw DECIMAL(10,3),             -- Instantaneous demand (kW)

    -- Metadata
    quality_flags JSONB,                 -- Voltage sags, harmonics, etc.

    PRIMARY KEY (time, meter_id)
);

-- Convert to hypertable (enables time-series optimization)
SELECT create_hypertable('power_readings', 'time');

-- Indexes for fast queries
CREATE INDEX idx_power_meter_time ON power_readings(meter_id, time DESC);
CREATE INDEX idx_power_high_demand ON power_readings(time, demand_kw)
    WHERE demand_kw > 80; -- Partial index for peak demand queries
```

**Data Volume Estimate:**
- Sampling: Every 5 minutes = 288 readings/day/meter
- 10 meters × 288 readings × 365 days = **1,051,200 rows/year**
- Uncompressed: ~1 GB/year
- **Compressed: ~100 MB/year (90% reduction)**

**Key Metrics Tracked:**
- **Real Power (kW):** Actual energy consumption
- **Power Factor:** Efficiency metric (low PF = higher bills)
- **Peak Demand (kW):** Used for demand charges (MEA/PEA billing)
- **Energy (kWh):** Cumulative consumption for billing

**Why This Design:**
- Three-phase monitoring (commercial buildings use 3-phase)
- Power factor tracking (utilities charge penalties for low PF)
- Demand tracking (demand charges are 30-40% of electricity bills)
- Quality flags for power quality monitoring (JSONB for flexibility)

### 4.2 Lighting System

**Purpose:** Track lighting energy usage, occupancy correlation, after-hours waste

**Sampling Rate:** 5-15 minutes (pattern detection, not real-time control)

**Schema:**

```sql
CREATE TABLE lighting_readings (
    time TIMESTAMPTZ NOT NULL,
    zone_id VARCHAR(20) NOT NULL,        -- 'FLOOR_1_ZONE_A', 'PARKING_LEVEL_B2'

    -- Status
    status VARCHAR(10),                  -- 'ON', 'OFF', 'DIM'
    brightness_percent INTEGER,          -- 0-100 (for dimmable lights)

    -- Energy
    energy_kwh DECIMAL(10,3),            -- Cumulative energy for this zone
    power_w DECIMAL(8,2),                -- Current power draw (Watts)

    -- Occupancy correlation
    occupancy_detected BOOLEAN,          -- From PIR motion sensors
    lux_level INTEGER,                   -- Ambient light level (for daylight harvesting)

    -- Control mode
    control_mode VARCHAR(20),            -- 'AUTO', 'MANUAL', 'SCHEDULE', 'OVERRIDE'
    schedule_enabled BOOLEAN,            -- Whether scheduled control is active

    PRIMARY KEY (time, zone_id)
);

SELECT create_hypertable('lighting_readings', 'time');
CREATE INDEX idx_lighting_zone_time ON lighting_readings(zone_id, time DESC);
CREATE INDEX idx_lighting_afterhours ON lighting_readings(time, status)
    WHERE EXTRACT(HOUR FROM time) NOT BETWEEN 7 AND 19; -- After-hours usage
```

**Key Metrics:**
- **Energy per zone:** Identify high-consumption areas
- **Occupancy correlation:** Lights on without occupancy = waste
- **After-hours usage:** Energy waste detection
- **Lux levels:** Daylight harvesting opportunities

**Use Cases:**
1. **After-Hours Waste Detection:** Lights on outside 7 AM - 7 PM without occupancy
2. **Occupancy Efficiency:** Compare energy/person across zones
3. **Daylight Harvesting:** Reduce brightness when natural light sufficient
4. **Schedule Optimization:** Identify zones needing schedule adjustments

### 4.3 Lifts & Escalators (Vertical Transportation)

**Purpose:** Track usage patterns, energy per trip, maintenance needs

**Sampling Rate:** Event-based (per trip) + periodic status (every 5 minutes)

**Schema:**

```sql
CREATE TABLE lift_events (
    time TIMESTAMPTZ NOT NULL,
    equipment_id VARCHAR(20) NOT NULL,   -- 'LIFT_01', 'ESCALATOR_NORTH'
    equipment_type VARCHAR(20),          -- 'LIFT', 'ESCALATOR', 'MOVING_WALKWAY'

    -- Event type
    event_type VARCHAR(30),              -- 'TRIP', 'STATUS_CHECK', 'MAINTENANCE', 'FAULT'

    -- Trip details (for lifts)
    floor_from INTEGER,
    floor_to INTEGER,
    trip_duration_seconds INTEGER,
    passenger_count INTEGER,             -- Estimated from load sensor (optional)

    -- Energy metrics
    energy_kwh DECIMAL(8,3),             -- Energy consumed for this trip
    regenerative_kwh DECIMAL(8,3),       -- Energy recovered (if regenerative drive)

    -- Status
    status VARCHAR(20),                  -- 'RUNNING', 'IDLE', 'OUT_OF_SERVICE', 'ERROR'
    load_percent INTEGER,                -- 0-100 (current load)

    -- Fault information
    fault_code VARCHAR(50),
    fault_description TEXT,

    PRIMARY KEY (time, equipment_id)
);

SELECT create_hypertable('lift_events', 'time');
CREATE INDEX idx_lift_equipment_time ON lift_events(equipment_id, time DESC);
CREATE INDEX idx_lift_faults ON lift_events(time, status)
    WHERE status = 'ERROR';
```

**Key Metrics:**
- **Trips per day:** Usage patterns by hour/day
- **Energy per trip:** Efficiency benchmarking
- **Passengers per trip:** Utilization rate
- **Downtime:** Maintenance scheduling optimization

**Analytics Opportunities:**
1. **Peak Hour Analysis:** When to enable all lifts vs park some
2. **Energy Efficiency:** Compare energy/trip across equipment
3. **Predictive Maintenance:** Fault patterns before failures
4. **Regenerative Savings:** Track energy recovery (if equipped)

### 4.4 Access Control System

**Purpose:** Security audit trail, occupancy tracking, unauthorized access detection

**Sampling Rate:** Event-based (every card swipe/door access)

**Schema:**

```sql
CREATE TABLE access_events (
    time TIMESTAMPTZ NOT NULL,
    door_id VARCHAR(20) NOT NULL,        -- 'MAIN_ENTRANCE', 'SERVER_ROOM_DOOR'

    -- Identity
    card_id VARCHAR(50),                 -- RFID card UID
    employee_id VARCHAR(20),             -- Link to HR system
    access_method VARCHAR(20),           -- 'CARD', 'BIOMETRIC', 'PIN', 'FACE_RECOGNITION'

    -- Result
    result VARCHAR(20),                  -- 'SUCCESS', 'DENIED', 'UNAUTHORIZED', 'INVALID_CARD'
    denial_reason VARCHAR(100),          -- 'CARD_EXPIRED', 'WRONG_ZONE', 'BLACKLISTED'

    -- Direction
    direction VARCHAR(10),               -- 'IN', 'OUT' (for occupancy tracking)

    -- Context
    zone_id VARCHAR(20),                 -- Security zone
    area_type VARCHAR(30),               -- 'PUBLIC', 'RESTRICTED', 'HIGH_SECURITY'

    PRIMARY KEY (time, door_id, card_id)
);

SELECT create_hypertable('access_events', 'time');
CREATE INDEX idx_access_door_time ON access_events(door_id, time DESC);
CREATE INDEX idx_access_employee ON access_events(employee_id, time DESC);
CREATE INDEX idx_access_unauthorized ON access_events(time, result)
    WHERE result IN ('DENIED', 'UNAUTHORIZED');
```

**Key Metrics:**
- **Access attempts:** Successful vs denied
- **Unique employees:** Daily active occupants
- **Peak hours:** Entry/exit patterns
- **Unauthorized attempts:** Security incidents

**Integration with CCTV:**
```sql
-- Link access events with face recognition
SELECT
    a.time,
    a.employee_id,
    a.door_id,
    a.result,
    f.person_id,
    f.similarity_score
FROM access_events a
LEFT JOIN face_recognition_events f
    ON f.time BETWEEN a.time - INTERVAL '5 seconds'
                  AND a.time + INTERVAL '5 seconds'
    AND f.camera_id = 'CAMERA_' || a.door_id
WHERE a.result = 'SUCCESS';
```

### 4.5 Fire Safety System

**Purpose:** Safety compliance, sensor health monitoring, incident response

**Sampling Rate:** 1 minute (safety-critical systems require frequent checks)

**Schema:**

```sql
CREATE TABLE fire_system_readings (
    time TIMESTAMPTZ NOT NULL,
    sensor_id VARCHAR(20) NOT NULL,      -- 'SMOKE_DET_F3_R301', 'SPRINKLER_ZONE_A'
    sensor_type VARCHAR(30),             -- 'SMOKE', 'HEAT', 'FLAME', 'SPRINKLER', 'ALARM_PANEL'

    -- Status
    status VARCHAR(20),                  -- 'NORMAL', 'ALERT', 'ALARM', 'FAULT', 'MAINTENANCE'
    alarm_level INTEGER,                 -- 0-3 (0=normal, 1=warning, 2=alert, 3=alarm)

    -- Sensor readings
    temperature_c DECIMAL(5,2),          -- For heat detectors
    smoke_density DECIMAL(5,2),          -- Obscuration percentage
    water_pressure_bar DECIMAL(5,2),     -- For sprinkler systems

    -- Maintenance
    battery_level INTEGER,               -- 0-100 (for battery-backed sensors)
    last_test_date DATE,                 -- Last manual test
    maintenance_due DATE,

    -- Location
    floor INTEGER,
    zone VARCHAR(20),
    room VARCHAR(50),

    PRIMARY KEY (time, sensor_id)
);

SELECT create_hypertable('fire_system_readings', 'time');
CREATE INDEX idx_fire_sensor_time ON fire_system_readings(sensor_id, time DESC);
CREATE INDEX idx_fire_alarms ON fire_system_readings(time, status)
    WHERE status IN ('ALERT', 'ALARM');
CREATE INDEX idx_fire_faults ON fire_system_readings(time, status)
    WHERE status = 'FAULT';
```

**Critical Alerts:**
```sql
-- Real-time alarm monitoring
SELECT
    sensor_id,
    sensor_type,
    status,
    floor,
    zone,
    time
FROM fire_system_readings
WHERE time > NOW() - INTERVAL '5 minutes'
  AND status IN ('ALERT', 'ALARM')
ORDER BY alarm_level DESC, time DESC;
```

**Compliance Reporting:**
- Sensor test history
- Battery replacement schedule
- Fault response times
- Alarm event log (required by fire safety regulations)

### 4.6 CCTV - Person Counting

**Purpose:** Occupancy tracking, zone monitoring, people flow analysis

**Sampling Rate:** Event-based (when person crosses counting line)

**Schema:**

```sql
CREATE TABLE counting_events (
    time TIMESTAMPTZ NOT NULL,
    camera_id VARCHAR(10) NOT NULL,      -- 'CAM_01', 'CAM_02'

    -- Detection
    track_id INTEGER NOT NULL,           -- Unique ID for this person (from tracker)
    event_type VARCHAR(10) NOT NULL,     -- 'IN', 'OUT'

    -- Location
    zone_id VARCHAR(20),                 -- Optional zone crossing
    line_id VARCHAR(20),                 -- Which counting line crossed

    -- Detection quality
    confidence DECIMAL(4,3),             -- 0.000-1.000 (YOLO confidence)
    bbox JSONB,                          -- {x, y, w, h} bounding box

    PRIMARY KEY (time, camera_id, track_id)
);

SELECT create_hypertable('counting_events', 'time');
CREATE INDEX idx_counting_camera_time ON counting_events(camera_id, time DESC);
CREATE INDEX idx_counting_zone ON counting_events(zone_id, time DESC);

-- Zone violations
CREATE TABLE zone_violations (
    time TIMESTAMPTZ NOT NULL,
    zone_id VARCHAR(20) NOT NULL,

    -- Violation details
    violation_type VARCHAR(50),          -- 'RESTRICTED_ACCESS', 'OVERCAPACITY', 'LOITERING'
    severity VARCHAR(20),                -- 'INFO', 'WARNING', 'CRITICAL'

    -- People involved
    person_count INTEGER,
    track_ids INTEGER[],                 -- Array of track IDs

    -- Duration
    duration_seconds INTEGER,            -- How long violation lasted

    -- Response
    alert_sent BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(50),
    acknowledged_at TIMESTAMPTZ,

    PRIMARY KEY (time, zone_id)
);

SELECT create_hypertable('zone_violations', 'time');
CREATE INDEX idx_violations_zone_time ON zone_violations(zone_id, time DESC);
CREATE INDEX idx_violations_unack ON zone_violations(time, alert_sent, acknowledged_at)
    WHERE acknowledged_at IS NULL;
```

**Real-time Occupancy Query:**

```sql
-- Current occupancy per camera (last 1 hour)
SELECT
    camera_id,
    SUM(CASE WHEN event_type = 'IN' THEN 1 ELSE 0 END) AS count_in,
    SUM(CASE WHEN event_type = 'OUT' THEN 1 ELSE 0 END) AS count_out,
    SUM(CASE WHEN event_type = 'IN' THEN 1 ELSE -1 END) AS current_occupancy
FROM counting_events
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY camera_id;
```

---

## 5. Continuous Aggregates

**Purpose:** Pre-compute common queries for fast dashboard loading

### 5.1 Hourly Power Summary

```sql
CREATE MATERIALIZED VIEW power_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    meter_id,

    -- Voltage statistics
    AVG(voltage_r) AS avg_voltage_r,
    AVG(voltage_s) AS avg_voltage_s,
    AVG(voltage_t) AS avg_voltage_t,

    -- Power statistics
    AVG(power_kw) AS avg_power_kw,
    MAX(power_kw) AS peak_power_kw,
    MIN(power_kw) AS min_power_kw,
    STDDEV(power_kw) AS stddev_power_kw,

    -- Power factor
    AVG(power_factor) AS avg_power_factor,
    MIN(power_factor) AS min_power_factor,

    -- Energy consumed (delta between first and last reading)
    MAX(energy_kwh) - MIN(energy_kwh) AS energy_consumed_kwh,

    -- Peak demand
    MAX(demand_kw) AS peak_demand_kw,

    -- Data quality
    COUNT(*) AS reading_count,
    COUNT(*) FILTER (WHERE power_factor < 0.85) AS low_pf_count

FROM power_readings
GROUP BY hour, meter_id;

-- Auto-refresh every 10 minutes
SELECT add_continuous_aggregate_policy('power_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');

-- Indexes
CREATE INDEX idx_power_hourly_meter_hour ON power_hourly(meter_id, hour DESC);
```

**Query Performance:**
- **Without aggregate:** Scan 288 raw rows (5-min sampling) → 500-1000ms
- **With aggregate:** Scan 1 pre-computed row → 5-10ms
- **Speedup: 100x faster**

### 5.2 Daily Power Summary

```sql
CREATE MATERIALIZED VIEW power_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', hour) AS day,
    meter_id,

    -- Energy totals
    SUM(energy_consumed_kwh) AS total_energy_kwh,

    -- Power statistics
    AVG(avg_power_kw) AS avg_power_kw,
    MAX(peak_power_kw) AS peak_power_kw,

    -- Power quality
    AVG(avg_power_factor) AS avg_power_factor,

    -- Peak demand (critical for billing)
    MAX(peak_demand_kw) AS peak_demand_kw,

    -- Operating hours (hours with power > 1 kW)
    COUNT(*) FILTER (WHERE avg_power_kw > 1) AS operating_hours,

    -- Low power factor hours (penalty charges)
    COUNT(*) FILTER (WHERE avg_power_factor < 0.85) AS low_pf_hours

FROM power_hourly
GROUP BY day, meter_id;

SELECT add_continuous_aggregate_policy('power_daily',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

### 5.3 Hourly Lighting Summary

```sql
CREATE MATERIALIZED VIEW lighting_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    zone_id,

    -- Operating time (minutes lights were on)
    -- Assuming 5-minute sampling: 12 readings/hour
    SUM(CASE WHEN status = 'ON' THEN 5 ELSE 0 END) AS minutes_on,

    -- Average brightness when on
    AVG(brightness_percent) FILTER (WHERE status = 'ON') AS avg_brightness,

    -- Energy consumed
    MAX(energy_kwh) - MIN(energy_kwh) AS energy_consumed_kwh,

    -- Occupancy correlation
    SUM(CASE WHEN occupancy_detected THEN 1 ELSE 0 END) AS occupancy_detections,
    COUNT(*) AS total_readings,
    (SUM(CASE WHEN occupancy_detected THEN 1 ELSE 0 END)::DECIMAL /
     COUNT(*) * 100) AS occupancy_percent,

    -- Waste detection (lights on without occupancy)
    SUM(CASE WHEN status = 'ON' AND NOT occupancy_detected THEN 1 ELSE 0 END) AS waste_readings,

    -- Control mode breakdown
    SUM(CASE WHEN control_mode = 'AUTO' THEN 1 ELSE 0 END) AS auto_mode_count,
    SUM(CASE WHEN control_mode = 'MANUAL' THEN 1 ELSE 0 END) AS manual_mode_count

FROM lighting_readings
GROUP BY hour, zone_id;

SELECT add_continuous_aggregate_policy('lighting_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');
```

**Waste Detection Query:**

```sql
-- Zones with highest lighting waste (on without occupancy)
SELECT
    zone_id,
    SUM(waste_readings) AS total_waste_readings,
    SUM(energy_consumed_kwh) AS total_energy_kwh,
    -- Estimate wasted energy (proportional to waste readings)
    SUM(energy_consumed_kwh) * (SUM(waste_readings)::DECIMAL / SUM(total_readings))
        AS estimated_wasted_kwh
FROM lighting_hourly
WHERE hour >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY zone_id
ORDER BY estimated_wasted_kwh DESC
LIMIT 10;
```

### 5.4 Daily Lift Summary

```sql
CREATE MATERIALIZED VIEW lift_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    equipment_id,
    equipment_type,

    -- Trip statistics
    COUNT(*) FILTER (WHERE event_type = 'TRIP') AS total_trips,
    AVG(trip_duration_seconds) FILTER (WHERE event_type = 'TRIP') AS avg_trip_duration,

    -- Passenger statistics (if available)
    SUM(passenger_count) FILTER (WHERE event_type = 'TRIP') AS total_passengers,
    AVG(passenger_count) FILTER (WHERE event_type = 'TRIP') AS avg_passengers_per_trip,

    -- Energy metrics
    SUM(energy_kwh) FILTER (WHERE event_type = 'TRIP') AS total_energy_kwh,
    AVG(energy_kwh) FILTER (WHERE event_type = 'TRIP') AS avg_energy_per_trip,
    SUM(regenerative_kwh) FILTER (WHERE event_type = 'TRIP') AS total_regenerative_kwh,

    -- Efficiency (passengers per kWh)
    SUM(passenger_count) / NULLIF(SUM(energy_kwh), 0) AS passengers_per_kwh,

    -- Downtime
    COUNT(*) FILTER (WHERE status = 'ERROR') AS error_count,
    SUM(trip_duration_seconds) FILTER (WHERE status = 'OUT_OF_SERVICE') / 3600.0 AS downtime_hours,

    -- Utilization (trips vs capacity)
    -- Assuming 16-hour operation (6 AM - 10 PM), 30-second average trip
    COUNT(*) FILTER (WHERE event_type = 'TRIP')::DECIMAL / (16 * 120) * 100 AS utilization_percent

FROM lift_events
GROUP BY day, equipment_id, equipment_type;

SELECT add_continuous_aggregate_policy('lift_daily',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

### 5.5 Daily Access Control Summary

```sql
CREATE MATERIALIZED VIEW access_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS day,
    door_id,

    -- Access statistics
    COUNT(*) AS total_access_attempts,
    COUNT(*) FILTER (WHERE result = 'SUCCESS') AS successful_access,
    COUNT(*) FILTER (WHERE result = 'DENIED') AS denied_access,
    COUNT(*) FILTER (WHERE result = 'UNAUTHORIZED') AS unauthorized_attempts,

    -- Security metrics
    (COUNT(*) FILTER (WHERE result = 'UNAUTHORIZED')::DECIMAL /
     NULLIF(COUNT(*), 0) * 100) AS unauthorized_percent,

    -- Unique users
    COUNT(DISTINCT employee_id) AS unique_employees,

    -- Peak hour (most common access hour)
    mode() WITHIN GROUP (ORDER BY EXTRACT(HOUR FROM time)) AS peak_hour,

    -- Access method breakdown
    COUNT(*) FILTER (WHERE access_method = 'CARD') AS card_access,
    COUNT(*) FILTER (WHERE access_method = 'BIOMETRIC') AS biometric_access,
    COUNT(*) FILTER (WHERE access_method = 'FACE_RECOGNITION') AS face_recog_access,

    -- After-hours access (outside 6 AM - 8 PM)
    COUNT(*) FILTER (WHERE EXTRACT(HOUR FROM time) NOT BETWEEN 6 AND 20) AS afterhours_access

FROM access_events
GROUP BY day, door_id;

SELECT add_continuous_aggregate_policy('access_daily',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

### 5.6 Hourly Person Counting Summary

```sql
CREATE MATERIALIZED VIEW counting_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS hour,
    camera_id,

    -- In/Out counts
    COUNT(*) FILTER (WHERE event_type = 'IN') AS count_in,
    COUNT(*) FILTER (WHERE event_type = 'OUT') AS count_out,

    -- Net occupancy change
    COUNT(*) FILTER (WHERE event_type = 'IN') -
    COUNT(*) FILTER (WHERE event_type = 'OUT') AS net_count,

    -- Detection quality
    AVG(confidence) AS avg_confidence,
    COUNT(*) FILTER (WHERE confidence < 0.7) AS low_confidence_count,

    -- Unique persons (distinct track IDs)
    COUNT(DISTINCT track_id) AS unique_persons

FROM counting_events
GROUP BY hour, camera_id;

SELECT add_continuous_aggregate_policy('counting_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');
```

### 5.7 Building-Wide Energy Summary

**Purpose:** Single view combining all energy sources for executive dashboard

```sql
CREATE MATERIALIZED VIEW building_energy_hourly
WITH (timescaledb.continuous) AS
SELECT
    h.hour,

    -- Main power totals
    SUM(p.energy_consumed_kwh) AS total_energy_kwh,
    MAX(p.peak_power_kw) AS peak_power_kw,
    AVG(p.avg_power_factor) AS avg_power_factor,

    -- Breakdown by system (requires submeters or estimation)
    SUM(l.energy_consumed_kwh) AS lighting_energy_kwh,
    SUM(lf.total_energy_kwh) AS lift_energy_kwh,

    -- Estimated HVAC (if no submeter: Total - Lighting - Lifts)
    SUM(p.energy_consumed_kwh) -
        COALESCE(SUM(l.energy_consumed_kwh), 0) -
        COALESCE(SUM(lf.total_energy_kwh), 0) AS estimated_hvac_kwh,

    -- Occupancy correlation
    AVG(c.net_count) AS avg_occupancy_change,

    -- Energy per person (if we have total occupancy)
    SUM(p.energy_consumed_kwh) / NULLIF(AVG(c.net_count), 0) AS kwh_per_person

FROM (
    -- Generate hour series
    SELECT DISTINCT time_bucket('1 hour', time) AS hour
    FROM power_readings
) h
LEFT JOIN power_hourly p ON p.hour = h.hour
LEFT JOIN lighting_hourly l ON l.hour = h.hour
LEFT JOIN LATERAL (
    SELECT
        DATE_TRUNC('hour', day) AS hour,
        SUM(total_energy_kwh) AS total_energy_kwh
    FROM lift_daily
    WHERE DATE_TRUNC('hour', day) = h.hour
    GROUP BY hour
) lf ON TRUE
LEFT JOIN counting_hourly c ON c.hour = h.hour
GROUP BY h.hour;

SELECT add_continuous_aggregate_policy('building_energy_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '10 minutes',
    schedule_interval => INTERVAL '10 minutes');
```

**Executive Dashboard Query (Last 24 Hours):**

```sql
SELECT
    hour,
    total_energy_kwh,
    lighting_energy_kwh,
    lift_energy_kwh,
    estimated_hvac_kwh,
    -- Percentages
    (lighting_energy_kwh / NULLIF(total_energy_kwh, 0) * 100) AS lighting_percent,
    (lift_energy_kwh / NULLIF(total_energy_kwh, 0) * 100) AS lift_percent,
    (estimated_hvac_kwh / NULLIF(total_energy_kwh, 0) * 100) AS hvac_percent,
    -- Cost estimate (assuming 4 THB/kWh)
    total_energy_kwh * 4 AS estimated_cost_thb
FROM building_energy_hourly
WHERE hour >= NOW() - INTERVAL '24 hours'
ORDER BY hour DESC;
```

---

## 6. KPI Framework for Corporate Buildings

### 6.1 Business Objectives

**Primary Goal:** Cost reduction through energy optimization and carbon tax preparation

**Key Stakeholders:**
- **CFO/Finance:** Cost reduction, budget compliance
- **CSR/Sustainability:** Carbon footprint, ESG reporting
- **Facility Manager:** Operational efficiency, equipment performance
- **Executive Team:** Overall building performance, ROI

### 6.2 KPI Categories

**Category 1: Cost Reduction KPIs**

```sql
CREATE TABLE energy_targets (
    id SERIAL PRIMARY KEY,
    target_name VARCHAR(100) NOT NULL,
    target_type VARCHAR(50) NOT NULL,    -- 'MONTHLY_KWH', 'DAILY_COST', 'PEAK_DEMAND'
    target_value DECIMAL(12,2) NOT NULL,
    unit VARCHAR(20),                    -- 'kWh', 'THB', 'kW'

    -- Time period
    period_type VARCHAR(20),             -- 'DAILY', 'MONTHLY', 'YEARLY'
    effective_from DATE NOT NULL,
    effective_to DATE,

    -- Baseline for comparison
    baseline_period DATERANGE,           -- e.g., '[2024-01-01,2024-12-31)'
    baseline_value DECIMAL(12,2),        -- Historical baseline
    reduction_percent DECIMAL(5,2),      -- e.g., 15.00 = reduce 15% from baseline

    -- Alert configuration
    alert_threshold DECIMAL(5,2),        -- Alert when 90% of target reached
    alert_recipients TEXT[],             -- Array of email addresses

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(50),
    notes TEXT
);

-- Example targets
INSERT INTO energy_targets (target_name, target_type, target_value, unit, period_type,
                           baseline_period, reduction_percent, effective_from, alert_threshold)
VALUES
('Monthly Energy Reduction 2025', 'MONTHLY_KWH', 50000, 'kWh', 'MONTHLY',
 '[2024-01-01,2024-12-31)', 15.00, '2025-01-01', 90.00),

('Peak Demand Limit', 'PEAK_DEMAND', 100, 'kW', 'DAILY',
 NULL, NULL, '2025-01-01', 95.00),

('Monthly Cost Budget', 'DAILY_COST', 250000, 'THB', 'MONTHLY',
 '[2024-01-01,2024-12-31)', 10.00, '2025-01-01', 90.00);
```

**Calculated KPIs:**

```
1. Energy Cost Savings (%)
   = (Baseline - Current) / Baseline × 100
   Target: 10-20% reduction YoY

2. Monthly Electricity Bill vs Budget
   = Actual Cost / Budgeted Cost × 100
   Target: ≤ 100% (stay within budget)

3. Peak Demand Reduction (%)
   = (Baseline Peak - Current Peak) / Baseline Peak × 100
   Target: 15-25% reduction
   Impact: Reduce MEA/PEA demand charges (30-40% of bill)
```

**Category 2: Carbon Tax & Environmental KPIs**

```sql
CREATE TABLE carbon_factors (
    id SERIAL PRIMARY KEY,
    region VARCHAR(50),                  -- 'THAILAND', 'BANGKOK'
    source VARCHAR(50),                  -- 'GRID_ELECTRICITY', 'SOLAR', 'DIESEL'
    emission_factor DECIMAL(10,6),       -- kgCO2e per kWh
    unit VARCHAR(20),                    -- 'kgCO2e/kWh'
    source_reference TEXT,               -- 'TGO 2024 - Thailand Grid Average'
    effective_from DATE NOT NULL,
    effective_to DATE,

    -- Carbon tax rate (if applicable)
    carbon_tax_rate DECIMAL(8,2),        -- THB per tCO2e
    tax_effective_from DATE
);

-- Thailand grid electricity (2024 data from TGO)
INSERT INTO carbon_factors (region, source, emission_factor, unit, source_reference, effective_from)
VALUES
('THAILAND', 'GRID_ELECTRICITY', 0.521300, 'kgCO2e/kWh',
 'TGO 2024 - Thailand Greenhouse Gas Management Organization', '2024-01-01');
```

**Calculated KPIs:**

```
1. Carbon Emissions (tCO2e/month)
   = Total kWh × Emission Factor (0.5213 kgCO2e/kWh) / 1000
   Target: 15-30% reduction YoY
   Importance: Thailand preparing carbon tax (expected 200-500 THB/tCO2e)

2. Carbon Intensity (kgCO2e/sqm/year)
   = Annual Carbon Emissions / Building Area
   Target: < 100 kgCO2e/sqm/year (LEED Gold standard)
   Benchmark: Office buildings typically 120-150 kgCO2e/sqm/year

3. Projected Carbon Tax Cost
   = Carbon Emissions (tCO2e) × Tax Rate (THB/tCO2e)
   Assumption: 300 THB/tCO2e (mid-range estimate)
   Purpose: Financial planning for future carbon tax
```

**Category 3: Energy Efficiency KPIs**

```sql
CREATE TABLE building_info (
    id SERIAL PRIMARY KEY,
    building_name VARCHAR(100),
    total_area_sqm DECIMAL(10,2),        -- Gross floor area
    conditioned_area_sqm DECIMAL(10,2),  -- Air-conditioned area
    floors INTEGER,
    max_occupancy INTEGER,               -- Design capacity
    typical_occupancy INTEGER,           -- Average daily occupancy
    building_type VARCHAR(50),           -- 'OFFICE', 'RETAIL', 'MIXED_USE'

    -- Certifications
    certification VARCHAR(50),           -- 'LEED_GOLD', 'TREES_PLATINUM', 'EDGE'
    certification_date DATE,
    certification_expiry DATE,

    -- Construction
    construction_year INTEGER,
    major_retrofit_year INTEGER,

    updated_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO building_info
VALUES (1, 'Corporate Headquarters', 5000.00, 4500.00, 10, 500, 350,
        'OFFICE', 'LEED_GOLD', '2020-06-01', '2025-06-01', 2018, NULL, NOW());
```

**Calculated KPIs:**

```
1. Energy Use Intensity (EUI)
   = Annual kWh / Building Area (sqm)
   Unit: kWh/sqm/year
   Target: < 150 kWh/sqm/year (efficient office)
   Benchmarks:
   - Excellent: < 120 kWh/sqm/year
   - Good: 120-150 kWh/sqm/year
   - Average: 150-200 kWh/sqm/year
   - Poor: > 200 kWh/sqm/year

2. HVAC Efficiency Ratio
   = HVAC Energy / Total Energy × 100
   Target: 40-50% (typical for tropical climate)
   Alert: If > 60% = HVAC inefficiency

3. Lighting Efficiency Ratio
   = Lighting Energy / Total Energy × 100
   Target: < 20% (modern LED lighting)
   Alert: If > 25% = upgrade opportunity
```

**Category 4: Building Performance KPIs**

```
1. Occupancy Efficiency
   = Actual Occupancy / Design Capacity × 100
   Target: 60-80% (optimal utilization)
   Use: Right-size HVAC and lighting schedules

2. Energy per Occupant
   = Daily kWh / Daily Average Occupancy
   Unit: kWh/person/day
   Target: < 15 kWh/person/day for offices
   Use: Compare efficiency across time periods

3. After-Hours Energy Waste
   = Energy (6 PM - 6 AM) / Total Daily Energy × 100
   Target: < 15% (assuming minimal night operations)
   Opportunity: Identify systems left on unnecessarily

4. Equipment Utilization
   - Meeting rooms: > 60% booked hours
   - Lifts: trips vs capacity
   - Parking: occupancy rate
   Use: Optimize space allocation
```

**Category 5: Compliance & Certification KPIs**

```
1. LEED/TREES Score Components
   - Energy performance (EUI vs baseline)
   - Water efficiency
   - IEQ (Indoor Environmental Quality)
   Target: Maintain or improve score

2. ESG Reporting Metrics (for SET-listed companies)
   - Scope 1 emissions: Direct (diesel generators)
   - Scope 2 emissions: Indirect (grid electricity)
   - Scope 3 emissions: Supply chain
   Requirement: Annual sustainability report

3. Carbon Disclosure Project (CDP) Score
   - A-list: Leadership (target)
   - B: Management
   - C: Awareness
   Importance: Investor relations, corporate reputation
```

### 6.3 KPI Configuration Schema

**Electricity Rate Configuration:**

```sql
CREATE TABLE electricity_rates (
    id SERIAL PRIMARY KEY,
    rate_name VARCHAR(100),
    rate_type VARCHAR(50),               -- 'TOU' (Time of Use), 'FLAT'
    meter_type VARCHAR(50),              -- 'RESIDENTIAL', 'COMMERCIAL', 'INDUSTRIAL'
    voltage_level VARCHAR(20),           -- 'LOW_VOLTAGE', 'MEDIUM_VOLTAGE', 'HIGH_VOLTAGE'

    -- Time-of-Use rates (THB/kWh)
    peak_rate DECIMAL(6,4),              -- e.g., 4.5000
    off_peak_rate DECIMAL(6,4),          -- e.g., 2.5000
    shoulder_rate DECIMAL(6,4),          -- e.g., 3.2000

    -- Peak hours definition (Thailand MEA/PEA)
    peak_hours_start TIME,               -- e.g., '09:00'
    peak_hours_end TIME,                 -- e.g., '22:00'

    -- Demand charge (THB/kW/month)
    demand_charge DECIMAL(8,2),          -- e.g., 300.00

    -- Service charge (THB/month)
    service_charge DECIMAL(8,2),         -- e.g., 50.00

    -- Fuel adjustment (Ft) - variable monthly
    ft_rate DECIMAL(6,4),                -- e.g., 0.1234 (changes monthly)

    -- VAT
    vat_percent DECIMAL(4,2),            -- e.g., 7.00

    -- Effective period
    effective_from DATE NOT NULL,
    effective_to DATE
);

-- Example: MEA TOU rate for commercial (medium voltage)
INSERT INTO electricity_rates
(rate_name, rate_type, meter_type, voltage_level,
 peak_rate, off_peak_rate, shoulder_rate,
 peak_hours_start, peak_hours_end,
 demand_charge, service_charge, ft_rate, vat_percent, effective_from)
VALUES
('MEA TOU Commercial MV 2025', 'TOU', 'COMMERCIAL', 'MEDIUM_VOLTAGE',
 4.5000, 2.5000, 3.2000,
 '09:00', '22:00',
 300.00, 50.00, 0.1234, 7.00, '2025-01-01');
```

### 6.4 Dashboard Design (4 Pages)

**Page 1: Executive Overview**

```sql
-- Real-time executive metrics
WITH current_month AS (
    SELECT
        SUM(total_energy_kwh) AS energy_kwh,
        MAX(peak_demand_kw) AS peak_kw
    FROM power_daily
    WHERE day >= DATE_TRUNC('month', CURRENT_DATE)
),
last_month AS (
    SELECT
        SUM(total_energy_kwh) AS energy_kwh,
        MAX(peak_demand_kw) AS peak_kw
    FROM power_daily
    WHERE day >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
      AND day < DATE_TRUNC('month', CURRENT_DATE)
),
targets AS (
    SELECT target_value
    FROM energy_targets
    WHERE target_type = 'MONTHLY_KWH'
      AND CURRENT_DATE BETWEEN effective_from AND COALESCE(effective_to, '2099-12-31')
    LIMIT 1
),
costs AS (
    SELECT SUM(total_cost_thb) AS total_cost
    FROM daily_electricity_cost
    WHERE day >= DATE_TRUNC('month', CURRENT_DATE)
),
carbon AS (
    SELECT SUM(carbon_tonnes) AS total_carbon
    FROM daily_carbon_emissions
    WHERE day >= DATE_TRUNC('month', CURRENT_DATE)
)
SELECT
    -- Current month metrics
    c.energy_kwh AS current_month_kwh,
    costs.total_cost AS current_month_cost_thb,
    carbon.total_carbon AS current_month_carbon_tonnes,

    -- Comparisons
    ((c.energy_kwh - l.energy_kwh) / l.energy_kwh * 100) AS energy_change_percent,

    -- vs Target
    (c.energy_kwh / t.target_value * 100) AS target_achievement_percent,

    -- Projected carbon tax (assuming 300 THB/tCO2e)
    (carbon.total_carbon * 300) AS projected_carbon_tax_thb,

    -- Top system breakdown
    'HVAC' AS top_consumer_system,
    '55%' AS top_consumer_percent

FROM current_month c
CROSS JOIN last_month l
CROSS JOIN targets t
CROSS JOIN costs
CROSS JOIN carbon;
```

**Widgets:**
1. **Total Energy Cost This Month** - Large number with % change vs last month
2. **Carbon Emissions** - Tonnes with projected tax cost
3. **Target Achievement** - Progress bar (energy vs target)
4. **Year-to-Date Savings** - THB saved, % reduction
5. **System Breakdown** - Pie chart (HVAC, Lighting, Lifts, Other)

**Page 2: Energy Analysis**

```sql
-- Hourly energy trend (last 24 hours)
SELECT
    hour,
    total_energy_kwh,
    peak_power_kw,
    lighting_energy_kwh,
    lift_energy_kwh,
    estimated_hvac_kwh,
    avg_power_factor
FROM building_energy_hourly
WHERE hour >= NOW() - INTERVAL '24 hours'
ORDER BY hour;
```

**Widgets:**
1. **Real-time Power** - Current kW (last reading)
2. **24-Hour Trend** - Line chart (power over time)
3. **Peak Demand Today** - vs yesterday, vs target
4. **Energy Breakdown** - Stacked bar chart (HVAC/Lighting/Lifts by hour)
5. **Power Factor** - Gauge chart (alert if < 0.85)
6. **Monthly Comparison** - This month vs last year same month

**Page 3: ESG & Compliance**

```sql
-- Annual carbon footprint trend
SELECT
    DATE_TRUNC('month', day) AS month,
    SUM(total_energy_kwh) AS total_kwh,
    SUM(carbon_tonnes) AS carbon_tonnes,
    SUM(total_energy_kwh) / MAX(b.total_area_sqm) AS eui_monthly,
    SUM(carbon_kg) / MAX(b.total_area_sqm) AS carbon_intensity
FROM daily_carbon_emissions e
CROSS JOIN building_info b
WHERE day >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY month
ORDER BY month;
```

**Widgets:**
1. **Carbon Footprint Trend** - Area chart (12 months)
2. **Energy Intensity (EUI)** - vs LEED/TREES benchmarks
3. **Certification Status** - Days until expiry, score progress
4. **Industry Benchmark** - Your building vs average
5. **Renewable Energy %** - If solar panels installed

**Page 4: Building Operations**

```sql
-- Occupancy vs energy correlation
WITH occupancy AS (
    SELECT
        DATE_TRUNC('day', time) AS day,
        SUM(CASE WHEN result = 'SUCCESS' AND direction = 'IN' THEN 1 ELSE 0 END) -
        SUM(CASE WHEN result = 'SUCCESS' AND direction = 'OUT' THEN 1 ELSE 0 END) AS net_occupancy
    FROM access_events
    WHERE time >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY day
)
SELECT
    e.day,
    e.total_energy_kwh,
    o.net_occupancy,
    (e.total_energy_kwh / NULLIF(o.net_occupancy, 0)) AS kwh_per_person
FROM (
    SELECT day, SUM(total_energy_kwh) AS total_energy_kwh
    FROM power_daily
    WHERE day >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY day
) e
LEFT JOIN occupancy o ON o.day = e.day
ORDER BY e.day;
```

**Widgets:**
1. **Occupancy Trend** - Line chart (people per day)
2. **Energy per Person** - Trend chart
3. **Equipment Uptime** - Lift/escalator availability %
4. **After-Hours Waste** - Energy used outside 6 AM - 8 PM
5. **Maintenance Alerts** - Upcoming/overdue maintenance
6. **Zone Analysis** - Energy by floor/zone

---

## 7. Cost & Carbon Calculations

### 7.1 Automated Cost Calculation

**Daily Electricity Cost (TOU Billing):**

```sql
CREATE MATERIALIZED VIEW daily_electricity_cost
WITH (timescaledb.continuous) AS
SELECT
    p.day,
    p.meter_id,
    p.total_energy_kwh,
    p.peak_demand_kw,
    r.rate_name,

    -- Energy charges (simplified - assuming off-peak rate for now)
    -- Real implementation would need hourly TOU calculation
    (p.total_energy_kwh * r.off_peak_rate) AS base_energy_charge,

    -- Demand charge (peak kW × rate)
    (p.peak_demand_kw * r.demand_charge / 30) AS daily_demand_charge,

    -- Fuel adjustment (Ft)
    (p.total_energy_kwh * r.ft_rate) AS ft_charge,

    -- Service charge (prorated daily)
    (r.service_charge / 30) AS daily_service_charge,

    -- Subtotal
    (p.total_energy_kwh * r.off_peak_rate) +
    (p.peak_demand_kw * r.demand_charge / 30) +
    (p.total_energy_kwh * r.ft_rate) +
    (r.service_charge / 30) AS subtotal,

    -- VAT
    ((p.total_energy_kwh * r.off_peak_rate) +
     (p.peak_demand_kw * r.demand_charge / 30) +
     (p.total_energy_kwh * r.ft_rate) +
     (r.service_charge / 30)) * (r.vat_percent / 100) AS vat,

    -- Total
    ((p.total_energy_kwh * r.off_peak_rate) +
     (p.peak_demand_kw * r.demand_charge / 30) +
     (p.total_energy_kwh * r.ft_rate) +
     (r.service_charge / 30)) * (1 + r.vat_percent / 100) AS total_cost_thb

FROM power_daily p
CROSS JOIN LATERAL (
    SELECT * FROM electricity_rates
    WHERE p.day >= effective_from
      AND (effective_to IS NULL OR p.day <= effective_to)
    LIMIT 1
) r;

SELECT add_continuous_aggregate_policy('daily_electricity_cost',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

**Accurate TOU Calculation (Hourly):**

```sql
-- More accurate TOU calculation using hourly data
CREATE MATERIALIZED VIEW hourly_electricity_cost
WITH (timescaledb.continuous) AS
SELECT
    p.hour,
    p.meter_id,
    p.energy_consumed_kwh,

    -- Determine rate based on time
    CASE
        WHEN EXTRACT(HOUR FROM p.hour) BETWEEN
             EXTRACT(HOUR FROM r.peak_hours_start) AND
             EXTRACT(HOUR FROM r.peak_hours_end) - 1
        THEN r.peak_rate
        ELSE r.off_peak_rate
    END AS applicable_rate,

    -- Energy charge for this hour
    p.energy_consumed_kwh *
    CASE
        WHEN EXTRACT(HOUR FROM p.hour) BETWEEN
             EXTRACT(HOUR FROM r.peak_hours_start) AND
             EXTRACT(HOUR FROM r.peak_hours_end) - 1
        THEN r.peak_rate
        ELSE r.off_peak_rate
    END AS energy_charge,

    -- Ft charge
    p.energy_consumed_kwh * r.ft_rate AS ft_charge

FROM power_hourly p
CROSS JOIN LATERAL (
    SELECT * FROM electricity_rates
    WHERE p.hour::DATE >= effective_from
      AND (effective_to IS NULL OR p.hour::DATE <= effective_to)
    LIMIT 1
) r;
```

**Monthly Bill Summary:**

```sql
SELECT
    DATE_TRUNC('month', day) AS month,

    -- Energy breakdown
    SUM(total_energy_kwh) AS total_kwh,
    SUM(base_energy_charge) AS energy_charge,
    MAX(daily_demand_charge) * 30 AS demand_charge,
    SUM(ft_charge) AS ft_charge,
    MAX(daily_service_charge) * 30 AS service_charge,
    SUM(vat) AS vat,

    -- Total
    SUM(total_cost_thb) AS total_bill_thb,

    -- Average cost per kWh
    (SUM(total_cost_thb) / SUM(total_energy_kwh)) AS avg_cost_per_kwh

FROM daily_electricity_cost
WHERE day >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '12 months')
GROUP BY month
ORDER BY month;
```

### 7.2 Carbon Emission Calculations

**Daily Carbon Emissions:**

```sql
CREATE MATERIALIZED VIEW daily_carbon_emissions
WITH (timescaledb.continuous) AS
SELECT
    p.day,
    p.meter_id,
    p.total_energy_kwh,
    cf.emission_factor,
    cf.source_reference,

    -- Carbon emissions (kgCO2e)
    (p.total_energy_kwh * cf.emission_factor) AS carbon_kg,

    -- Convert to tonnes
    (p.total_energy_kwh * cf.emission_factor / 1000) AS carbon_tonnes,

    -- Projected carbon tax (if rate defined)
    (p.total_energy_kwh * cf.emission_factor / 1000) *
        COALESCE(cf.carbon_tax_rate, 300) AS projected_tax_thb

FROM power_daily p
CROSS JOIN LATERAL (
    SELECT * FROM carbon_factors
    WHERE source = 'GRID_ELECTRICITY'
      AND p.day >= effective_from
      AND (effective_to IS NULL OR p.day <= effective_to)
    LIMIT 1
) cf;

SELECT add_continuous_aggregate_policy('daily_carbon_emissions',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
```

**Annual Carbon Report:**

```sql
SELECT
    EXTRACT(YEAR FROM day) AS year,

    -- Total emissions
    SUM(carbon_tonnes) AS total_carbon_tonnes,

    -- Per building area (carbon intensity)
    SUM(carbon_kg) / MAX(b.total_area_sqm) AS carbon_intensity_kg_per_sqm,

    -- Per occupant
    SUM(carbon_kg) / MAX(b.typical_occupancy) / 365 AS carbon_kg_per_person_per_day,

    -- Projected tax
    SUM(projected_tax_thb) AS projected_annual_tax_thb,

    -- Benchmarking
    CASE
        WHEN SUM(carbon_kg) / MAX(b.total_area_sqm) < 100 THEN 'Excellent'
        WHEN SUM(carbon_kg) / MAX(b.total_area_sqm) < 120 THEN 'Good'
        WHEN SUM(carbon_kg) / MAX(b.total_area_sqm) < 150 THEN 'Average'
        ELSE 'Needs Improvement'
    END AS performance_rating

FROM daily_carbon_emissions e
CROSS JOIN building_info b
GROUP BY year
ORDER BY year;
```

### 7.3 Monthly Performance Summary with KPI Comparisons

```sql
CREATE MATERIALIZED VIEW monthly_performance_summary
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 month', day) AS month,

    -- Energy metrics
    SUM(total_energy_kwh) AS total_energy_kwh,
    AVG(avg_power_kw) AS avg_power_kw,
    MAX(peak_power_kw) AS max_peak_power_kw,
    AVG(avg_power_factor) AS avg_power_factor,

    -- Cost metrics
    SUM(c.total_cost_thb) AS total_cost_thb,
    (SUM(c.total_cost_thb) / SUM(total_energy_kwh)) AS avg_cost_per_kwh,

    -- Carbon metrics
    SUM(co2.carbon_kg) AS total_carbon_kg,
    SUM(co2.carbon_tonnes) AS total_carbon_tonnes,
    SUM(co2.projected_tax_thb) AS projected_carbon_tax_thb,

    -- Building intensity metrics
    (SUM(total_energy_kwh) / MAX(b.total_area_sqm)) AS energy_intensity_kwh_per_sqm,
    (SUM(co2.carbon_kg) / MAX(b.total_area_sqm)) AS carbon_intensity_kg_per_sqm,

    -- Occupancy correlation (from access control)
    AVG(occ.daily_occupancy) AS avg_daily_occupancy,
    (SUM(total_energy_kwh) / NULLIF(AVG(occ.daily_occupancy), 0)) AS kwh_per_person

FROM power_daily p
LEFT JOIN daily_electricity_cost c ON c.day = p.day AND c.meter_id = p.meter_id
LEFT JOIN daily_carbon_emissions co2 ON co2.day = p.day AND co2.meter_id = p.meter_id
LEFT JOIN LATERAL (
    SELECT
        day,
        SUM(unique_employees) AS daily_occupancy
    FROM access_daily
    WHERE access_daily.day = p.day
    GROUP BY day
) occ ON TRUE
CROSS JOIN building_info b
GROUP BY month, b.total_area_sqm;

SELECT add_continuous_aggregate_policy('monthly_performance_summary',
    start_offset => INTERVAL '3 months',
    end_offset => INTERVAL '1 month',
    schedule_interval => INTERVAL '1 day');
```

### 7.4 KPI Achievement Tracking Function

```sql
CREATE OR REPLACE FUNCTION check_kpi_achievement(
    check_date DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    target_name VARCHAR(100),
    target_type VARCHAR(50),
    target_value DECIMAL(12,2),
    actual_value DECIMAL(12,2),
    achievement_percent DECIMAL(6,2),
    status VARCHAR(20),
    variance DECIMAL(12,2),
    alert_needed BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH actual_data AS (
        -- Get actual values for the period
        SELECT
            DATE_TRUNC('month', day)::DATE AS period,
            SUM(total_energy_kwh) AS actual_kwh,
            MAX(peak_demand_kw) AS actual_peak_kw,
            SUM(total_cost_thb) AS actual_cost
        FROM power_daily pd
        LEFT JOIN daily_electricity_cost c ON c.day = pd.day
        WHERE day >= DATE_TRUNC('month', check_date)
          AND day < DATE_TRUNC('month', check_date) + INTERVAL '1 month'
        GROUP BY period
    ),
    baseline_data AS (
        -- Get baseline for comparison (same period last year)
        SELECT
            SUM(total_energy_kwh) AS baseline_kwh
        FROM power_daily
        WHERE day >= DATE_TRUNC('month', check_date - INTERVAL '1 year')
          AND day < DATE_TRUNC('month', check_date - INTERVAL '1 year') + INTERVAL '1 month'
    )
    SELECT
        t.target_name,
        t.target_type,
        t.target_value,
        -- Actual value based on target type
        CASE
            WHEN t.target_type = 'MONTHLY_KWH' THEN a.actual_kwh
            WHEN t.target_type = 'PEAK_DEMAND' THEN a.actual_peak_kw
            WHEN t.target_type = 'DAILY_COST' THEN a.actual_cost
        END AS actual_value,
        -- Achievement percentage
        CASE
            WHEN t.target_type = 'MONTHLY_KWH' THEN
                (a.actual_kwh / NULLIF(t.target_value, 0) * 100)
            WHEN t.target_type = 'PEAK_DEMAND' THEN
                (a.actual_peak_kw / NULLIF(t.target_value, 0) * 100)
            WHEN t.target_type = 'DAILY_COST' THEN
                (a.actual_cost / NULLIF(t.target_value, 0) * 100)
        END AS achievement_percent,
        -- Status
        CASE
            WHEN t.target_type = 'MONTHLY_KWH' AND a.actual_kwh <= t.target_value THEN 'ACHIEVED'
            WHEN t.target_type = 'PEAK_DEMAND' AND a.actual_peak_kw <= t.target_value THEN 'ACHIEVED'
            WHEN t.target_type = 'DAILY_COST' AND a.actual_cost <= t.target_value THEN 'ACHIEVED'
            WHEN t.target_type = 'MONTHLY_KWH' AND a.actual_kwh <= t.target_value * (t.alert_threshold / 100) THEN 'ON_TRACK'
            WHEN t.target_type = 'PEAK_DEMAND' AND a.actual_peak_kw <= t.target_value * (t.alert_threshold / 100) THEN 'ON_TRACK'
            WHEN t.target_type = 'DAILY_COST' AND a.actual_cost <= t.target_value * (t.alert_threshold / 100) THEN 'ON_TRACK'
            ELSE 'AT_RISK'
        END AS status,
        -- Variance (target - actual, positive = under target)
        CASE
            WHEN t.target_type = 'MONTHLY_KWH' THEN (t.target_value - a.actual_kwh)
            WHEN t.target_type = 'PEAK_DEMAND' THEN (t.target_value - a.actual_peak_kw)
            WHEN t.target_type = 'DAILY_COST' THEN (t.target_value - a.actual_cost)
        END AS variance,
        -- Alert needed?
        CASE
            WHEN t.target_type = 'MONTHLY_KWH' AND a.actual_kwh > t.target_value * (t.alert_threshold / 100) THEN TRUE
            WHEN t.target_type = 'PEAK_DEMAND' AND a.actual_peak_kw > t.target_value * (t.alert_threshold / 100) THEN TRUE
            WHEN t.target_type = 'DAILY_COST' AND a.actual_cost > t.target_value * (t.alert_threshold / 100) THEN TRUE
            ELSE FALSE
        END AS alert_needed

    FROM energy_targets t
    CROSS JOIN actual_data a
    LEFT JOIN baseline_data b ON TRUE
    WHERE check_date >= t.effective_from
      AND (t.effective_to IS NULL OR check_date <= t.effective_to);
END;
$$ LANGUAGE plpgsql;

-- Usage example
SELECT * FROM check_kpi_achievement(CURRENT_DATE);
```

**Expected Output:**

```
target_name                    | target_value | actual_value | achievement_percent | status   | variance | alert_needed
-------------------------------|--------------|--------------|---------------------|----------|----------|-------------
Monthly Energy Reduction 2025  | 50000.00     | 48500.00     | 97.00               | ACHIEVED | 1500.00  | FALSE
Peak Demand Limit             | 100.00       | 105.00       | 105.00              | AT_RISK  | -5.00    | TRUE
Monthly Cost Budget           | 250000.00    | 245000.00    | 98.00               | ACHIEVED | 5000.00  | FALSE
```

---

## 8. Face Recognition with pgvector

### 8.1 Enable pgvector Extension

```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 8.2 Registered Persons Schema

```sql
CREATE TABLE registered_persons (
    person_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) UNIQUE,      -- Link to HR system

    -- Personal info
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    position VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),

    -- Registration
    registration_date TIMESTAMPTZ DEFAULT NOW(),
    registered_by VARCHAR(50),           -- Who registered this person
    registration_method VARCHAR(30),     -- 'BULK_IMPORT', 'SELF_SERVICE', 'ADMIN'

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    deactivated_date TIMESTAMPTZ,
    deactivated_reason TEXT,

    -- Metadata
    notes TEXT,
    photo_count INTEGER DEFAULT 0,       -- How many face embeddings registered
    last_seen TIMESTAMPTZ,               -- Last face recognition match

    -- GDPR compliance
    consent_given BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMPTZ,
    data_retention_until DATE            -- Auto-delete after this date
);

CREATE INDEX idx_person_employee ON registered_persons(employee_id);
CREATE INDEX idx_person_active ON registered_persons(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_person_department ON registered_persons(department);
```

### 8.3 Face Embeddings Storage

**From Meeting 1: 3-5 photos per person optimal**

```sql
CREATE TABLE face_embeddings (
    id BIGSERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES registered_persons(person_id) ON DELETE CASCADE,

    -- Vector embedding (ArcFace = 512 dimensions)
    embedding vector(512) NOT NULL,

    -- Capture details
    photo_source VARCHAR(20),            -- 'REGISTRATION', 'LIVE_CAPTURE', 'ADMIN_UPLOAD'
    camera_id VARCHAR(10),               -- If from live capture
    capture_date TIMESTAMPTZ DEFAULT NOW(),

    -- Quality metrics
    quality_score DECIMAL(4,3),          -- 0.000-1.000 (from face detection)
    face_size INTEGER,                   -- Pixels (larger = better quality)
    face_angle DECIMAL(5,2),             -- Degrees from frontal (0 = perfect)
    brightness_score DECIMAL(4,3),       -- Lighting quality
    sharpness_score DECIMAL(4,3),        -- Focus quality

    -- Photo metadata
    photo_metadata JSONB,                -- {wearing_mask, wearing_glasses, etc.}
    photo_path VARCHAR(255),             -- Original photo storage path

    -- Classification
    is_primary BOOLEAN DEFAULT FALSE,    -- Primary photo for display
    embedding_version VARCHAR(20),       -- Model version (e.g., 'arcface_r100')

    -- Validation
    verified BOOLEAN DEFAULT FALSE,      -- Manually verified by admin
    verified_by VARCHAR(50),
    verified_at TIMESTAMPTZ
);

-- **CRITICAL INDEX** for fast similarity search
CREATE INDEX idx_face_embedding_hnsw ON face_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Other indexes
CREATE INDEX idx_face_person ON face_embeddings(person_id);
CREATE INDEX idx_face_quality ON face_embeddings(quality_score DESC);
CREATE INDEX idx_face_source ON face_embeddings(photo_source);
```

**Index Performance:**

```
HNSW (Hierarchical Navigable Small World) parameters:
- m = 16: Max connections per layer (higher = better recall, more memory)
- ef_construction = 64: Construction time quality (higher = better index, slower build)

Performance:
- 10,000 faces: ~10ms search time
- 100,000 faces: ~15ms search time
- 1,000,000 faces: ~25ms search time
```

### 8.4 Face Recognition Events

```sql
CREATE TABLE face_recognition_events (
    id BIGSERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    camera_id VARCHAR(10) NOT NULL,

    -- Recognition result
    person_id INTEGER REFERENCES registered_persons(person_id),
    matched_embedding_id BIGINT REFERENCES face_embeddings(id),

    -- Similarity scores
    similarity_score DECIMAL(5,4),       -- 0.0000-1.0000 (cosine similarity)
    distance DECIMAL(5,4),               -- 1 - similarity (lower = better match)
    confidence VARCHAR(20),              -- 'HIGH', 'MEDIUM', 'LOW', 'NO_MATCH'

    -- Detection details
    bbox JSONB,                          -- Bounding box {x, y, w, h}
    detection_quality DECIMAL(4,3),      -- YOLO confidence

    -- Voting results (from Meeting 1: multi-frame verification)
    vote_count INTEGER,                  -- How many embeddings voted
    vote_agreement_percent DECIMAL(5,2), -- % of embeddings that agreed

    -- Photo storage
    photo_path VARCHAR(255),             -- Captured face photo
    full_frame_path VARCHAR(255),        -- Full camera frame

    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,   -- Manual verification if needed
    verified_by VARCHAR(50),
    verified_at TIMESTAMPTZ,

    -- Metadata
    notes TEXT
);

-- Hypertable for time-series
SELECT create_hypertable('face_recognition_events', 'time');

-- Indexes
CREATE INDEX idx_face_recog_camera_time ON face_recognition_events(camera_id, time DESC);
CREATE INDEX idx_face_recog_person_time ON face_recognition_events(person_id, time DESC);
CREATE INDEX idx_face_recog_confidence ON face_recognition_events(confidence, time DESC);
CREATE INDEX idx_face_recog_unverified ON face_recognition_events(time)
    WHERE is_verified = FALSE AND confidence = 'MEDIUM';
```

### 8.5 Face Recognition Queries

**8.5.1 Find Top Matches (Similarity Search)**

```sql
-- Find top 5 matches for a given face embedding
WITH query_embedding AS (
    -- This would be the 512-dim vector from live detection
    SELECT embedding FROM face_embeddings WHERE id = $1
)
SELECT
    p.person_id,
    p.employee_id,
    p.full_name,
    p.department,
    fe.id AS embedding_id,

    -- Cosine similarity (1 = identical, 0 = completely different)
    1 - (fe.embedding <=> qe.embedding) AS similarity,

    -- Distance (0 = identical, 2 = completely opposite)
    fe.embedding <=> qe.embedding AS distance,

    -- Quality score
    fe.quality_score,
    fe.photo_source,

    -- Confidence classification
    CASE
        WHEN 1 - (fe.embedding <=> qe.embedding) > 0.65 THEN 'HIGH'
        WHEN 1 - (fe.embedding <=> qe.embedding) > 0.55 THEN 'MEDIUM'
        WHEN 1 - (fe.embedding <=> qe.embedding) > 0.45 THEN 'LOW'
        ELSE 'NO_MATCH'
    END AS confidence

FROM face_embeddings fe
JOIN registered_persons p ON p.person_id = fe.person_id
CROSS JOIN query_embedding qe
WHERE p.is_active = TRUE
ORDER BY fe.embedding <=> qe.embedding  -- <=> is cosine distance operator
LIMIT 5;
```

**Threshold Selection (from Meeting 1):**

```
Similarity Score  | Distance | Confidence | Action
------------------|----------|------------|------------------
> 0.65            | < 0.35   | HIGH       | Auto-accept
0.55 - 0.65       | 0.35-0.45| MEDIUM     | Require verification
0.45 - 0.55       | 0.45-0.55| LOW        | Likely different person
< 0.45            | > 0.55   | NO_MATCH   | Reject
```

**8.5.2 Voting Mechanism (Multi-Embedding Verification)**

```sql
-- Compare against ALL embeddings for a person and vote
WITH query_embedding AS (
    SELECT $1::vector(512) AS embedding  -- Live detection embedding
),
similarity_scores AS (
    SELECT
        fe.person_id,
        fe.id AS embedding_id,
        1 - (fe.embedding <=> qe.embedding) AS similarity,
        fe.quality_score
    FROM face_embeddings fe
    CROSS JOIN query_embedding qe
    WHERE fe.person_id IN (
        -- Only check against top candidate
        SELECT p.person_id
        FROM face_embeddings fe2
        JOIN registered_persons p ON p.person_id = fe2.person_id
        CROSS JOIN query_embedding qe2
        WHERE p.is_active = TRUE
        ORDER BY fe2.embedding <=> qe2.embedding
        LIMIT 1
    )
),
votes AS (
    SELECT
        person_id,
        COUNT(*) AS total_embeddings,
        SUM(CASE WHEN similarity > 0.65 THEN 1 ELSE 0 END) AS high_confidence_votes,
        SUM(CASE WHEN similarity > 0.55 THEN 1 ELSE 0 END) AS medium_confidence_votes,
        AVG(similarity) AS avg_similarity,
        MAX(similarity) AS max_similarity
    FROM similarity_scores
    GROUP BY person_id
)
SELECT
    v.*,
    p.full_name,
    p.employee_id,

    -- Vote agreement percentage
    (high_confidence_votes::DECIMAL / total_embeddings * 100) AS vote_agreement_percent,

    -- Decision
    CASE
        WHEN (high_confidence_votes::DECIMAL / total_embeddings) >= 0.60 THEN 'MATCH'
        WHEN (medium_confidence_votes::DECIMAL / total_embeddings) >= 0.60 THEN 'POSSIBLE_MATCH'
        ELSE 'NO_MATCH'
    END AS decision,

    -- Confidence
    CASE
        WHEN (high_confidence_votes::DECIMAL / total_embeddings) >= 0.80 THEN 'HIGH'
        WHEN (high_confidence_votes::DECIMAL / total_embeddings) >= 0.60 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS confidence

FROM votes v
JOIN registered_persons p ON p.person_id = v.person_id;
```

**From Meeting 1: Voting Rules**
- 60%+ of embeddings must agree for match
- 80%+ agreement = HIGH confidence
- 60-80% agreement = MEDIUM confidence (require verification)
- < 60% agreement = NO_MATCH

**8.5.3 Registration Quality Check**

```sql
-- Check registration quality for a person
SELECT
    p.person_id,
    p.full_name,
    p.photo_count,

    -- Quality statistics
    COUNT(fe.id) AS actual_embedding_count,
    AVG(fe.quality_score) AS avg_quality,
    MIN(fe.quality_score) AS min_quality,

    -- Diversity check (ensure photos are different)
    AVG(fe.face_angle) AS avg_face_angle,
    STDDEV(fe.face_angle) AS angle_diversity,

    -- Recommendations
    CASE
        WHEN COUNT(fe.id) < 3 THEN 'Add more photos (min 3)'
        WHEN COUNT(fe.id) > 5 THEN 'Too many photos (max 5)'
        WHEN AVG(fe.quality_score) < 0.6 THEN 'Low quality photos, re-register'
        WHEN STDDEV(fe.face_angle) < 5 THEN 'Add photos from different angles'
        ELSE 'Good registration'
    END AS recommendation

FROM registered_persons p
LEFT JOIN face_embeddings fe ON fe.person_id = p.person_id
WHERE p.is_active = TRUE
GROUP BY p.person_id, p.full_name, p.photo_count
ORDER BY actual_embedding_count ASC;
```

**8.5.4 Performance Monitoring**

```sql
-- Daily recognition statistics
SELECT
    DATE_TRUNC('day', time) AS day,
    camera_id,

    -- Recognition counts
    COUNT(*) AS total_detections,
    COUNT(*) FILTER (WHERE confidence = 'HIGH') AS high_confidence,
    COUNT(*) FILTER (WHERE confidence = 'MEDIUM') AS medium_confidence,
    COUNT(*) FILTER (WHERE confidence = 'LOW') AS low_confidence,
    COUNT(*) FILTER (WHERE confidence = 'NO_MATCH') AS no_match,

    -- Unique persons
    COUNT(DISTINCT person_id) AS unique_persons,

    -- Average similarity
    AVG(similarity_score) FILTER (WHERE person_id IS NOT NULL) AS avg_similarity,

    -- Accuracy metrics (if verified)
    COUNT(*) FILTER (WHERE is_verified = TRUE) AS verified_count,
    COUNT(*) FILTER (WHERE is_verified = TRUE AND confidence = 'HIGH') AS correctly_identified

FROM face_recognition_events
WHERE time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY day, camera_id
ORDER BY day DESC, camera_id;
```

### 8.6 Integration with Access Control

```sql
-- Match face recognition with door access
CREATE MATERIALIZED VIEW access_with_face_verification
AS
SELECT
    a.time AS access_time,
    a.door_id,
    a.employee_id AS card_employee_id,
    a.result AS access_result,

    -- Face recognition within ±5 seconds
    f.time AS face_time,
    p.employee_id AS face_employee_id,
    f.confidence AS face_confidence,
    f.similarity_score,

    -- Match validation
    CASE
        WHEN a.employee_id = p.employee_id THEN 'MATCH'
        WHEN a.employee_id IS NULL THEN 'NO_CARD'
        WHEN p.employee_id IS NULL THEN 'NO_FACE'
        ELSE 'MISMATCH'
    END AS verification_status,

    -- Security alert (card + face mismatch = possible fraud)
    CASE
        WHEN a.employee_id != p.employee_id
             AND a.result = 'SUCCESS'
             AND f.confidence = 'HIGH'
        THEN TRUE
        ELSE FALSE
    END AS security_alert

FROM access_events a
LEFT JOIN face_recognition_events f
    ON f.camera_id = 'CAMERA_' || a.door_id
    AND f.time BETWEEN a.time - INTERVAL '5 seconds'
                   AND a.time + INTERVAL '5 seconds'
LEFT JOIN registered_persons p ON p.person_id = f.person_id
WHERE a.time >= NOW() - INTERVAL '90 days';

-- Security alerts query
SELECT *
FROM access_with_face_verification
WHERE security_alert = TRUE
ORDER BY access_time DESC;
```

---

## 9. Data Lifecycle Management

### 9.1 Compression Policies

**Purpose:** Reduce storage costs by compressing old data (90-95% savings)

**9.1.1 Enable Compression**

```sql
-- Power readings: compress after 7 days
ALTER TABLE power_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'meter_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('power_readings', INTERVAL '7 days');

-- Lighting readings: compress after 7 days
ALTER TABLE lighting_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'zone_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('lighting_readings', INTERVAL '7 days');

-- Lift events: compress after 7 days
ALTER TABLE lift_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'equipment_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('lift_events', INTERVAL '7 days');

-- Access events: compress after 14 days (security audit trail)
ALTER TABLE access_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'door_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('access_events', INTERVAL '14 days');

-- Fire system: compress after 7 days
ALTER TABLE fire_system_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'sensor_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('fire_system_readings', INTERVAL '7 days');

-- CCTV counting: compress after 7 days
ALTER TABLE counting_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'camera_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('counting_events', INTERVAL '7 days');

-- Face recognition: compress after 30 days (keep recent for verification)
ALTER TABLE face_recognition_events SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'camera_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('face_recognition_events', INTERVAL '30 days');
```

**Compression Statistics:**

```sql
-- View compression stats
SELECT
    h.table_name,
    pg_size_pretty(total_bytes) AS total_size,
    pg_size_pretty(compressed_bytes) AS compressed_size,
    pg_size_pretty(uncompressed_bytes) AS uncompressed_size,
    ROUND((1 - compressed_bytes::DECIMAL / NULLIF(total_bytes, 0)) * 100, 2) AS compression_ratio_percent
FROM timescaledb_information.hypertables h
LEFT JOIN LATERAL (
    SELECT
        SUM(total_bytes) AS total_bytes,
        SUM(compressed_total_bytes) AS compressed_bytes,
        SUM(uncompressed_total_bytes) AS uncompressed_bytes
    FROM timescaledb_information.chunks c
    WHERE c.hypertable_name = h.table_name
) stats ON TRUE
ORDER BY total_bytes DESC;
```

**Expected Results:**

```
table_name              | total_size | compressed_size | uncompressed_size | compression_ratio_percent
------------------------|------------|-----------------|-------------------|-------------------------
power_readings          | 1000 MB    | 80 MB           | 920 MB            | 92.00
access_events           | 500 MB     | 50 MB           | 450 MB            | 90.00
lighting_readings       | 300 MB     | 25 MB           | 275 MB            | 91.67
```

### 9.2 Data Retention Policies

**Purpose:** Automatically delete old data to save storage

**9.2.1 Raw Data Retention**

```sql
-- Power readings: keep 90 days
SELECT add_retention_policy('power_readings', INTERVAL '90 days');

-- Lighting: keep 90 days
SELECT add_retention_policy('lighting_readings', INTERVAL '90 days');

-- Lift events: keep 90 days
SELECT add_retention_policy('lift_events', INTERVAL '90 days');

-- Access events: keep 1 year (security/audit requirement)
SELECT add_retention_policy('access_events', INTERVAL '1 year');

-- Fire system: keep 1 year (safety compliance)
SELECT add_retention_policy('fire_system_readings', INTERVAL '1 year');

-- CCTV counting: keep 30 days (PDPA compliance)
SELECT add_retention_policy('counting_events', INTERVAL '30 days');

-- Face recognition: keep 30 days (PDPA compliance)
SELECT add_retention_policy('face_recognition_events', INTERVAL '30 days');
```

**9.2.2 Aggregate Data Retention**

```sql
-- Hourly aggregates: keep 2 years
SELECT add_retention_policy('power_hourly', INTERVAL '2 years');
SELECT add_retention_policy('lighting_hourly', INTERVAL '2 years');
SELECT add_retention_policy('counting_hourly', INTERVAL '2 years');
SELECT add_retention_policy('building_energy_hourly', INTERVAL '2 years');

-- Daily aggregates: keep 3 years
SELECT add_retention_policy('power_daily', INTERVAL '3 years');
SELECT add_retention_policy('lift_daily', INTERVAL '3 years');
SELECT add_retention_policy('access_daily', INTERVAL '3 years');
SELECT add_retention_policy('daily_electricity_cost', INTERVAL '3 years');
SELECT add_retention_policy('daily_carbon_emissions', INTERVAL '3 years');

-- Monthly aggregates: keep 5 years
SELECT add_retention_policy('monthly_performance_summary', INTERVAL '5 years');
```

### 9.3 Data Lifecycle Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Data Lifecycle Timeline                      │
└─────────────────────────────────────────────────────────────────┘

Day 0-7:    ████████ Raw data (uncompressed)
            - Fast queries
            - All details available
            - ~1 GB storage

Day 7-90:   ████████ Raw data (COMPRESSED)
            - Still queryable (transparent decompression)
            - Same query interface
            - ~100 MB storage (90% savings!)

Day 90+:    ████████ Raw data DELETED
            - Aggregates still available:
              * Hourly: up to 2 years
              * Daily: up to 3 years
              * Monthly: up to 5 years

Year 2+:    ████████ Hourly aggregates deleted
            - Daily/monthly still available

Year 3+:    ████████ Daily aggregates deleted
            - Monthly still available

Year 5+:    ████████ All data deleted
            - Export to archive storage if needed
```

### 9.4 Manual Data Management

**9.4.1 Decompress Specific Chunks**

```sql
-- If you need to update old data, decompress first
SELECT decompress_chunk('_timescaledb_internal._hyper_1_25_chunk');

-- Update data
UPDATE power_readings
SET power_kw = 95
WHERE time = '2024-01-15 10:30:00' AND meter_id = 'MAIN_METER_01';

-- Re-compress
SELECT compress_chunk('_timescaledb_internal._hyper_1_25_chunk');
```

**9.4.2 Manual Compression (Before Policy Time)**

```sql
-- Compress all chunks older than 3 days manually
SELECT compress_chunk(c.chunk_name)
FROM timescaledb_information.chunks c
WHERE c.hypertable_name = 'power_readings'
  AND c.range_end < NOW() - INTERVAL '3 days'
  AND NOT c.is_compressed;
```

**9.4.3 Export Before Deletion**

```sql
-- Export data before retention policy deletes it
-- Export to CSV for archival
COPY (
    SELECT * FROM power_readings
    WHERE time >= '2023-01-01' AND time < '2024-01-01'
) TO '/backup/power_readings_2023.csv' CSV HEADER;

-- Or export to compressed binary format
COPY (
    SELECT * FROM power_readings
    WHERE time >= '2023-01-01' AND time < '2024-01-01'
) TO PROGRAM 'gzip > /backup/power_readings_2023.csv.gz' CSV HEADER;
```

### 9.5 Backup Strategy

**9.5.1 Continuous Archiving (WAL)**

```bash
# postgresql.conf configuration
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /backup/wal/%f && cp %p /backup/wal/%f'
archive_timeout = 300  # Force WAL switch every 5 minutes

# Enable in TimescaleDB
# This allows point-in-time recovery (PITR)
```

**9.5.2 Daily Backup Script**

```bash
#!/bin/bash
# /opt/scripts/backup_timescaledb.sh

BACKUP_DIR="/backup/timescaledb"
DB_NAME="building_management"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR/{full,config,incremental}

# 1. Full database backup (daily at 2 AM)
echo "Starting full backup at $(date)"
pg_dump -Fc -Z9 $DB_NAME > $BACKUP_DIR/full/full_backup_$DATE.dump

# 2. Configuration tables only (fast, frequent)
echo "Backing up configuration tables"
pg_dump -Fc -Z9 \
    -t energy_targets \
    -t electricity_rates \
    -t carbon_factors \
    -t building_info \
    -t equipment_registry \
    -t registered_persons \
    -t face_embeddings \
    $DB_NAME > $BACKUP_DIR/config/config_backup_$DATE.dump

# 3. Cleanup old backups
echo "Cleaning up backups older than $RETENTION_DAYS days"
find $BACKUP_DIR/full -name "*.dump" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR/config -name "*.dump" -mtime +$RETENTION_DAYS -delete

# 4. Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/full/full_backup_$DATE.dump \
#     s3://my-bucket/backups/timescaledb/full/ \
#     --storage-class GLACIER

# 5. Verify backup integrity
echo "Verifying backup"
pg_restore -l $BACKUP_DIR/full/full_backup_$DATE.dump > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Backup verification successful"
else
    echo "ERROR: Backup verification failed!" | mail -s "Backup Failed" admin@company.com
fi

echo "Backup completed at $(date)"
```

**9.5.3 Restore Procedures**

```bash
# Full restore
pg_restore -d $DB_NAME -c $BACKUP_DIR/full/full_backup_20250104_020000.dump

# Restore specific table
pg_restore -d $DB_NAME -t registered_persons -c \
    $BACKUP_DIR/config/config_backup_20250104_020000.dump

# Point-in-time recovery (PITR)
# 1. Restore from base backup
pg_restore -d $DB_NAME $BACKUP_DIR/full/full_backup_20250104_020000.dump

# 2. Create recovery.conf
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /backup/wal/%f %p'
recovery_target_time = '2025-01-04 14:30:00'
EOF

# 3. Restart PostgreSQL (will replay WAL until target time)
systemctl restart postgresql
```

**9.5.4 Backup Monitoring**

```sql
-- Create backup log table
CREATE TABLE backup_logs (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(20),         -- 'FULL', 'CONFIG', 'INCREMENTAL'
    backup_path VARCHAR(255),
    backup_size_bytes BIGINT,
    backup_duration_seconds INTEGER,
    status VARCHAR(20),              -- 'SUCCESS', 'FAILED'
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Log backup completion
INSERT INTO backup_logs
(backup_type, backup_path, backup_size_bytes, backup_duration_seconds, status)
VALUES
('FULL', '/backup/full_backup_20250104_020000.dump', 1024000000, 180, 'SUCCESS');

-- Monitor backup health
SELECT
    backup_type,
    MAX(completed_at) AS last_backup,
    NOW() - MAX(completed_at) AS time_since_last_backup,
    COUNT(*) FILTER (WHERE completed_at >= CURRENT_DATE - INTERVAL '7 days') AS backups_last_week,
    COUNT(*) FILTER (WHERE status = 'FAILED' AND completed_at >= CURRENT_DATE - INTERVAL '7 days') AS failures_last_week
FROM backup_logs
GROUP BY backup_type;
```

---

## 10. Performance Optimization

### 10.1 Index Optimization

**10.1.1 Monitor Index Usage**

```sql
-- Find unused indexes
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Find missing indexes (based on sequential scans)
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / NULLIF(seq_scan, 0) AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;
```

**10.1.2 Create Targeted Indexes**

```sql
-- Partial index for high power alerts
CREATE INDEX idx_power_high_demand ON power_readings(time, demand_kw)
WHERE demand_kw > 80;

-- Partial index for security incidents
CREATE INDEX idx_access_security ON access_events(time, employee_id, result)
WHERE result IN ('DENIED', 'UNAUTHORIZED');

-- Multi-column index for common queries
CREATE INDEX idx_face_recog_camera_person_time
ON face_recognition_events(camera_id, person_id, time DESC);

-- Expression index for time-based queries
CREATE INDEX idx_power_hour ON power_readings(date_trunc('hour', time), meter_id);
```

### 10.2 Query Performance Monitoring

**10.2.1 Enable pg_stat_statements**

```sql
-- Add to postgresql.conf:
shared_preload_libraries = 'timescaledb,pg_stat_statements'
pg_stat_statements.track = all

-- Restart PostgreSQL, then:
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

**10.2.2 Find Slow Queries**

```sql
-- Top 20 slowest queries
SELECT
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(max_exec_time::numeric, 2) AS max_time_ms,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND((100 * total_exec_time / SUM(total_exec_time) OVER ())::numeric, 2) AS percent_total
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Most frequent queries
SELECT
    query,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND((100 * calls / SUM(calls) OVER ())::numeric, 2) AS percent_calls
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;
```

**10.2.3 Analyze Query Plans**

```sql
-- Explain analyze for optimization
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
SELECT
    hour,
    total_energy_kwh,
    peak_power_kw
FROM building_energy_hourly
WHERE hour >= NOW() - INTERVAL '24 hours'
ORDER BY hour DESC;

-- Look for:
-- - Sequential Scans (bad on large tables)
-- - High execution time
-- - Missing indexes
```

### 10.3 Connection Pooling

**10.3.1 PgBouncer Configuration**

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
building_management = host=localhost port=5432 dbname=building_management

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool settings
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5

# Performance
server_idle_timeout = 600
server_lifetime = 3600
```

**10.3.2 Application Connection Pooling (SQLAlchemy)**

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Use PgBouncer
engine = create_engine(
    'postgresql://user:pass@localhost:6432/building_management',
    poolclass=QueuePool,
    pool_size=20,              # Number of persistent connections
    max_overflow=10,           # Additional connections if needed
    pool_pre_ping=True,        # Verify connections before using
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo_pool=True             # Log pool events (debug)
)
```

### 10.4 TimescaleDB-Specific Optimizations

**10.4.1 Chunk Size Tuning**

```sql
-- Check current chunk sizes
SELECT
    hypertable_name,
    chunk_name,
    range_start,
    range_end,
    pg_size_pretty(total_bytes) AS chunk_size
FROM timescaledb_information.chunks
WHERE hypertable_name = 'power_readings'
ORDER BY range_start DESC
LIMIT 10;

-- Adjust chunk interval (if chunks too large/small)
-- Default: 7 days, optimal: 1-7 days depending on data volume
SELECT set_chunk_time_interval('power_readings', INTERVAL '1 day');
```

**10.4.2 Parallel Query Settings**

```sql
-- Enable parallel queries (postgresql.conf)
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
parallel_setup_cost = 1000
parallel_tuple_cost = 0.1

-- For specific large queries
SET max_parallel_workers_per_gather = 4;
SELECT
    DATE_TRUNC('day', time) AS day,
    SUM(power_kw) AS total_power
FROM power_readings
WHERE time >= '2024-01-01'
GROUP BY day;
```

**10.4.3 Memory Settings**

```sql
-- postgresql.conf tuning for TimescaleDB

# Memory (for server with 16 GB RAM)
shared_buffers = 4GB                    # 25% of RAM
effective_cache_size = 12GB             # 75% of RAM
work_mem = 64MB                         # For complex queries
maintenance_work_mem = 1GB              # For CREATE INDEX, VACUUM

# TimescaleDB specific
timescaledb.max_background_workers = 8
```

### 10.5 Materialized View Refresh Optimization

```sql
-- Check continuous aggregate refresh status
SELECT
    view_name,
    completed_threshold,
    invalidation_threshold,
    last_run_started_at,
    last_run_status
FROM timescaledb_information.continuous_aggregate_stats;

-- Manually refresh if needed
CALL refresh_continuous_aggregate('power_hourly',
    '2025-01-01', '2025-01-02');

-- Adjust refresh schedule for lower load
SELECT remove_continuous_aggregate_policy('power_hourly');
SELECT add_continuous_aggregate_policy('power_hourly',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 hour',      -- Reduced from 10 minutes
    schedule_interval => INTERVAL '1 hour'); -- Refresh less frequently
```

---

## 11. Security & Compliance

### 11.1 Row-Level Security (RLS)

**11.1.1 Enable RLS for Sensitive Data**

```sql
-- Enable RLS on face recognition events
ALTER TABLE face_recognition_events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their department's data
CREATE POLICY face_recog_department_policy ON face_recognition_events
FOR SELECT
USING (
    person_id IN (
        SELECT person_id FROM registered_persons
        WHERE department = current_setting('app.user_department', TRUE)
    )
    OR current_setting('app.user_role', TRUE) = 'admin'
);

-- Policy: Admins can see everything
CREATE POLICY face_recog_admin_policy ON face_recognition_events
FOR ALL
USING (current_setting('app.user_role', TRUE) = 'admin');

-- Set user context in application
-- Python example:
import psycopg2
conn = psycopg2.connect(...)
cursor = conn.cursor()
cursor.execute("SET app.user_department = 'IT'")
cursor.execute("SET app.user_role = 'user'")
```

**11.1.2 Access Control by Role**

```sql
-- Create roles
CREATE ROLE energy_viewer;
CREATE ROLE facility_manager;
CREATE ROLE security_officer;
CREATE ROLE admin;

-- Grant permissions
-- Energy viewer: read-only on power/lighting
GRANT SELECT ON power_readings, lighting_readings TO energy_viewer;
GRANT SELECT ON power_hourly, power_daily TO energy_viewer;

-- Facility manager: read/write on equipment, read on energy
GRANT SELECT ON ALL TABLES IN SCHEMA public TO facility_manager;
GRANT INSERT, UPDATE ON equipment_registry TO facility_manager;
GRANT INSERT, UPDATE ON energy_targets TO facility_manager;

-- Security officer: full access to access control and face recognition
GRANT SELECT, INSERT, UPDATE ON access_events TO security_officer;
GRANT SELECT, INSERT, UPDATE ON face_recognition_events TO security_officer;
GRANT SELECT, INSERT, UPDATE ON registered_persons TO security_officer;

-- Admin: full access
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;
```

### 11.2 Data Anonymization

**11.2.1 Anonymization Function (for dev/test)**

```sql
CREATE OR REPLACE FUNCTION anonymize_personal_data()
RETURNS void AS $$
BEGIN
    -- Anonymize registered persons
    UPDATE registered_persons
    SET
        full_name = 'Employee ' || person_id,
        email = 'employee' || person_id || '@example.com',
        phone = '0XX-XXX-' || LPAD(person_id::TEXT, 4, '0'),
        notes = NULL;

    -- Clear face photos (keep embeddings for testing)
    UPDATE face_embeddings SET photo_path = NULL;
    UPDATE face_recognition_events SET photo_path = NULL, full_frame_path = NULL;

    -- Anonymize access events
    UPDATE access_events SET card_id = 'CARD_' || id;

    RAISE NOTICE 'Personal data anonymized successfully';
END;
$$ LANGUAGE plpgsql;

-- Execute for dev/test environment
SELECT anonymize_personal_data();
```

**11.2.2 GDPR Compliance - Right to be Forgotten**

```sql
CREATE OR REPLACE FUNCTION delete_person_data(p_employee_id VARCHAR(20))
RETURNS void AS $$
DECLARE
    v_person_id INTEGER;
BEGIN
    -- Get person_id
    SELECT person_id INTO v_person_id
    FROM registered_persons
    WHERE employee_id = p_employee_id;

    IF v_person_id IS NULL THEN
        RAISE EXCEPTION 'Person not found: %', p_employee_id;
    END IF;

    -- Delete face recognition events (cascades to related tables)
    DELETE FROM face_recognition_events WHERE person_id = v_person_id;

    -- Delete face embeddings (includes photos)
    DELETE FROM face_embeddings WHERE person_id = v_person_id;

    -- Anonymize access events (can't delete due to audit trail)
    UPDATE access_events
    SET employee_id = NULL, card_id = 'DELETED_' || id
    WHERE employee_id = p_employee_id;

    -- Delete person record
    DELETE FROM registered_persons WHERE person_id = v_person_id;

    RAISE NOTICE 'Person data deleted: % (person_id: %)', p_employee_id, v_person_id;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT delete_person_data('EMP001');
```

### 11.3 Audit Logging

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    table_name VARCHAR(50),
    operation VARCHAR(10),           -- 'INSERT', 'UPDATE', 'DELETE'
    user_name VARCHAR(50),
    user_ip INET,
    old_data JSONB,
    new_data JSONB,
    query TEXT
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO audit_log (table_name, operation, user_name, old_data, query)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(OLD), current_query());
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO audit_log (table_name, operation, user_name, old_data, new_data, query)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(OLD), row_to_json(NEW), current_query());
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO audit_log (table_name, operation, user_name, new_data, query)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, row_to_json(NEW), current_query());
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_registered_persons
AFTER INSERT OR UPDATE OR DELETE ON registered_persons
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_energy_targets
AFTER INSERT OR UPDATE OR DELETE ON energy_targets
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

### 11.4 Encryption

**11.4.1 Encryption at Rest**

```bash
# Use PostgreSQL built-in encryption
# Initialize cluster with encryption
initdb -D /var/lib/postgresql/data --data-checksums --encoding=UTF8

# Or use disk-level encryption (LUKS)
cryptsetup luksFormat /dev/sdb
cryptsetup open /dev/sdb pgdata
mkfs.ext4 /dev/mapper/pgdata
mount /dev/mapper/pgdata /var/lib/postgresql/data
```

**11.4.2 Encryption in Transit**

```bash
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
ssl_ca_file = '/etc/ssl/certs/ca.crt'

# Require SSL for all connections
# pg_hba.conf
hostssl all all 0.0.0.0/0 md5
```

**11.4.3 Column-Level Encryption (for sensitive data)**

```sql
-- Install pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive columns
CREATE TABLE employee_sensitive (
    employee_id VARCHAR(20) PRIMARY KEY,
    encrypted_ssn BYTEA,  -- Social Security Number (encrypted)
    encrypted_salary BYTEA
);

-- Insert encrypted data
INSERT INTO employee_sensitive (employee_id, encrypted_ssn, encrypted_salary)
VALUES (
    'EMP001',
    pgp_sym_encrypt('123-45-6789', 'encryption_key'),
    pgp_sym_encrypt('50000', 'encryption_key')
);

-- Query encrypted data
SELECT
    employee_id,
    pgp_sym_decrypt(encrypted_ssn, 'encryption_key') AS ssn,
    pgp_sym_decrypt(encrypted_salary, 'encryption_key') AS salary
FROM employee_sensitive;
```

---

## 12. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Week 1: Database Setup**
- [ ] Install PostgreSQL 15+
- [ ] Install TimescaleDB extension
- [ ] Install pgvector extension
- [ ] Configure server (memory, connections)
- [ ] Setup PgBouncer connection pooling
- [ ] Configure backup system

**Week 2: Core Schema**
- [ ] Create all hypertables (6 systems)
- [ ] Create configuration tables
- [ ] Create face recognition tables
- [ ] Setup indexes
- [ ] Enable compression policies
- [ ] Setup retention policies

### Phase 2: Data Aggregation (Weeks 3-4)

**Week 3: Continuous Aggregates**
- [ ] Create hourly aggregates (all systems)
- [ ] Create daily aggregates
- [ ] Create building-wide energy summary
- [ ] Test aggregate refresh performance
- [ ] Configure refresh policies

**Week 4: KPI & Calculations**
- [ ] Create cost calculation views
- [ ] Create carbon emission views
- [ ] Create monthly summary views
- [ ] Implement KPI achievement function
- [ ] Setup initial targets and rates

### Phase 3: Integration (Weeks 5-6)

**Week 5: API Integration**
- [ ] Design data ingestion API (FastAPI)
- [ ] Implement authentication
- [ ] Create endpoints for each system
- [ ] Implement bulk insert optimization
- [ ] Setup API rate limiting

**Week 6: Face Recognition Integration**
- [ ] Implement vector similarity search
- [ ] Create registration API
- [ ] Implement voting mechanism
- [ ] Setup photo storage (S3/local)
- [ ] Test performance (1000+ faces)

### Phase 4: Dashboard & Reporting (Weeks 7-8)

**Week 7: Backend APIs**
- [ ] Executive dashboard API
- [ ] Energy analysis API
- [ ] ESG reporting API
- [ ] Building operations API
- [ ] WebSocket for real-time updates

**Week 8: Reports & Alerts**
- [ ] Daily/weekly/monthly reports
- [ ] Email notification system
- [ ] Line Notify integration
- [ ] Alert threshold monitoring
- [ ] Export functionality (PDF/Excel)

### Phase 5: Security & Optimization (Weeks 9-10)

**Week 9: Security**
- [ ] Implement row-level security
- [ ] Setup audit logging
- [ ] Configure SSL/TLS
- [ ] GDPR compliance functions
- [ ] Security testing

**Week 10: Performance Tuning**
- [ ] Query optimization
- [ ] Index tuning
- [ ] Load testing
- [ ] Monitoring setup (Grafana)
- [ ] Documentation

### Phase 6: Production (Week 11-12)

**Week 11: Deployment**
- [ ] Production environment setup
- [ ] Data migration (if existing system)
- [ ] Backup verification
- [ ] Disaster recovery testing
- [ ] Performance baseline

**Week 12: Go-Live**
- [ ] User training
- [ ] Monitoring dashboards
- [ ] Support procedures
- [ ] Performance monitoring
- [ ] Handover documentation

---

## 13. Next Steps

### 13.1 Immediate Actions

1. **Confirm Requirements:**
   - Review 6 system integration requirements
   - Confirm KPI priorities with stakeholders
   - Verify API specifications from customer

2. **Infrastructure Planning:**
   - Server specifications (CPU, RAM, storage)
   - Network architecture
   - Backup storage location
   - Development/staging environments

3. **Team Preparation:**
   - Database administrator assignment
   - Backend developer (FastAPI)
   - Frontend developer (dashboard)
   - DevOps for deployment

### 13.2 Future Enhancements

**Advanced Analytics:**
- Machine learning for energy prediction
- Anomaly detection (unusual consumption patterns)
- Predictive maintenance (equipment failures)
- Occupancy forecasting

**Additional Integrations:**
- Weather API (correlate energy with temperature)
- Solar panel monitoring (if installed)
- Water consumption tracking
- Indoor air quality sensors

**Mobile Application:**
- Real-time alerts on mobile
- Building access via face recognition
- Energy consumption notifications
- Manager approval workflows

**Advanced Reporting:**
- Custom report builder (drag-and-drop)
- Automated report scheduling
- Multi-building comparison
- Tenant billing (if applicable)

### 13.3 Questions for Next Meeting

1. **Data Sources:**
   - API specifications available?
   - Authentication methods?
   - Sample data for testing?

2. **Infrastructure:**
   - On-premise or cloud deployment?
   - Server specifications decided?
   - Network security requirements?

3. **User Access:**
   - How many users?
   - Role definitions?
   - Single sign-on (SSO) required?

4. **Compliance:**
   - Any specific industry regulations?
   - Data retention requirements?
   - Audit frequency?

---

## Appendix A: System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                        Building Management System                     │
│                         (TimescaleDB Architecture)                    │
└───────────────────────────────────────────────────────────────────────┘

┌─────────────────────────── Data Sources ─────────────────────────────┐
│                                                                        │
│  [Main Power]  [Lighting]  [Lift/Esc]  [Access]  [Fire]  [CCTV]     │
│      API         API         API         API      API      API       │
│       │           │            │           │        │        │        │
└───────┼───────────┼────────────┼───────────┼────────┼────────┼────────┘
        │           │            │           │        │        │
        └───────────┴────────────┴───────────┴────────┴────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │   FastAPI Backend       │
                    │  - Authentication       │
                    │  - Rate Limiting        │
                    │  - Data Validation      │
                    │  - Bulk Insert          │
                    └────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐  ┌────────────▼─────────┐  ┌──────────▼─────────┐
│   Hypertables  │  │  Continuous Aggs     │  │  Configuration     │
│                │  │                      │  │                    │
│ • power_readings│  │ • power_hourly      │  │ • energy_targets   │
│ • lighting_..   │  │ • power_daily       │  │ • elec_rates       │
│ • lift_events   │  │ • lighting_hourly   │  │ • carbon_factors   │
│ • access_events │  │ • building_energy   │  │ • building_info    │
│ • fire_system   │  │ • daily_cost        │  │ • equipment_reg    │
│ • counting_..   │  │ • daily_carbon      │  │                    │
│ • face_recog    │  │ • monthly_summary   │  │ Face Recognition:  │
│                 │  │                      │  │ • registered_pers  │
│ Compressed 90%  │  │ Auto-refresh         │  │ • face_embeddings  │
│ after 7 days    │  │ every 10min-1day     │  │   (pgvector)       │
└────────┬────────┘  └──────────┬───────────┘  └──────────┬─────────┘
         │                      │                          │
         └──────────────────────┼──────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Query Layer          │
                    │  - KPI Calculations    │
                    │  - Vector Search       │
                    │  - Aggregations        │
                    │  - Alerts              │
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌───────────▼──────────┐  ┌────────▼────────┐
│   Dashboard    │  │   REST API           │  │   WebSocket     │
│                │  │                      │  │                 │
│ • Executive    │  │ • Energy queries     │  │ • Real-time     │
│ • Energy       │  │ • Face recognition   │  │   updates       │
│ • ESG          │  │ • Reports            │  │ • Alerts        │
│ • Operations   │  │ • Configuration      │  │ • Live charts   │
└────────────────┘  └──────────────────────┘  └─────────────────┘

┌─────────────────── Data Lifecycle ────────────────────┐
│                                                        │
│  Day 0-7:    Uncompressed (fast queries)              │
│  Day 7-90:   Compressed 90% (still queryable)         │
│  Day 90+:    Raw deleted, aggregates remain           │
│  Year 2+:    Hourly deleted, daily/monthly remain     │
│  Year 5+:    Archive to cold storage                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Appendix B: Performance Benchmarks

**Expected Performance (Server: 4 vCPU, 8GB RAM, SSD)**

| Operation | Expected Time | Notes |
|-----------|---------------|-------|
| Insert 1000 power readings | 50-100ms | Batch insert |
| Query hourly data (24h) | 5-10ms | Continuous aggregate |
| Query daily data (1 year) | 10-20ms | Continuous aggregate |
| Face similarity search (100k faces) | 15-25ms | HNSW index |
| Real-time dashboard load | 200-500ms | 4 API calls parallel |
| Monthly report generation | 1-2 seconds | Full calculations |
| Compression job (1 day chunk) | 30-60 seconds | Background job |
| Daily backup (10GB database) | 2-5 minutes | pg_dump with compression |

---

## Appendix C: Storage Estimates

**Annual Storage Requirements (4 cameras, 10 power meters, 50 zones)**

| Data Type | Sampling | Rows/Year | Uncompressed | Compressed | Final |
|-----------|----------|-----------|--------------|------------|-------|
| Power readings | 5 min | 1,051,200 | 1.0 GB | 100 MB | 100 MB |
| Lighting | 10 min | 2,628,000 | 1.5 GB | 150 MB | 150 MB |
| Lift events | Events | 500,000 | 250 MB | 25 MB | 25 MB |
| Access events | Events | 1,000,000 | 500 MB | 50 MB | **1 year retention** |
| Fire system | 1 min | 26,280,000 | 3.0 GB | 300 MB | **1 year retention** |
| Counting events | Events | 100,000 | 50 MB | 5 MB | **30 days only** |
| Face recognition | Events | 50,000 | 500 MB | 50 MB | **30 days only** |
| Face embeddings | - | 5,000 | 10 MB | - | **Permanent** |
| Aggregates (hourly/daily) | - | - | 200 MB | - | **2-5 years** |
| **Total Year 1** | | | **~7 GB** | **~1 GB** | **~1 GB** |
| **Total Year 3** | | | | | **~3 GB** |

**Notes:**
- Raw data compressed 90% after 7 days
- CCTV data (counting + face) deleted after 30 days (PDPA)
- Access and fire data kept 1 year (compliance)
- Aggregates provide historical analysis even after raw data deleted

---

**Meeting Note 3 Complete**

**Total Pages:** 60+
**Total Words:** ~15,000
**Schema Objects:** 25+ tables/views
**Code Examples:** 100+

This comprehensive meeting note documents all decisions, schemas, queries, and implementation details for the TimescaleDB-based Building Management System with IoT integration and face recognition capabilities.
