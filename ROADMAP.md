# E-NOSE CLOUD - NEXT STEPS ROADMAP

**Status Saat Ini:** ✅ Backend Rust + PostgreSQL + Dashboard sudah LIVE di Azure
**URL:** https://enose-cloud.grayfield-495d5d13.eastasia.azurecontainerapps.io

---

## 🎯 PHASE A: DEVICE INTEGRATION (Hardware → Cloud)

### 1. MQTT Connection Setup
**Status:** Konfigurasi sudah ada di backend, belum diaktifkan
**Yang perlu dilakukan:**
- [ ] Set environment variable `MQTT_ENABLED=true` di Azure Container App
- [ ] Buat MQTT broker (pilih salah satu):
  - Option 1: Azure IoT Hub (recommended for production)
  - Option 2: HiveMQ Cloud (gratis tier)
  - Option 3: Self-hosted Mosquitto
- [ ] Update `MQTT_BROKER`, `MQTT_USERNAME`, `MQTT_PASSWORD` di environment variables
- [ ] Test koneksi dari backend ke MQTT broker

**Cara test:**
```bash
az containerapp update --name enose-cloud --resource-group enose-cloud-rg \
  --set-env-vars \
  "MQTT_ENABLED=true" \
  "MQTT_BROKER=mqtt.broker.url:1883" \
  "MQTT_USERNAME=your_username" \
  "MQTT_PASSWORD=your_password"
```

---

### 2. ESP32 Firmware Development
**Yang perlu dilakukan:**
- [ ] Setup ESP32 dengan sensor array (8 sensor MQ series)
- [ ] Implementasi pembacaan sensor (ADC readings)
- [ ] Kirim data ke MQTT topic: `enose/measurements`
- [ ] Format data JSON:
```json
{
  "sample_id": 1,
  "device_id": "esp32-001",
  "features": [1500.2, 1800.5, 2200.3, 1100.1, 2900.4, 1600.7, 1550.9, 2100.2]
}
```

**Library yang dibutuhkan (ESP32):**
- PubSubClient (MQTT)
- ArduinoJson
- WiFi.h

---

### 3. Edge Impulse Integration
**Status:** Backend sudah siap terima features array
**Yang perlu dilakukan:**
- [ ] Train model di Edge Impulse dengan data dari `Raw Data Kopi Rafi`
- [ ] Deploy model ke ESP32 atau cloud inference
- [ ] Model output → `score` dan `accuracy`
- [ ] Kirim hasil inference ke backend via MQTT atau HTTP POST

**Endpoint untuk POST manual (testing):**
```
POST https://enose-cloud.grayfield-495d5d13.eastasia.azurecontainerapps.io/api/v1/measurements
Content-Type: application/json

{
  "sample_id": 1,
  "score": 91.5,
  "accuracy": 95.8,
  "source": "esp32",
  "device_id": "esp32-001",
  "features": [1500.2, 1800.5, ...]
}
```

---

### 4. OTA (Over-The-Air) Updates
**Yang perlu dilakukan:**
- [ ] Setup OTA server (bisa pakai Azure Blob Storage atau GitHub Releases)
- [ ] Implementasi OTA update di ESP32 firmware
- [ ] Version management untuk firmware
- [ ] Auto-update notification dari cloud ke device

**Library ESP32:**
- ESP32httpUpdate
- ArduinoOTA

---

## 🎯 PHASE B: CLOUD IMPROVEMENTS

### 5. Real-time Dashboard Updates
**Status:** Dashboard refresh manual (button)
**Yang perlu dilakukan:**
- [ ] Implementasi WebSocket di backend untuk real-time updates
- [ ] Dashboard auto-refresh saat ada data baru
- [ ] Live notification badge

**Backend changes needed:**
- Add WebSocket route di Axum
- Broadcast message saat data baru masuk

---

### 6. API Authentication & Security
**Status:** API terbuka tanpa auth
**Yang perlu dilakukan:**
- [ ] Implementasi JWT atau API Key authentication
- [ ] Rate limiting untuk API endpoints
- [ ] CORS configuration yang lebih ketat
- [ ] Device authentication untuk MQTT

---

### 7. Advanced Analytics
**Yang perlu dilakukan:**
- [ ] Grafik trend per sample (time-series)
- [ ] Anomaly detection
- [ ] Model drift monitoring
- [ ] Export data ke CSV/Excel

---

### 8. Multi-tenant Support
**Untuk skala lebih besar:**
- [ ] User management & login system
- [ ] Multiple devices per user
- [ ] Device grouping/organization

---

## 🎯 PHASE C: PRODUCTION READINESS

### 9. Monitoring & Logging
- [ ] Setup Azure Application Insights
- [ ] Error tracking & alerting
- [ ] Performance monitoring
- [ ] Database backup automation

### 10. CI/CD Pipeline
- [ ] GitHub Actions untuk auto-build Docker
- [ ] Auto-deploy ke Azure saat push ke main branch
- [ ] Automated testing

### 11. Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Device setup guide
- [ ] User manual untuk dashboard

---

## 📋 CURRENT BACKEND CAPABILITIES (Already Working)

✅ REST API untuk create/read/delete measurements
✅ PostgreSQL database dengan Azure
✅ Dashboard HTML dengan analytics
✅ PDF report generation
✅ MQTT worker (konfigurasi ada, tinggal enable)
✅ CORS enabled untuk cross-origin requests
✅ Health check endpoint
✅ Sample name mapping (18 coffee types)

---

## 🔧 QUICK START - Testing MQTT (Next Priority)

1. **Install MQTT broker lokal (testing):**
```bash
# Option 1: Mosquitto (Windows)
# Download dari https://mosquitto.org/download/

# Option 2: Docker
docker run -d -p 1883:1883 eclipse-mosquitto

# Option 3: Cloud - HiveMQ
# Sign up di https://www.hivemq.com/mqtt-cloud-broker/
```

2. **Enable MQTT di backend:**
```bash
az containerapp update --name enose-cloud --resource-group enose-cloud-rg \
  --set-env-vars "MQTT_ENABLED=true" \
  "MQTT_BROKER=your-broker-url:1883"
```

3. **Test dengan MQTT client:**
```bash
# Publish test message
mosquitto_pub -h your-broker -t enose/measurements -m '{"sample_id":1,"device_id":"test","features":[1,2,3,4,5,6,7,8]}'
```

---

## 📞 SUPPORT & RESOURCES

- Backend Code: `c:\Users\User\lancar\src\main.rs`
- Dashboard: `c:\Users\User\lancar\dashboard.html`
- Azure Container App: `enose-cloud` (resource group: `enose-cloud-rg`)
- Database: `enose-cloud-pg.postgres.database.azure.com`
- Training Data: `c:\Users\User\lancar\Raw Data Kopi Rafi\`

**PostgreSQL Credentials:**
- User: `enoseadmin`
- Password: `RafiGanteng123!`
- Database: `enose`

---

**Last Updated:** 2026-09-13
**Cloud Status:** ✅ LIVE & HEALTHY
