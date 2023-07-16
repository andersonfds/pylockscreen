import simplepyble as ble
import numpy as np
import argparse
import pyautogui as gui
import os

## Parse arguments
parser = argparse.ArgumentParser(description='Simple BLE')

parser.add_argument('-d', '--device', type=str, required=True, help='BLE device name')
parser.add_argument('-t', '--threshold', type=int, default=10, help='Threshold for distance (cm)')

args = parser.parse_args()

## Setting up adapter
adapter : ble.Adapter = ble.Adapter.get_adapters()[0]
distances = np.array([])

def get_distance(power, rssi):
    return 10 ** ((power - rssi) / 20)

def lock_screen():
    if os.name == 'nt':
        gui.hotkey('win', 'l')
    elif os.name == 'darwin':
        gui.hotkey('command', 'ctrl', 'q')
    elif os.name == 'posix':
        gui.hotkey('super', 'l')

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

adapter.set_callback_on_scan_updated(on_device_scanned)
adapter.scan_start()

try:
    while True:
        pass
except KeyboardInterrupt:
    exit(0)