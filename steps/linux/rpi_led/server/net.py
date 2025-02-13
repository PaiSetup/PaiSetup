import time

import machine
import network
import uasyncio as asyncio

ssid = "MiliLokatorzy 2,4GHz"
password = "Smile4Smile"
wlan = network.WLAN(network.STA_IF)
port = 30123


def connect():
    if wlan.isconnected():
        return True

    wlan.active(True)
    wlan.connect(ssid, password)

    for _ in range(20):
        status = wlan.status()
        if status in [network.STAT_CONNECT_FAIL, network.STAT_WRONG_PASSWORD, network.STAT_NO_AP_FOUND, network.STAT_GOT_IP]:
            break
        time.sleep(0.5)

    if wlan.status() == network.STAT_GOT_IP:
        return True
    else:
        # There was an error connecting. Print the error.
        errors = {
            network.STAT_IDLE: "no activity",
            network.STAT_CONNECTING: "still connecting",
            -network.STAT_WRONG_PASSWORD: "wrong password",
            -network.STAT_NO_AP_FOUND: "no response",
            -network.STAT_CONNECT_FAIL: "general failure",
        }
        status = wlan.status()
        error = errors.get(status, f"unknown error {status}")
        print(f'Failed connecting to "{ssid}" - {error}')

        # Sometimes the board fails to connect to WiFi when first connect to power.
        # No idea why that is, but performing a hard reset always helps. Soft reset
        # also helps but requires more iterations (usually 3-4). I tried to add big
        # sleeps before connecting, but it also didn't help.
        if machine.reset_cause() == machine.PWRON_RESET:
            machine.reset()
        else:
            return False


def set_hostname(hostname):
    wlan.config(hostname=hostname)


def print_config():
    ip, subnet, gateway, dns = wlan.ifconfig()
    ssid = wlan.config("ssid")
    hostname = wlan.config("hostname")
    connected = wlan.status() == network.STAT_GOT_IP

    config = {
        "ssid": ssid,
        "connected": connected,
        "ip": ip,
        "hostname": hostname,
    }
    for k, v in config.items():
        print(f"{k} = {v}")


def disconnect():
    wlan.disconnect()
    wlan.active(False)


def start_async_server(client_handler):
    ip = wlan.ifconfig()[0]
    print(f"Starting async server on {ip}:{port}")
    return asyncio.start_server(client_handler, ip, port)
