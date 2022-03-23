aes = CryptoJS.AES
b64 = CryptoJS.

function AESencrypt(plain, key) {
    return aes.encrypt(plain, key);
}

function AESdecrypt(cipher, key) {
    return aes.decrypt(cipher, key);
}

function b64encode(data) {

}
