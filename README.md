# Bitaxe Flatline Monitor

## Introduction

Some Bitaxes when overclocked will experience what is called the Flatline of Death. This appears that the Bitaxe is still running in AxeOS, but the hashrate remains fixed and no new shares are submitted. On AxeOS, this looks like a flatline. Bitaxes can flatline after just a few minutes, hours or even days and is very frustrating to think it's hashing away submitting shares - when it is not. Essentially your Bitaxe has crashed and needs to be restarted. 

The Bitaxe Flatline Monitor is a Python script designed to monitor [Bitaxe open-source ASIC Bitcoin miners](https://bitaxe.org/). It periodically checks the status of one or more Bitaxe devices, logging metrics such as uptime, hashrate, ASIC temperature, VR temperature, shares, and restart count. If a device stops producing new shares (indicating a "flatline"), the script automatically sends a restart command to restore functionality. The script supports both single and multiple device monitoring, with features like daily log rotation, configurable log retention, and a color-coded console output for easy reading.

## Installation

1. **Install Python**: Ensure Python 3.x is installed on your system. You can download it from [Python Downloads](https://www.python.org/downloads/) if needed.

2. **Install Dependencies**: The script requires the `requests` library for making API calls to Bitaxe devices. Install it using pip:
   ```bash
   pip install requests
   ```

3. **Clone the Repository**: If the script is hosted on GitHub, clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-username/bitaxe-flatline-monitor.git
   cd bitaxe-flatline-monitor
   ```

## Usage

### Single Bitaxe Mode

To monitor a single Bitaxe device, run the script with the device’s IP address as a command-line argument:

```bash
python bitaxe_flatline_monitor.py <IP_ADDRESS> [-i <INTERVAL>]
```

- `<IP_ADDRESS>`: The IP address of the Bitaxe device (e.g., `192.168.2.88`).
- `-i <INTERVAL>`: Optional. The time interval between status checks in seconds (default: 60).

**Example**:
```bash
python bitaxe_flatline_monitor.py 192.168.2.88 -i 60
```

This command monitors the device at `192.168.2.88`, checking its status every 60 seconds. Status updates are displayed in the console with color-coded metrics and logged to `logs/192.168.2.88.log`.

### Multiple Bitaxe Mode

To monitor multiple Bitaxe devices, create a configuration file named `bitaxes.conf` in the same directory as the script. List each device’s IP address on a new line, and optionally include settings like log retention duration. Then, run the script without an IP address argument:

```bash
python bitaxe_flatline_monitor.py
```

**Sample `bitaxes.conf`**:
```
# Settings
retain-log-days=7

# Bitaxe IPs
192.168.2.88
192.168.2.89
192.168.2.77

```

This monitors all devices listed in `bitaxes.conf`, with status updates for each device displayed in the console and logged to individual files in the `logs/` directory (e.g., `logs/192.168.2.88.log`, `logs/192.168.2.89.log`, `logs/192.168.2.77.log`). 

## Configuration (only used for monitoring multiple Bitaxes)

The `bitaxes.conf` file is used in multiple Bitaxe mode to specify device IP addresses and settings. The file format is as follows:
- **IP Addresses**: List each Bitaxe device’s IP address on a new line (e.g., `192.168.2.88`).
- **Settings**: Use the format `key=value`. Currently supported:
  - `retain-log-days`: Specifies the number of days to retain log files (default: 7).
- **Comments**: Lines starting with `#` are ignored.

**Example `bitaxes.conf`**:
```
# Settings
retain-log-days=7

# Bitaxe IPs
192.168.2.88
192.168.2.89
192.168.2.77
```

- The `bitaxes.conf` file must be in the same directory as the script.
- If `retain-log-days` is not specified, it defaults to 7 days.
- Log files are stored in a `logs/` directory, created automatically if it doesn’t exist, and are rotated daily.

## Features

- **Single and Multiple Device Support**: Monitor one Bitaxe device via command-line IP or multiple devices via `bitaxes.conf`.
- **Comprehensive Metrics**: Tracks and displays uptime, hashrate, ASIC temperature, VR temperature, shares, and restart count.
- **Automatic Restart**: Sends a restart command to a device if no new shares are detected, ensuring continuous mining.
- **Logging**:
  - Each device has a dedicated log file in the `logs/` directory.
  - Logs are rotated daily and retained for the number of days specified in `retain-log-days`.
  - Logs use UTF-8 encoding to support emojis.

## Requirements

- **Bitaxe Devices**: The script is designed for [Bitaxe open-source ASIC Bitcoin miners](https://bitaxe.org/). Devices must be powered on, connected to the same network, and have their APIs accessible.
- **Network Access**: Ensure the Bitaxe devices are reachable via their IP addresses over Wi-Fi, as Bitaxe devices typically lack Ethernet ports.
- **Python 3.x**: Required to run the script.
- **Dependencies**: The `requests` library must be installed via pip.

## Example Output

**Single Bitaxe Mode**:
```
[09 Jun 2025 21:24:11] Bitaxe1:🕓️ Uptime: 1:17:11 | ⚡️ Hash: 992.0 GH/s | 🌡️ ASIC: 60.0°C / VR: 43°C | ✅ Shares: 540 | ↩️ Restarts: 0
Next check in: 60 seconds
```

**Multiple Bitaxe Mode**:
```
[09 Jun 2025 21:24:11] Bitaxe1        :🕓️ Uptime: 1:17:11 | ⚡️ Hash: 992.0 GH/s | 🌡️ ASIC: 60.0°C / VR: 43°C | ✅ Shares: 540 | ↩️ Restarts: 0
[09 Jun 2025 21:24:11] Bitaxe-thunder :🕓️ Uptime: 2:05:30 | ⚡️ Hash: 980.0 GH/s | 🌡️ ASIC: 45.5°C / VR: 44°C | ✅ Shares: 520彼此

## License

This script is provided under the [MIT License](https://opensource.org/licenses/MIT). See the LICENSE file in the repository for details.