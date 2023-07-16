import simplepyble as ble
import numpy as np
import argparse
import os
import time
from sys import platform

## Parse arguments
parser = argparse.ArgumentParser(description='Simple BLE')

parser.add_argument('-d', '--device', type=str, required=True, help='BLE device name')
parser.add_argument('-t', '--threshold', type=int, default=10, help='Threshold for distance (cm)')

args = parser.parse_args()

## Setting up adapter
adapter : ble.Adapter = ble.Adapter.get_adapters()[0]
distances = np.array([])
main_loop = True

def get_distance(power, rssi):
    return 10 ** ((power - rssi) / 20)

def get_platform():
    if platform == "linux" or platform == "linux2":
        return "linux"
    elif platform == "darwin":
        return "mac"
    elif platform == "win32":
        return "win"

def send_lock_mac():
    os.system('pmset displaysleepnow')

def send_lock_win():
    os.system('rundll32.exe user32.dll,LockWorkStation')

def send_lock_linux():
    os.system('gnome-screensaver-command -l')

def lock_screen():
    platform = get_platform()
    if platform == "mac":
        send_lock_mac()
    elif platform == "win":
        send_lock_win()
    elif platform == "linux":
        send_lock_linux()

def on_scan_stop():
    global main_loop
    main_loop = False
    pass

def on_device_scanned(peripheral: ble.Peripheral):
    identifier = peripheral.identifier()

    if identifier != args.device:
        return
    
    distance = get_distance(peripheral.tx_power(), peripheral.rssi())

    if distance == 0:
        return
    
    global distances
    distances = np.append(distances, distance)

    if len(distances) > 10:
        distances = distances[1:]
    
    average = int(np.mean(distances))

    if average >= args.threshold:
        lock_screen()
        adapter.scan_stop()

adapter.set_callback_on_scan_updated(on_device_scanned)
adapter.set_callback_on_scan_stop(on_scan_stop)
adapter.scan_start()

try:
    while main_loop:
        time.sleep(1)
        pass
except KeyboardInterrupt:
    exit(0)