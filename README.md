# **PS4 State Monitor**

[![Ko-fi](https://img.shields.io/badge/Support%20Me-Ko--fi-FF5E5B?style=flat-square&logo=ko-fi&logoColor=white)](https://ko-fi.com/techmorph)

A minimal Flask microservice that exposes a REST API for monitoring your PS4's power state and 
waking it remotely via Wake-on-LAN (WoL).

It determines PS4 state using a two-stage heuristic:
- ICMP ping → detects if the NIC is reachable (Rest Mode or On)
- TCP port probe (9295, 987) → confirms if the PS4 is fully awake

Endpoints:
  GET  /health       — Liveness check
  GET  /state        — Returns current PS4 state: Offline | Rest | On
  POST /ps4/wake     — Sends WoL magic packet on configured port (default: 9)
  POST /ps4/wake_alt — Sends WoL magic packet on alternate port (7 or 9)

Fully configurable via environment variables (PS4_MAC, PS4_IP, BROADCAST, etc.).
Optional Bearer token auth for wake endpoints. Designed for self-hosted setups, 
Home Assistant REST integrations, or any local automation stack.

## ⚙️ Environment Variables

All configuration is done via the environment variables. No code changes needed.

| Variable | Default | Description |
|---|---|---|
| `PS4_MAC` | `AA:BB:CC:DD:EE:FF` | MAC address of your PS4's network interface |
| `PS4_IP` | `192.168.*.*` | Local IP address of your PS4 |
| `BROADCAST` | `192.168.1.255` | Broadcast address for your subnet |
| `SEND_INTERFACE` | `192.168.*.*` | IP of the host interface to send WoL packets from |
| `PS4_PORTS` | `9295,987` | Comma-separated TCP ports to probe for "fully awake" state |
| `TOKEN` | *(empty)* | Optional Bearer token to protect wake endpoints |

---

### Finding Your Values

**`PS4_MAC`** — The MAC address of your PS4.
- On your PS4: **Settings → System → System Information**
- Format it with colons: `A1:B2:C3:D4:E5:F6`

**`PS4_IP`** — Your PS4's local IP address.
- On your PS4: **Settings → Network → View Connection Status**
- Strongly recommended to set a **static/reserved IP** in your router's DHCP settings so this never changes.

**`BROADCAST`** — The broadcast address for your subnet.
- If your router is `192.168.1.1` and your subnet mask is `255.255.255.0`, your broadcast is `192.168.1.255`
- Replace the last octet with `255`. Example: `10.0.0.x` subnet → `10.0.0.255`

**`SEND_INTERFACE`** — The IP address of the **host machine** running this service (not the PS4).
- Run `ip addr` (Linux) or `ipconfig` (Windows) on your server and use the local IP of the network interface on the same subnet as your PS4.
- Example: if your server is `192.168.1.50`, set this to `192.168.1.50`

---

### Example `.env` / Docker Compose

```env
PS4_MAC=A1:B2:C3:D4:E5:F6
PS4_IP=192.168.1.100
BROADCAST=192.168.1.255
SEND_INTERFACE=192.168.1.50
PS4_PORTS=9295,987
TOKEN=your_secret_token_here
```

```yaml
services:
  ps4-monitor:
    image: ps4-monitor
    ports:
      - "9091:9091"
    environment:
      PS4_MAC: "A1:B2:C3:D4:E5:F6"
      PS4_IP: "192.168.1.100"
      BROADCAST: "192.168.1.255"
      SEND_INTERFACE: "192.168.1.50"
      PS4_PORTS: "9295,987"
      TOKEN: "your_secret_token_here"
```

> ⚠️ **Important:** `PS4_MAC`, `PS4_IP`, and `BROADCAST` must all be on the same subnet as 
> `SEND_INTERFACE`, otherwise Wake-on-LAN packets will not reach your PS4.

---

## 💛 Support

If this project helps your setup, consider supporting development:

[![Ko-fi](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Ko--fi-FF5E5B?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/techmorph)
