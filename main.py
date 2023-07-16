import simplepyble as ble
import numpy as np
import argparse
import os
import time
from sys import platform
from src.device_checker import DeviceChecker
import signal

# Parse arguments
parser = argparse.ArgumentParser(description='Simple BLE')

parser.add_argument('-d', '--device', type=str,
                    required=True, help='BLE device name')
parser.add_argument('-t', '--threshold', type=int,
                    default=10, help='Threshold for distance (cm)')

parser.add_argument('--debug', action='store_true', help='Debug mode')

args = parser.parse_args()
device = DeviceChecker()
did_auto_lock = False
initial_state = True

# Setting up adapter
adapter: ble.Adapter = ble.Adapter.get_adapters()[0]
distances = np.array([])
main_loop = True
did_change_state = False


def debug_print(*args):
    if args.debug:
        print(*args)

def get_distance(power, rssi):
    return 10 ** ((power - rssi) / 20)


def is_increasing():
    global distances

    if len(distances) < 10:
        return False

    first_five = distances[:5]
    last_five = distances[5:]

    first_five_mean = np.mean(first_five)
    last_five_mean = np.mean(last_five)

    return last_five_mean > first_five_mean


def on_device_scanned(peripheral: ble.Peripheral):
    global device
    global did_auto_lock
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

    if average >= args.threshold and not did_auto_lock:
        did_auto_lock = True
        adapter.scan_stop()
        device.lock_screen()
        debug_print("Locked screen with distance", average, "cm")
    else:
        debug_print(f'[{average}] Threshold not reached')


adapter.set_callback_on_scan_updated(on_device_scanned)

last_is_locked = device.check_is_screen_locked()


def handle_interrupt(signal, frame):
    # Add any cleanup code here if needed
    exit(0)


signal.signal(signal.SIGINT, handle_interrupt)

while main_loop:
    is_locked = device.check_is_screen_locked()
    did_change_state = is_locked != last_is_locked
    last_is_locked = is_locked

    if did_change_state or initial_state:
        initial_state = False
        is_scanning = adapter.scan_is_active()

        if not is_locked:
            did_auto_lock = False

        if is_locked and is_scanning:
            adapter.scan_stop()
            debug_print("should stop scanning")

        if not is_locked and not is_scanning:
            adapter.scan_start()
            debug_print("should start scanning")

    time.sleep(1)
