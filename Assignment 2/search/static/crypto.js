// This class is used for encryption/decryption
var Crypto = function(key) {
	this.key = key;
	this.cipher = CryptoJS.AES;
	
	this.decrypt = function(ciphertext) {
		return JSON.parse(CryptoJS.enc.Utf8.stringify(CryptoJS.AES.decrypt(window.atob(ciphertext), this.key)));
	}

	this.encrypt = function(jsObj) {
		console.log(jsObj);
		return window.btoa(CryptoJS.AES.encrypt(JSON.stringify(jsObj), this.key).toString());
	}

	this.bucket = function(input) {
		return input;//CryptoJS.SHA3(input + this.key).toString()[0];
	}
};