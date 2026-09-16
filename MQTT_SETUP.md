# MQTT Setup Guide - E-Nose Cloud Backend

## Overview

Backend Rust ini mendukung **dual input**: HTTP API dan MQTT subscriber. Data dari kedua sumber masuk ke PostgreSQL yang sama dan tampil di dashboard yang sama.

---

## Architecture

```
ESP32-S3 (DHT22) ──MQTT Publish──> MQTT Broker ──Subscribe──> Backend Rust
                                                                    │
HTTP Client ──POST /api/v1/measurements──────────────────────────►│
                                                                    │
                                                                    ▼
                                                              PostgreSQL
                                                                    │
                                                                    ▼
                                                              Dashboard
```

---

## MQTT Configuration

### Environment Variables

Tambahkan ke file `.env`:

```env
# Enable MQTT subscriber (set to true)
MQTT_ENABLED=true

# MQTT Broker connection
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883

# Authentication (optional, leave empty for public brokers)
MQTT_USERNAME=
MQTT_PASSWORD=

# Client ID (unique identifier for this backend instance)
MQTT_CLIENT_ID=enose-cloud

# Topic to subscribe
# Wildcard '+' supports multiple devices: enose/ESP32-001/measurement, enose/ESP32-002/measurement, etc.
MQTT_TOPIC=enose/+/measurement

# TLS/SSL (set to true for encrypted connection)
MQTT_TLS=false
```

### Railway Deployment

Untuk Railway, tambahkan environment variables di **Service Settings → Variables**:

```
MQTT_ENABLED=true
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
MQTT_TOPIC=enose/+/measurement
```

---

## MQTT Payload Format

ESP32-S3 harus publish JSON dengan format berikut:

### Topic Pattern
```
enose/ESP32-001/measurement
```

### JSON Payload
```json
{
  "sample_id": 1,
  "score": 28.5,
  "accuracy": 72.0,
  "source": "dht22",
  "device_id": "ESP32-001",
  "features": [285, 720, 0, 0, 0, 0, 0, 0]
}
```

### Field Validation

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `sample_id` | integer | 1-18 | Coffee sample identifier |
| `score` | float | 0-100 | Classification score |
| `accuracy` | float | 0-100 | Model accuracy percentage |
| `source` | string | - | Data source (e.g., "dht22", "mqtt") - auto-set to "mqtt" by backend |
| `device_id` | string | - | Device identifier (e.g., "ESP32-001") |
| `features` | array[8] | - | Sensor readings (8 channels) |
| `captured_at` | string (ISO8601) | - | Optional timestamp, auto-generated if not provided |

**Note:** Backend akan otomatis set `source = "mqtt"` untuk data yang datang dari MQTT.

---

## Testing MQTT Locally

### 1. Install MQTT Broker (Mosquitto)

**Windows:**
```powershell
# Download dari: https://mosquitto.org/download/
# Install dan jalankan service
net start mosquitto
```

**macOS:**
```bash
brew install mosquitto
brew services start mosquitto
```

**Linux:**
```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
```

### 2. Configure Backend

Edit `.env`:
```env
MQTT_ENABLED=true
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_TOPIC=enose/+/measurement
```

### 3. Run Backend

```bash
cargo run
```

Expected logs:
```
INFO MQTT: Initializing connection...
INFO MQTT: Connected and subscribed topic="enose/+/measurement" broker="localhost" port=1883
```

### 4. Publish Test Data

**Using mosquitto_pub:**
```bash
mosquitto_pub -h localhost -t "enose/ESP32-001/measurement" -m '{
  "sample_id": 1,
  "score": 28.5,
  "accuracy": 72.0,
  "source": "dht22",
  "device_id": "ESP32-001",
  "features": [285, 720, 0, 0, 0, 0, 0, 0]
}'
```

**Using MQTT.fx or MQTTX (GUI):**
- Connect to `localhost:1883`
- Publish to topic: `enose/ESP32-001/measurement`
- Payload: (JSON di atas)

### 5. Verify Backend Logs

```
INFO MQTT: Message received topic="enose/ESP32-001/measurement" payload_len=156
INFO MQTT: Measurement saved (201) measurement_id="550e8400-e29b-41d4-a716-446655440000" sample_id=1 device_id="ESP32-001"
```

### 6. Check Dashboard

Buka: `http://localhost:8080/dashboard`

Data MQTT akan muncul di dashboard bersama data HTTP.

---

## Public MQTT Brokers (For Testing)

Jika tidak ingin install broker lokal, gunakan public broker:

