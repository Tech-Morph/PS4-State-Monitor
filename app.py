from flask import Flask, jsonify, request
from wakeonlan import send_magic_packet
import os
import subprocess
import time
import socket

APP = Flask(__name__)

PS4_MAC = os.environ.get("PS4_MAC", "A1:B2:C3:D4:E5:F6)
PS4_IP = os.environ.get("PS4_IP", "192.168.*.*")
BCAST = os.environ.get("BROADCAST", "192.168.1.255")
SEND_INTERFACE = os.environ.get("SEND_INTERFACE", "192.168.*.*")

# Comma-separated ports to probe for "fully awake" (adjust if you know better)
PORTS = os.environ.get("PS4_PORTS", "9295,987").strip()
PROBE_PORTS = [int(p) for p in PORTS.split(",") if p.strip().isdigit()]

TOKEN = os.environ.get("TOKEN", "")

def ping(host: str, timeout_s: int = 1) -> bool:
    r = subprocess.run(
        ["ping", "-c", "1", "-W", str(timeout_s), host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return r.returncode == 0

def tcp_probe(host: str, port: int, timeout_s: float = 0.4) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout_s):
            return True
    except OSError:
        return False

def require_token_if_set():
    if not TOKEN:
        return None
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {TOKEN}":
        return ("Unauthorized", 401)
    return None

@APP.get("/health")
def health():
    return jsonify(ok=True)

@APP.get("/state")
def state():
    reachable = ping(PS4_IP, timeout_s=1)
    awake_tcp = False
    if reachable and PROBE_PORTS:
        awake_tcp = any(tcp_probe(PS4_IP, p) for p in PROBE_PORTS)

    # State interpretation:
    # - reachable=False => Off-ish / deep rest / unreachable
    # - reachable=True & awake_tcp=False => Rest Mode / NIC only
    # - awake_tcp=True => Fully on (best-effort heuristic)
    if not reachable:
        state = "Offline"
    elif awake_tcp:
        state = "On"
    else:
        state = "Rest"

    return jsonify(
        ps4_ip=PS4_IP,
        reachable=reachable,
        awake_tcp=awake_tcp,
        probed_ports=PROBE_PORTS,
        state=state,
        ts=int(time.time()),
    )

@APP.post("/ps4/wake")
def wake():
    denied = require_token_if_set()
    if denied:
        return denied

    for _ in range(WOL_COUNT):
        send_magic_packet(
            PS4_MAC,
            ip_address=BCAST,
            port=WOL_PORT,
            interface=SEND_INTERFACE,
        )
        time.sleep(WOL_INTERVAL_MS / 1000.0)

    return jsonify(
        sent=True,
        mac=PS4_MAC,
        broadcast=BCAST,
        port=WOL_PORT,
        count=WOL_COUNT,
        interface=SEND_INTERFACE,
    )

@APP.post("/ps4/wake_alt")
def wake_alt():
    denied = require_token_if_set()
    if denied:
        return denied

    alt_port = 7 if WOL_PORT == 9 else 9
    for _ in range(WOL_COUNT):
        send_magic_packet(
            PS4_MAC,
            ip_address=BCAST,
            port=alt_port,
            interface=SEND_INTERFACE,
        )
        time.sleep(WOL_INTERVAL_MS / 1000.0)

    return jsonify(
        sent=True,
        mac=PS4_MAC,
        broadcast=BCAST,
        port=alt_port,
        count=WOL_COUNT,
        interface=SEND_INTERFACE,
    )

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=9091)
