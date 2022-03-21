from requester.request import Requester
from crypto import crypto
from datetime import datetime


def beautify_device(device_info: tuple) -> dict:
    info = {
        "id_device": device_info[0],
        "id_user": device_info[1],
        "name": str(device_info[2]).capitalize(),
        "camera": bool(device_info[3]),
        "micro": bool(device_info[4]),
        "folder": bool(device_info[5]),
        "active": bool(device_info[6])
    }
    return info


def beautify_device_list(device_list: list) -> list:
    liste = []
    for device in device_list:
        liste.append(beautify_device(device))
    return sorted(liste, key=lambda x:not x["active"])


def get_devices_info(user_id: int) -> list:
    try:
        req = Requester()
        devices_info = req.list_devices(int(user_id))
        devices_list = beautify_device_list(devices_info)
        return devices_list
    except Exception as e:
        print("[CRITICAL] get_devices_info : " + str(e))
        return {}


def is_active(device: dict) -> bool:
    return device["active"]
