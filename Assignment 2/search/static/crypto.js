// This class is used for encryption/decryption
var Crypto = function(key) {
	this.decrypt = function(ciphertext) {
		return JSON.parse(CryptoJS.enc.Utf8.stringify(CryptoJS.AES.decrypt(atob(ciphertext), key)));
	}

	this.encrypt = function(jsObj) {
		return btoa(CryptoJS.AES.encrypt(JSON.stringify(jsObj), key).toString());
	}

	this.bucket = function(input) {
		return CryptoJS.SHA3(input + this.key).toString()[0];
	}
};