# Bitaxe-Flatline-Monitor
Some Bitaxes when overclocked will experience what is called the Flatline of Death. This appears that the Bitaxe is still running in AxeOS, but the hashrate remains fixed and no new shares are submitted. On AxeOS, this looks like a flatline. Bitaxes can flatline after just a few minutes, hours or even days and is very frustrating to think it's hashing away submitting shares - when it is not. Essentially your Bitaxe has crashed and needs to be restarted. 

This python script constantly monitors your Bitaxe for flatlining hashrate/shares and will restart if it detects the shares not increasing.

## Usage
Run the Bitaxe Flatline Monitor by providing your Bitaxe's IP address:
```
python bitaxe_flatline_monitor.py <bitaxe_ip>
```

### Optional parameters:

`-i`, `--interval` : How many seconds between checking for flatlining (default: 60)

Example:
```
python bitaxe_flatline_monitor.py 192.168.2.88 -i 120
```
