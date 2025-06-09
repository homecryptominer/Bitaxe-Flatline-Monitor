# Bitaxe Flatline Monitor
# Version 0.05: This release includes the hostname for those people who have multiple Bitaxes running. Also shortened labels for easier reading.

import time
import requests
import argparse
from datetime import datetime, timedelta
import sys
import math

# Define ANSI color codes
COLOR_TIMESTAMP = "\033[92m"  # Green
COLOR_HOSTNAME = "\033[96m"  # Cyan
COLOR_UPTIME = "\033[38;5;36m"  # Navy green
COLOR_HASHRATE = "\033[94m"   # Blue
COLOR_ASIC_TEMP = "\033[91m"  # Red
COLOR_VR_TEMP = "\033[95m"    # Magenta
COLOR_SHARES = "\033[93m"     # Yellow
COLOR_RESTARTS = "\033[96m"   # Cyan
COLOR_COUNTDOWN = "\033[96m"  # Cyan
COLOR_RESET = "\033[0m"

def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rNext check in: {COLOR_COUNTDOWN}{remaining:2d} seconds{COLOR_RESET} ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 30 + "\r")

def format_uptime(uptime_seconds):
    try:
        uptime_td = timedelta(seconds=int(uptime_seconds))
        return str(uptime_td)
    except Exception:
        return "N/A"

def monitor_bitaxe(ip: str, interval: int = 60):
    prev_shares = None
    restart_count = 0
    stats_url = f"http://{ip}/api/system/info"
    restart_url = f"http://{ip}/api/system/restart"

    while True:
        wait_after_restart = False
        try:
            response = requests.get(stats_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Get Hostname
            hostname = data.get("hostname", "N/A")

            # Convert hashrate to GH/s
            hashrate = data.get("hashRate", "N/A")
            if isinstance(hashrate, (int, float)):
                hashrate = math.ceil(hashrate * 10) / 10  # round up to nearest 0.1
            else:
                hashrate = "N/A"

            asic_temp = data.get("temp", "N/A")
            if isinstance(asic_temp, (int, float)):
                asic_temp = round(asic_temp, 1)

            vr_temp = data.get("vrTemp", "N/A")
            shares = data.get("sharesAccepted", 0)

            # New: Get uptime and format it
            uptime_seconds = data.get("uptimeSeconds", None)
            uptime_str = format_uptime(uptime_seconds)

            now = datetime.now().strftime("%d %b %Y %H:%M:%S")
            print(f"{COLOR_TIMESTAMP}[{now}]{COLOR_RESET} "
                  f"{COLOR_HOSTNAME}{hostname}{COLOR_RESET}:"
                  f"⏱  Uptime: {COLOR_UPTIME}{uptime_str}{COLOR_RESET} | "
                  f"💪 Hash: {COLOR_HASHRATE}{hashrate} GH/s{COLOR_RESET} | "
                  f"🔥 ASIC: {COLOR_ASIC_TEMP}{asic_temp}°C{COLOR_RESET} / "
                  f"VR: {COLOR_VR_TEMP}{vr_temp}°C{COLOR_RESET} | "
                  f"✅ Shares: {COLOR_SHARES}{shares}{COLOR_RESET} | "
                  f"Restarts: {COLOR_RESTARTS}{restart_count}{COLOR_RESET}")

            if prev_shares is not None and shares == prev_shares:
                print("⚠️ No new shares detected. Restarting Bitaxe...")
                try:
                    restart_resp = requests.post(restart_url, timeout=5)
                    if restart_resp.status_code == 200:
                        restart_count += 1
                        print("✅ Restart command sent successfully.")
                        wait_after_restart = True  # Flag to wait after restart
                    else:
                        print(f"⚠️ Failed to restart Bitaxe: {restart_resp.status_code}")
                except requests.RequestException as e:
                    print(f"🚫 Error sending restart command: {e}")

            prev_shares = shares

        except requests.RequestException as e:
            print(f"🚫 Error communicating with Bitaxe at {ip}: {e}")

        # Wait for 60 seconds after a restart, or interval otherwise
        if wait_after_restart:
            countdown_timer(60)
        else:
            countdown_timer(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor Bitaxe and restart on stagnant shares.")
    parser.add_argument("ip", help="IP address of the Bitaxe device (e.g. 192.168.2.88)")
    parser.add_argument("-interval", "-i", type=int, default=60, help="Time interval between checks in seconds (default: 60)")
    args = parser.parse_args()

    monitor_bitaxe(args.ip, args.interval)