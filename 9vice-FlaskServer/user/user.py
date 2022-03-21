from requester.request import Requester
from crypto import crypto
from datetime import datetime

def beautify_info(user_info: tuple) -> dict:
    lastcon = "Jamais"

    if user_info[6]:
        lastcon = str(datetime.now() - user_info[6]).split('.')[0]#.replace(':', 'h ', 1).replace(':', 'm ', 1) + 's'
        hour= lastcon.split(":")[0]
        min=lastcon.split(":")[1]
        sec=lastcon.split(":")[2]

        activite = "En Ligne" if (int(hour) ==0 and int(min)<5) else hour + "h " + min + "m " + sec + "s"

    info = {
        "id": user_info[0],
        "username": str(user_info[1]).capitalize(),
        "mail": user_info[2],
        "isAdmin": bool(user_info[4]),
        "isBlocked": bool(user_info[5]),
        "lastCon": activite
    }
    return info

def beautify_list(user_list: list) -> list:
    liste = []
    for user in user_list:
        liste.append(beautify_info(user))
    return sorted(liste, key=lambda x:x["id"])

def get_info(cookie: str) -> dict:
    try:
        req = Requester()
        aes = crypto.AESCipher()
        user_id = aes.decrypt(cookie)
        user_info = req.user_info(int(user_id))
        return beautify_info(user_info)
    except Exception as e:
        print("[CRITICAL] " + str(e))
        return {}


def is_logged(dicti: dict) -> bool:
    return dicti != {}


def is_locked(dicti: dict) -> bool:
    return dicti["isBlocked"]