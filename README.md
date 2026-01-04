<div align="center">

  <img src="https://brands.home-assistant.io/_/vektiva_smarwi/logo.png" alt="Vektiva Smarwi Logo" width="300">

  # Vektiva Smarwi – Home Assistant Integration

  [![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
  [![version](https://img.shields.io/github/v/release/GeroComp/homeassistant-vektiva-smarwi?style=for-the-badge)](https://github.com/GeroComp/homeassistant-vektiva-smarwi/releases)
  [![License](https://img.shields.io/github/license/GeroComp/homeassistant-vektiva-smarwi?style=for-the-badge)](LICENSE)

</div>

---

This custom integration allows you to control the [**Vektiva Smarwi smart window opener**](https://vektiva.com/index.php) directly from [Home Assistant](https://www.home-assistant.io/).

It provides full local control over your windows via your Wi-Fi network, ensuring fast response times and privacy without relying on external clouds.

---

## ✨ Features
* **🔌 Plug & Play:** Automatically discovers Smarwi devices on your network (DHCP & mDNS support).
* **🪟 Full Control:** Open, Close, Stop, and set specific position (0-100%).
* **🎨 Dynamic Icons:** Icons change automatically based on window state (Open/Closed/Tilt).
* **⚡ Local API:** Works strictly over your local network (no cloud required).
* **📊 Live Feedback:** Real-time updates of position and status.

---

## 📦 Installation

### Option 1: Via HACS (Recommended)
The easiest way to install and keep the integration updated.

1.  Open **HACS** in Home Assistant.
2.  Click the **3 dots menu** (top right corner) → Select **Custom repositories**.
3.  Paste the following URL into the Repository field:
    ```text
    https://github.com/GeroComp/homeassistant-vektiva-smarwi
    ```
4.  Select category: **Integration**.
5.  Click **Add**, then find "Vektiva Smarwi" in the list and click **Download**.
6.  **Restart Home Assistant**.

### Option 2: Manual Installation
1.  Download the latest release from this repository.
2.  Copy the folder `custom_components/vektiva_smarwi` into your Home Assistant config folder:
    `config/custom_components/vektiva_smarwi`
3.  **Restart Home Assistant**.

---

## ⚙️ Configuration

### Method A: Auto-Discovery (Easiest)
Once installed and restarted, Home Assistant should automatically find your device.

1.  Go to **Settings** → **Devices & Services**.
2.  Look for the **"Discovered"** section.
3.  Click **Configure** on the Vektiva Smarwi notification.
4.  Confirm the setup. Done!

> **💡 IMPORTANT:** If the discovery notification does not appear immediately, **restart your Smarwi device** (unplug it from the power socket for 5 seconds and plug it back in). This forces the device to announce itself on the network, allowing Home Assistant to find it.

### Method B: Manual Add via UI
If the device is not discovered automatically (e.g., due to network setup):

1.  Go to **Settings** → **Devices & Services**.
2.  Click **+ ADD INTEGRATION** (bottom right).
3.  Search for **Vektiva Smarwi**.
4.  Enter the **IP address** of your device.

> **⚠️ Tip:** It is highly recommended to set a **Static IP address** for your Smarwi device in your router settings. If the IP address changes (via DHCP), Home Assistant might lose connection to the device.

---

## 🛠️ Troubleshooting

### Auto-discovery not working?
If Home Assistant doesn't find your device automatically:
1.  **Restart Smarwi (Crucial Step):** Unplug the device from power and plug it back in. This is often required to trigger the discovery packet.
2.  **Network:** Ensure your Home Assistant is on the **same network subnet** as the Smarwi device.
3.  **Docker:** If running in Docker, you must use `network_mode: host` for discovery to work.
4.  **Manual:** You can always add the device manually using its IP address (Method B).

### Device is unavailable?
* **Check Connection:** Ensure the Smarwi is connected to Wi-Fi and has power.
* **Verify IP:** Check if the IP address has changed in your router.
* **Test Access:** Open the device’s IP address in a web browser. If the Smarwi web interface loads, the device is working correctly.

---

## ❤️ Credits & Acknowledgements

This project exists thanks to the hard work of the original creators and the manufacturer.

* **Original Creator:** Huge thanks to **[cvrky](https://github.com/cvrky)** for the initial development of this Home Assistant integration.
* **Manufacturer:** Special thanks to **[Vektiva](https://vektiva.com/)** for designing the **Smarwi** hardware and providing an open API.
* **Maintenance:** Currently updated and maintained by **[GeroComp](https://github.com/GeroComp)**.

## 📜 License

MIT License – see the [LICENSE](LICENSE) file for details.
