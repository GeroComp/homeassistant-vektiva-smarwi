# Vektiva Smarwi – Home Assistant Integration

This custom integration allows you to control the [**Vektiva Smarwi smart window opener**](https://vektiva.com/index.php) directly from [Home Assistant](https://www.home-assistant.io/).


The project was originally created by [cvrky](https://github.com/cvrky/vektiva_smarwi_ha) and has now been taken over and updated to work with current versions of Home Assistant.

---

## ✨ Features
- Control Smarwi devices (open / close / stop).
- Display current state (open, closed, moving).
- Support for multiple devices.
- Easy installation via **HACS**.

---

## 📦 Installation

### 1. Via HACS (recommended)
1. Open HACS in Home Assistant.
2. Go to **Integrations → Custom repositories**.
3. Add this repository:
[(https://github.com/GeroComp/homeassistant-vektiva-smarwi.git)](https://github.com/GeroComp/homeassistant-vektiva-smarwi.git)
as type **Integration**.
4. Install the integration and restart Home Assistant.

### 2. Manual installation
1. Download the repository contents.
2. Copy the folder `custom_components/vektiva_smarwi` into:
   config/custom_components/vektiva_smarwi
3. Restart Home Assistant.

---

## ⚙️ Configuration

Add the following to your `configuration.yaml`:

```yaml
cover:
- platform: vektiva_smarwi
 host: 192.168.x.x   # IP address of the Smarwi device.
 name: optional entity name.

🛠️ Known Issues
If the device does not respond, check the IP address.

The integration requires Smarwi to be accessible on your local network.

🤝 Credits
Original author: cvrky

Maintenance & fixes: GeroComp

📜 License
MIT License – see the LICENSE file.

---

👉 To make it even more appealing, I’d suggest adding:
- A **screenshot** of the Smarwi entity in Home Assistant UI.
- A short **demo GIF** showing open/close actions.

Would you like me to also prepare a **short badge section** (e.g., HACS badge, GitHub release badge) so your README looks more professional and recognizable to the HA community?
