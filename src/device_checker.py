import ctypes
import os
import sys


class DeviceCheckerMac:

    def check_is_screen_locked(self):
        import Quartz
        d = Quartz.CGSessionCopyCurrentDictionary()
        return d.get("CGSSessionScreenIsLocked", 0) == 1

    def lock_screen(self):
        if self.check_is_screen_locked():
            return
        os.system('pmset displaysleepnow')


class DeviceCheckerWindows:

    def check_is_screen_locked(self):
        return ctypes.windll.user32.GetForegroundWindow() % 10 == 0

    def lock_screen(self):
        if self.check_is_screen_locked():
            return
        return ctypes.windll.user32.LockWorkStation() == 0


class DeviceCheckerLinux:

    def check_is_screen_locked(self):
        return os.system('gnome-screensaver-command -q') == 0

    def lock_screen(self):
        if self.check_is_screen_locked():
            return
        os.system('gnome-screensaver-command -l')


def get_platform():
    if sys.platform == "linux" or sys.platform == "linux2":
        return "linux"
    elif sys.platform == "darwin":
        return "mac"
    elif sys.platform == "win32":
        return "win"


def get_device_checker():
    platform = get_platform()
    if platform == "mac":
        return DeviceCheckerMac()
    elif platform == "win":
        return DeviceCheckerWindows()
    elif platform == "linux":
        return DeviceCheckerLinux()


class DeviceChecker:
    def __init__(self):
        self.device_checker = get_device_checker()

    def check_is_screen_locked(self):
        return self.device_checker.check_is_screen_locked()

    def lock_screen(self):
        self.device_checker.lock_screen()
