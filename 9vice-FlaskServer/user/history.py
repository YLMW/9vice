from requester.request import Requester
from datetime import datetime


def beautify_history(history_info: tuple) -> dict:
    info = {
        "id_device": history_info[1],
        "id_user": history_info[2],
        "name": str(history_info[0]).capitalize(),
        "timestamp": history_info[3].strftime("%d %B, %Y, %H:%M:%S")
    }

    return info


def beautify_history_list(history_list: list) -> list:
    liste = []
    for hist in history_list:
        liste.append(beautify_history(hist))
    return liste


def get_history_info(user_id: int) -> list:
    try:
        req = Requester()
        history_info = req.get_user_history(int(user_id))
        history_list = beautify_history_list(history_info)
        return history_list
    except Exception as e:
        print("[CRITICAL] get_history_info : " + str(e))
        return {}


def get_history_info_like(user_id: int, like: str) -> list:
    try:
        req = Requester()
        history_info = req.get_historique_like(int(user_id), like)
        history_list = beautify_history_list(history_info)
        return history_list
    except Exception as e:
        print("[CRITICAL] get_history_info : " + str(e))
        return {}
