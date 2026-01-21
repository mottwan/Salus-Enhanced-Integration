# Salus Enhanced – Home Assistant Integration

An enhanced Home Assistant integration that supports **IT600 and IT500** gateways, multiple Salus device models, and extended entities.

> ⚠️ **Important (v1.0.1):**
> The `config_flow` is currently **not working** in version **1.0.1**.
> This means the integration **cannot be added from the UI** yet.
> Please use **YAML configuration** as described below.

---

## 🚀 Features

- **IT600 & IT500 support**: Local control (IT600) and cloud control (IT500)
- **Extended device support**: Thermostats, sensors, switches, covers, and binary sensors
- **Multiple Salus models supported**:
  - **IT600**: HTRP-RF, TS600, VS10/VS20, SQ610, FC600, and many more
  - **IT500**: IT500, RT310i, RT310, RT510, RT520, XT500
- **Rich entities**: Temperature, humidity, battery level, heating state, valve position
- **Coordinated updates**: Uses `DataUpdateCoordinator` for efficiency
- **Modular & extensible**: Clean code structure for easy addition of new devices

---

## 📦 Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click **"..."** (top-right) → **Custom repositories**
4. Add this repository URL and select **Integration**
5. Click **Install**
6. Restart Home Assistant

### Manual Installation

1. Copy the folder:
   ```
   custom_components/salus_enhanced
   ```
   to:
   ```
   /config/custom_components/
   ```
2. Restart Home Assistant

---

## ⚙️ Configuration (YAML – Required for v1.0.1)

Since `config_flow` is not functional in **v1.0.1**, the integration must be configured via `configuration.yaml`.

### IT600 (Local Gateway – UGE600)

```yaml
salus_enhanced:
  platform: it600
  host: 192.168.1.100
  euid: "001E5E0D32906128"
```

**Notes:**
- `host` = local IP address of the IT600 gateway
- `euid` = EUID printed on the gateway
- If the real EUID does not work, try:
  ```yaml
  euid: "0000000000000000"
  ```
- Make sure **Local WiFi Mode** is enabled in the Salus app
- Home Assistant and the gateway must be on the same network

---

### IT500 (Cloud – salus-it500.com)

```yaml
salus_enhanced:
  platform: it500
  email: your@email.com
  password: your_password
  device_id: 34508332
```

#### How to find the IT500 Device ID

1. Open https://salus-it500.com in a browser
2. Log in with the same credentials as the mobile app
3. Select your device
4. In the URL you will see:
   ```
   https://salus-it500.com/public/control.php?devId=34508332
   ```
5. Copy the number after `devId=`

---

## 🔧 Supported Devices

### IT600 – Thermostats (Climate)
- HTRP-RF / HTRP-RF50
- TS600
- VS10WRF / VS10BRF
- VS20WRF / VS20BRF
- SQ610 / SQ610RF
- FC600

### IT600 – Binary Sensors
- SW600 (Window sensor)
- WLS600 (Water leak sensor)
- OS600 (Occupancy sensor)
- SD600 (Smoke detector)
- MS600 (Motion sensor)
- TRV10RFM (Thermostatic valve)
- RX10RF (Receiver)

### IT600 – Sensors
- PS600 (Temperature sensor)
- Battery level (all compatible devices)
- Humidity (from supported thermostats)

### IT600 – Switches
- SPE600
- RS600
- SR600
- SP600

### IT600 – Covers
- RS600 (Roller shutter controller)

### IT500 – Thermostats
- IT500
- RT310i
- RT310
- RT510
- RT520
- XT500

---

## 🛠️ Advanced Configuration

### Update Interval

You can change the update interval in `const.py`:

```python
SCAN_INTERVAL = 30  # seconds
```

---

## 🐛 Troubleshooting

### Integration cannot be added from UI
This is expected behavior in **v1.0.1**.
Please use **YAML configuration** until `config_flow` support is fixed.

### Devices not appearing
- Check Home Assistant logs
- Ensure devices are configured in the Salus app
- Restart Home Assistant after changing YAML

---

## 📝 Logging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.salus_enhanced: debug
    pyit600: debug
    pyit500: debug
```

---

## 📄 License

MIT License – see the LICENSE file for details

---

## 🙏 Credits

Based on:
- https://github.com/epoplavskis/homeassistant_salus (IT600)
- https://github.com/epoplavskis/pyit600
- https://github.com/RichyA/home-assistant-salus-it500 (IT500)
- https://github.com/RichyA/pyit500
