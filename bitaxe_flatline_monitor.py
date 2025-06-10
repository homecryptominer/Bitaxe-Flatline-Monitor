# Bitaxe Flatline Monitor
# Version 0.11

import time
import requests
import argparse
from datetime import datetime, timedelta
import sys
import math
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import re

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

# Helper function to format uptime
def format_uptime(uptime_seconds):
    try:
        uptime_td = timedelta(seconds=int(uptime_seconds))
        return str(uptime_td)
    except Exception:
        return "N/A"

# Helper function to strip ANSI codes
def strip_ansi_codes(s):
    return re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', s)

# Countdown timer function
def countdown_timer(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\rNext check in: {COLOR_COUNTDOWN}{remaining:2d} seconds{COLOR_RESET} ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 30 + "\r")

# BitaxeMonitor class to handle monitoring for each IP
class BitaxeMonitor:
    def __init__(self, ip, interval, file_logger, console_logger):
        self.ip = ip
        self.interval = interval
        self.file_logger = file_logger
        self.console_logger = console_logger
        self.prev_shares = None
        self.restart_count = 0
        self.stats_url = f"http://{ip}/api/system/info"
        self.restart_url = f"http://{ip}/api/system/restart"

    def update_status(self):
        self.timestamp = datetime.now().strftime("%d %b %Y %H:%M:%S")
        self.hostname = "N/A"
        self.uptime_str = "N/A"
        self.hashrate = "N/A"
        self.asic_temp = "N/A"
        self.vr_temp = "N/A"
        self.shares = 0
        try:
            response = requests.get(self.stats_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            self.hostname = data.get("hostname", "N/A")
            hashrate = data.get("hashRate", "N/A")
            if isinstance(hashrate, (int, float)):
                self.hashrate = math.ceil(hashrate * 10) / 10
            else:
                self.hashrate = "N/A"
            asic_temp = data.get("temp", "N/A")
            try:
                self.asic_temp = round(float(asic_temp), 1)
            except (ValueError, TypeError):
                self.asic_temp = "N/A"
            self.vr_temp = data.get("vrTemp", "N/A")
            self.shares = data.get("sharesAccepted", 0)
            uptime_seconds = data.get("uptimeSeconds", None)
            self.uptime_str = format_uptime(uptime_seconds)
            # Check for stagnant shares
            if self.prev_shares is not None and self.shares == self.prev_shares:
                try:
                    restart_resp = requests.post(self.restart_url, timeout=5)
                    if restart_resp.status_code == 200:
                        self.restart_count += 1
                        console_restart_message = f"⚠️ No new shares detected for {COLOR_ASIC_TEMP}{self.hostname}{COLOR_RESET} ({self.ip}). Restarting... ✅ Restart command sent successfully."
                        file_restart_message = f"⚠️ No new shares detected for {self.hostname} ({self.ip}). Restarting... ✅ Restart command sent successfully."
                    else:
                        console_restart_message = f"⚠️ Failed to restart {COLOR_ASIC_TEMP}{self.hostname}{COLOR_RESET} ({self.ip}): {restart_resp.status_code}"
                        file_restart_message = f"⚠️ Failed to restart {self.hostname} ({self.ip}): {restart_resp.status_code}"
                    self.console_logger.info(console_restart_message)
                    self.file_logger.info(file_restart_message)
                except requests.RequestException as e:
                    console_restart_message = f"🚫 Error sending restart command to {COLOR_ASIC_TEMP}{self.hostname}{COLOR_RESET} ({self.ip}): {e}"
                    file_restart_message = f"🚫 Error sending restart command to {self.hostname} ({self.ip}): {e}"
                    self.console_logger.info(console_restart_message)
                    self.file_logger.info(file_restart_message)
            self.prev_shares = self.shares
        except requests.RequestException as e:
            error_message = f"🚫 Error communicating with Bitaxe at {self.ip}: {e}"
            self.console_logger.error(error_message)
            self.file_logger.error(error_message)

    def print_status(self, max_len):
        padded_hostname = self.hostname.ljust(max_len)
        colored_padded_hostname = f"{COLOR_HOSTNAME}{padded_hostname}{COLOR_RESET}"
        # Format ASIC temperature to always show one decimal point
        asic_temp_str = f"{self.asic_temp:.1f}" if isinstance(self.asic_temp, (int, float)) else self.asic_temp
        console_message = (f"{COLOR_TIMESTAMP}[{self.timestamp}]{COLOR_RESET} "
                           f"{colored_padded_hostname}: "
                           f"🕓️ Uptime: {COLOR_UPTIME}{self.uptime_str}{COLOR_RESET} | "
                           f"⚡️ Hash: {COLOR_HASHRATE}{self.hashrate} GH/s{COLOR_RESET} | "
                           f"🌡️ ASIC: {COLOR_ASIC_TEMP}{asic_temp_str}°C{COLOR_RESET} / "
                           f"VR: {COLOR_VR_TEMP}{self.vr_temp}°C{COLOR_RESET} | "
                           f"✅ Shares: {COLOR_SHARES}{self.shares}{COLOR_RESET} | "
                           f"↩️ Restarts: {COLOR_RESTARTS}{self.restart_count}{COLOR_RESET}")
        self.console_logger.info(console_message)
        file_message = (f"[{self.timestamp}] {self.hostname}: "
                        f"🕓️ Uptime: {self.uptime_str} | "
                        f"⚡️ Hash: {self.hashrate} GH/s | "
                        f"🌡️ ASIC: {asic_temp_str}°C / VR: {self.vr_temp}°C | "
                        f"✅ Shares: {self.shares} | "
                        f"↩️ Restarts: {self.restart_count}")
        self.file_logger.info(file_message)

# Main script
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Monitor Bitaxe(s) and restart on stagnant shares.")
    parser.add_argument("ip", nargs="?", help="IP address of the Bitaxe device. If not provided, read from bitaxes.conf")
    parser.add_argument("-interval", "-i", type=int, default=60, help="Time interval between checks in seconds (default: 60)")
    args = parser.parse_args()

    # Determine IPs and retain_log_days
    if args.ip:
        ips = [args.ip]
        retain_log_days = 7
    else:
        try:
            with open("bitaxes.conf", "r") as f:
                lines = f.readlines()
            ips = []
            settings = {}
            for line in lines:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    settings[key.strip()] = value.strip()
                else:
                    ips.append(line)
            retain_log_days = int(settings.get("retain-log-days", 7))
        except FileNotFoundError:
            print("Configuration file bitaxes.conf not found.")
            sys.exit(1)
        except ValueError:
            print("Invalid value for retain-log-days in configuration file.")
            sys.exit(1)

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Set up console logger
    console_logger = logging.getLogger("console")
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)
    console_logger.setLevel(logging.INFO)
    console_logger.propagate = False

    # Create monitors for each IP
    monitors = []
    for ip in ips:
        file_logger = logging.getLogger(f"file_{ip}")
        file_handler = TimedRotatingFileHandler(f"logs/{ip}.log", when="midnight", backupCount=retain_log_days, encoding='utf-8')
        file_formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(file_formatter)
        file_logger.addHandler(file_handler)
        file_logger.setLevel(logging.INFO)
        file_logger.propagate = False
        monitor = BitaxeMonitor(ip, args.interval, file_logger, console_logger)
        monitors.append(monitor)

    # Log startup message
    startup_message = f"Monitoring Bitaxes: {', '.join(ips)} with interval {args.interval} seconds"
    console_logger.info(startup_message)

    # Main monitoring loop
    while True:
        # Update all monitors
        for monitor in monitors:
            monitor.update_status()
        # Collect all hostnames
        all_hostnames = [m.hostname for m in monitors]
        if all_hostnames:
            max_len = max(len(h) for h in all_hostnames)
        else:
            max_len = 0
        # Print all with padding
        for monitor in monitors:
            monitor.print_status(max_len)
        if len(monitors) > 1:
            print("---------------------------------------------------------------------------------------------------------------------------------------------------")
        countdown_timer(args.interval)