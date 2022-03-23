// Encode Base64
function toBase64String(words){
      return CryptoJS.enc.Base64.stringify(words);
}

// Decode Base64
function base64toString(input) {
    return CryptoJS.enc.Base64.parse(input);
}

// Decode UTF-8
function toWordArray(str){
      return CryptoJS.enc.Utf8.parse(str);
}

// Encode UTF-8
function toString(words){
      return CryptoJS.enc.Utf8.stringify(words);
}

// Encrypt AES256-CBC with iv
function AESencrypt(plain, key) {
    var iv = CryptoJS.lib.WordArray.random(16);
    var cipher = CryptoJS.AES.encrypt(plain, key, {iv: iv});
    encrypted = iv.toString() + cipher
    return encrypted;
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
	console.log('key: ' + key);

	function AESencrypt (data, key) {

		var iv = CryptoJS.lib.WordArray.random(8);
		iv = iv.toString();

		const cipher = CryptoJS.AES.encrypt(data, CryptoJS.enc.Utf8.parse(key), {
		       iv: CryptoJS.enc.Utf8.parse(iv), // parse the IV
		       padding: CryptoJS.pad.Pkcs7,
		       mode: CryptoJS.mode.CBC
		   });

	  	 // e.g. B6AeMHPHkEe7/KHsZ6TW/Q==
	 	  return cipher.toString();
	}

    	function AESdecrypt(ivCipherText, key){

		console.log('Start Decr');
		var ivB64 = ivCipherText.slice(0, 24);
		var iv = atob(ivB64);
		data = ivCipherText.slice(24);
		console.log('Sliced');

		key = CryptoJS.enc.Utf8.parse(key);
		iv  = CryptoJS.enc.Utf8.parse(iv);
		console.log('Parsed');
		var cipherParams = CryptoJS.lib.CipherParams.create({
		    ciphertext: CryptoJS.enc.Base64.parse(data)
			});
		console.log('Paramed');
		var decryptedFromText = CryptoJS.AES.decrypt(cipherParams, key, { iv: iv});
		console.log('decrypted');
		return decryptedFromText.toString(CryptoJS.enc.Utf8);
	}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Decrypt AES256-CBC with iv
function AESdecrypt(cipher, key) {
    plain = CryptoJS.AES.decrypt(cipher, key, {iv: iv});
}

