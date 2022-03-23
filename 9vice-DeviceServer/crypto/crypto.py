from Crypto.Cipher import AES
from Crypto import Random
import secrets
import string


import base64
from Crypto.Util.Padding import pad

def aes_cbc_encrypt_text(decrypt_text: str, key: str) -> str:
    """
    encryption AES_CBC The plaintext of
    :param decrypt_text: Plaintext
    :param key: secret key
    :param iv: Key offset
    :return: ciphertext
    """

    # Gen IV Alea
    iv = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(16))
    aes2 = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypt_text = aes2.encrypt(pad(decrypt_text.encode('utf-8'), AES.block_size, style='pkcs7'))
    encrypt_text = str(base64.encodebytes(encrypt_text), encoding='utf-8').replace("\n", "")

    ivB64 = base64.b64encode(iv.encode('utf-8'))
    ivCipherText = ivB64.decode('utf-8') + encrypt_text

    return ivCipherText # 24 char d'IV puis le cipher text


def aes_cbc_decrypt_js_text(ivCipherText: str, key: str) -> str:
    """
    decrypt AES_CBC The ciphertext of
    :param encrypt_text: ciphertext
    :param key: secret key
    :param iv: Key offset
    :return:Decrypted data
    example_url_learn_js_base64: aHR0cDovL2NyZWRpdC5jdXN0b21zLmdvdi5jbi8=
    """

    iv = base64.b64decode(ivCipherText[:24])
    print("IV Found : "); print(iv)
    encrypt_text = ivCipherText[24:]
    decode_encrypt_text = base64.b64decode(encrypt_text)
    # When initializing the AES object, pass in the same key, encryption mode, and iv as the encryption
    aes2 = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    decrypt_text = aes2.decrypt(decode_encrypt_text).decode('utf8')
    decrypt_text = decrypt_text.replace(b'\x00'.decode(), "").replace("", "")
    s = decrypt_text
    return s[:-ord(s[len(s) - 1:])]