### HiveMQ Public Broker
```env
MQTT_BROKER=broker.hivemq.com
MQTT_PORT=1883
```

### Eclipse Mosquitto Test Server
```env
MQTT_BROKER=test.mosquitto.org
MQTT_PORT=1883
```

### EMQX Public Broker
```env
MQTT_BROKER=broker.emqx.io
MQTT_PORT=1883
```

**⚠️ Warning:** Public brokers tidak aman untuk production. Semua orang bisa subscribe ke topic kamu.

---

## Production MQTT Brokers

Untuk production, gunakan managed MQTT broker dengan authentication:

### CloudMQTT (HiveMQ Cloud)
```env
MQTT_BROKER=your-instance.s2.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=your-username
MQTT_PASSWORD=your-password
MQTT_TLS=true
```

### AWS IoT Core
```env
MQTT_BROKER=xxxxxx-ats.iot.us-east-1.amazonaws.com
MQTT_PORT=8883
MQTT_TLS=true
# Requires certificate-based auth (not username/password)
```

### Azure IoT Hub
```env
MQTT_BROKER=your-iot-hub.azure-devices.net
MQTT_PORT=8883
MQTT_USERNAME=your-device-id
MQTT_PASSWORD=your-sas-token
MQTT_TLS=true
```

---

## ESP32-S3 Firmware Example

Contoh kode ESP32-S3 untuk publish data ke backend:

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// MQTT Broker
const char* mqtt_broker = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "enose/ESP32-001/measurement";
const char* device_id = "ESP32-001";

// DHT22 Sensor
#define DHT_PIN 5
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  
  // Init DHT22
  dht.begin();
  
  // Connect WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  
  // Connect MQTT
  client.setServer(mqtt_broker, mqtt_port);
  reconnect();
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    if (client.connect(device_id)) {
      Serial.println("connected!");
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Read DHT22
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  if (isnan(temp) || isnan(hum)) {
    Serial.println("Failed to read DHT22!");
    return;
  }
  
  // Prepare JSON payload
  StaticJsonDocument<512> doc;
  doc["sample_id"] = 1;
  doc["score"] = temp;
  doc["accuracy"] = hum;
  doc["source"] = "dht22";
  doc["device_id"] = device_id;
  
  JsonArray features = doc.createNestedArray("features");
  features.add((int)(temp * 10));  // 28.5°C → 285
  features.add((int)(hum * 10));   // 72.0% → 720
  features.add(0); features.add(0);
  features.add(0); features.add(0);
  features.add(0); features.add(0);
  
  // Serialize to string
  String payload;
  serializeJson(doc, payload);
  
  // Publish to MQTT
  if (client.publish(mqtt_topic, payload.c_str())) {
    Serial.println("✅ Published: " + payload);
  } else {
    Serial.println("❌ Publish failed!");
  }
  
  delay(30000); // Send every 30 seconds
}
```

---

## Logging

Backend menggunakan `tracing` untuk structured logging.

### Log Levels

Set via `RUST_LOG` environment variable:

```env
# Info level (recommended for production)
RUST_LOG=info

# Debug level (verbose, for troubleshooting)
RUST_LOG=debug

# Specific module logging
RUST_LOG=enose_cloud=debug,sqlx=info
```

### MQTT Log Events

| Event | Log Level | Example |
|-------|-----------|---------|
| Connection init | INFO | `MQTT: Initializing connection...` |
| Connected | INFO | `MQTT: Connected and subscribed topic="..." broker="..." port=1883` |
| Message received | INFO | `MQTT: Message received topic="..." payload_len=156` |
| Measurement saved | INFO | `MQTT: Measurement saved (201) measurement_id="..." sample_id=1` |
| Invalid JSON | WARN | `MQTT: Invalid JSON payload error="..."` |
| Validation failed | WARN | `MQTT: Payload validation failed` |
| Database error | WARN | `MQTT: Database insert failed` |
| Connection error | ERROR | `MQTT: Connection error, reconnecting in 10s` |

---

## Reconnection Behavior

Backend MQTT subscriber memiliki **auto-reconnect** logic:

1. **Initial connection failure:** Retry every **10 seconds**
2. **Connection lost:** Reconnect immediately with **10 second** retry interval
3. **Infinite retry loop:** Backend akan terus mencoba reconnect sampai berhasil

### Reconnection Flow

```
┌─────────────────────────────────────┐
│ Start MQTT Worker                   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Connect to MQTT Broker              │
└────────────┬────────────────────────┘
             │
         Success? ────No───┐
             │             │
            Yes            ▼
             │      ┌─────────────────┐
             │      │ Wait 10 seconds │
             │      └─────────┬───────┘
             │                │
             ▼                │
