"""Mock TF02-Pro LiDAR sensor — generates valid 9-byte data packets
and writes them to a virtual serial port created by socat.

This is ONLY for running the app in environments without the physical
sensor. The real sensor is used during normal development.
"""
import struct
import math
import time
import sys
import serial


def build_packet(distance_cm, strength=200, temp_c=25):
    """Build a valid 9-byte TF02-Pro data packet."""
    header = b"\x59\x59"
    dist_bytes = struct.pack("<H", max(0, min(0xFFFF, int(distance_cm))))
    strength_bytes = struct.pack("<H", max(0, min(0xFFFF, strength)))
    temp_raw = int((temp_c + 256) * 8)
    temp_bytes = struct.pack("<H", max(0, min(0xFFFF, temp_raw)))
    payload = header + dist_bytes + strength_bytes + temp_bytes
    checksum = sum(payload) & 0xFF
    return payload + bytes([checksum])


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyMock"
    ser = serial.Serial(port, 115200, timeout=0.1)
    print(f"Mock sensor writing to {port}")

    t = 0.0
    while True:
        # Simulate an object oscillating between ~50 and ~450 cm
        distance = 250 + 200 * math.sin(t * 0.5)
        packet = build_packet(distance)
        ser.write(packet)
        t += 0.1
        time.sleep(0.1)


if __name__ == "__main__":
    main()
