# Base44 Dev Environment

## What this project is

A Python **desktop GUI** application (Tkinter + matplotlib) that reads distance
data from a TF02-Pro LiDAR sensor over a serial port and displays real-time
graphs of distance, velocity, and acceleration. It is NOT a web app.

## How it runs in Base44

Since the preview is browser-based and there is no physical sensor in the
sandbox, the Docker setup (`Dockerfile.base44` + `docker-compose.base44.yml`)
provides:

- **Xvfb** — virtual framebuffer so Tkinter renders headlessly
- **x11vnc + noVNC/websockify** — serves the desktop in a browser on port 3000
- **socat** — creates a virtual serial port pair (`/dev/ttyUSB0` ↔ `/dev/ttyMock`)
- **`.base44/mock_sensor.py`** — generates fake TF02-Pro data packets (9-byte,
  header `\x59\x59`, checksum) so the app has live data without the real sensor

The startup script is `.base44/start.sh`.

## Key files (do not modify without asking)

| File | Role |
|---|---|
| `python_implement/window.py` | Main GUI (class `App`) — graphs, stopwatch, buttons |
| `python_implement/TF02_pro.py` | `MotorDados` — serial reader for the LiDAR sensor |
| `python_implement/StopWatch.py` | `StopWatch(Frame)` — Tkinter stopwatch widget |
| `python_implement/LidarSub.py` | Refactored version of the GUI (not the active entry point) |
| `python_implement/ZedSub.py` | ZED 2i camera reader (requires `pyzed.sl`, not installed) |

## Running

```bash
docker compose -f docker-compose.base44.yml up -d --build
```

The preview at port 3000 shows the noVNC page, which auto-connects to the VNC
desktop where the Tkinter app is running.

## Notes

- `C_implement/` is out of scope (per CLAUDE.md) — do not touch it.
- `ZedSub.py` requires the ZED SDK (`pyzed.sl`) which is not available in this
  environment; it is not part of the active app entry point.
- The app uses Python 3.12 f-string nested-quote syntax (PEP 701).
- No external secrets or credentials are needed.
