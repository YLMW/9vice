from ..requester import request
from ..crypto import crypto


def beutify_info(user_info: tuple) -> dict:
    info = {
        "id": user_info[0],
        "username": user_info[1],
        "mail": user_info[2],
        "isAdmin": bool(user_info[4])
    }
    return info


def get_info(cookie: str) -> dict:
    try:
        req = request.Requester()
        aes = crypto.AESCipher()
        user_id = aes.decrypt(cookie)
        user_info = req.user_info(int(user_id))
        return beutify_info(user_info)
    except Exception as e:
        print("[CRITICAL] " + str(e))
        return {}


def is_logged(dict) -> bool:
    return dict != {}