┌─────────────────────────────│───────┐
│ Subscribe to Topic          │       │
└────────────┬────────────────│───────┘
             │                │
         Success? ────No───────┘
             │
            Yes
             │
             ▼
┌─────────────────────────────────────┐
│ Event Loop (Poll Messages)          │
└────────────┬────────────────────────┘
             │
      Connection Lost?
             │
            Yes
             │
             ▼
┌─────────────────────────────────────┐
│ Wait 10 seconds, then reconnect     │
└─────────────────────────────────────┘
             │
             └──────────────────►(Loop back to Connect)
```

---

## Troubleshooting

### Backend tidak connect ke MQTT broker

**Cek log:**
```
ERROR MQTT: Subscribe failed, retrying in 10s
```

**Solusi:**
1. Verify broker address: `ping broker.hivemq.com`
2. Check firewall: Port 1883 (TCP) must be open
3. Test broker dengan MQTT client: `mosquitto_sub -h broker.hivemq.com -t "#"`

---

### Data tidak muncul di dashboard

**Cek log:**
```
WARN MQTT: Payload validation failed
```

**Solusi:**
1. Verify JSON format (use jsonlint.com)
2. Check `sample_id` range (must be 1-18)
3. Check `score`/`accuracy` range (must be 0-100)
4. Verify `features` array has 8 elements

---

### ESP32 tidak bisa publish

**Cek Serial Monitor:**
```
❌ Publish failed!
```

**Solusi:**
1. Check WiFi connection: `WiFi.status() == WL_CONNECTED`
2. Check MQTT connection: `client.connected()`
3. Increase MQTT buffer size: `client.setBufferSize(512)`
4. Check topic name (case-sensitive)

---

### Railway deployment: MQTT tidak jalan

**Cek Railway logs:**
```bash
railway logs
```

**Solusi:**
1. Verify `MQTT_ENABLED=true` di Railway Variables
2. Check `MQTT_BROKER` accessible from Railway (public broker)
3. Railway tidak support outgoing port 1883 kadang, gunakan port 8883 (TLS)
4. Test dengan public broker dulu: `broker.hivemq.com:1883`

---

## Dashboard Integration

Data dari MQTT dan HTTP **menggunakan database yang sama** dan **tampil di dashboard yang sama**.

### Source Field

Dashboard bisa filter berdasarkan `source`:
- `"api"` - Data dari HTTP POST `/api/v1/measurements`
- `"mqtt"` - Data dari MQTT subscriber
- `"dht22"` - Data dari ESP32-S3 dengan DHT22 sensor

### Real-time Update

Dashboard auto-refresh setiap **30 detik**, jadi data MQTT akan muncul maksimal 30 detik setelah diterima backend.

---

## Security Best Practices

### ✅ Recommended for Production:

1. **Use private MQTT broker** (not public)
2. **Enable authentication** (`MQTT_USERNAME`, `MQTT_PASSWORD`)
3. **Enable TLS encryption** (`MQTT_TLS=true`, port 8883)
4. **Use topic ACL** (restrict who can publish/subscribe)
5. **Validate all payloads** (backend already does this)
6. **Use API key** for HTTP endpoint (future enhancement)

### ❌ Avoid:

1. Public brokers for production data
2. Unencrypted connections (TLS disabled)
3. Hardcoded credentials in ESP32 firmware
4. Overly broad topic wildcards (`#` subscribes to everything)

---

## Performance Considerations

- Backend dapat handle **hundreds of MQTT messages per second**
- PostgreSQL connection pool: 5 concurrent connections
- MQTT QoS 1 (At Least Once) - guaranteed delivery
- Auto-reconnect tidak block HTTP server
- Dashboard pagination: Max 500 measurements

---

## Future Enhancements

- [ ] TLS/SSL support untuk MQTT (secure connection)
- [ ] MQTT Last Will & Testament (LWT) untuk device status monitoring
- [ ] MQTT retain flag untuk latest measurement
- [ ] Bidirectional MQTT (backend publish commands to ESP32)
- [ ] MQTT message queue (buffer offline messages)
- [ ] Dashboard filter by source (api/mqtt/dht22)

---

## Support

Untuk pertanyaan atau issue:
- Backend GitHub: https://github.com/mahendrafhrz/enose-cloud-backend
- MQTT protocol: https://mqtt.org/
- rumqttc crate docs: https://docs.rs/rumqttc/

---

**Last Updated:** 2026-09-16  
**Status:** ✅ Production Ready (MQTT enabled)
