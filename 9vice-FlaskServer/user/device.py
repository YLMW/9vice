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
    return sorted(liste, key=lambda x: not x["active"])


def get_devices_info(user_id: int) -> list:
    try:
        req = Requester()
        devices_info = req.list_devices(int(user_id))
        devices_list = beautify_device_list(devices_info)
        return devices_list
    except Exception as e:
        print("[CRITICAL] get_devices_info : " + str(e))
        return {}


def get_device_id(user_id: int, device_name: str) -> int:
    try:
        req = Requester()
        device_id = req.get_id_device(user_id, device_name)
        return device_id
    except Exception as e:
        print('[CRITICAL] get_device_id : ' + str(e))
        return -1


def get_device_hash(device_id: int) -> str:
    try:
        req = Requester()
        device_hash = req.get_hash_device(device_id)
        return device_hash
    except Exception as e:
        print('[CRITICAL] get_device_hash : ' + str(e))
        return ''


def is_active(device: dict) -> bool:
    return device["active"]


def set_active(id_user: int, id_device: int) -> bool:
    try:
        req = Requester()
        return req.set_active(id_user, id_device) and req.new_historique(id_user, id_device)
    except Exception as e:
        print('[CRITICAL] set_active : ' + str(e))
        return ''


def set_inactive(id_device: int) -> bool:
    try:
        req = Requester()
        return req.set_inactive(id_device)
    except Exception as e:
        print('[CRITICAL] set_active : ' + str(e))
        return ''
