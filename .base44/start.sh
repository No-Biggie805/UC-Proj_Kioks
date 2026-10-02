#!/bin/bash
set -e

# --- Virtual framebuffer (headless display for Tkinter) ---
Xvfb :0 -screen 0 1024x768x24 &
sleep 1
export DISPLAY=:0

# --- Virtual serial port pair (mock sensor <-> app) ---
# socat creates two linked PTYs; the app reads /dev/ttyUSB0,
# the mock sensor writes to /dev/ttyMock.
socat -d -d pty,raw,echo=0,link=/dev/ttyUSB0 pty,raw,echo=0,link=/dev/ttyMock &
sleep 1

# --- Mock sensor (fake TF02-Pro data) ---
python /mock_sensor.py /dev/ttyMock &

# --- VNC server ---
x11vnc -display :0 -forever -shared -rfbport 5900 -nopw -bg
sleep 1

# --- noVNC web client (served on port 6080) ---
# Create an auto-connect index page
cat > /usr/share/novnc/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&reconnect=true">
</head>
<body>Redirecting to noVNC…</body>
</html>
HTMLEOF

websockify --web /usr/share/novnc 6080 localhost:5900 &

# --- Launch the Tkinter application ---
cd /app/python_implement
exec python window.py
