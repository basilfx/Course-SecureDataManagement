// This class is used for encryption/decryption
var Crypto = function(key) {
	this.key = key;
	this.cipher = CryptoJS.AES;
	
	this.decrypt = function(ciphertext) {
		return CryptoJS.AES.decrypt(ciphertext, this.key).toString(CryptoJS.enc.Utf8);
	}

	this.encrypt = function(jsObj) {
		console.log(jsObj);
		return CryptoJS.AES.encrypt(jsObj, this.key).ciphertext.toString();
	}
};