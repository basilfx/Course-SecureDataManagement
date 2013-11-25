// This class is used for encryption/decryption
var Crypto = function(key) {
	this.key = key;
	this.cipher = CryptoJS.AES;
	this.mode = CryptoJS.mode.CBC;
	this.padding = CryptoJS.pad.Pkcs7;

	this.decrypt = function(ciphertext) {
		return this.cipher.decrypt(ciphertext, this.key, {
			mode: this.mode,
			padding: this.padding
		});
	}

	this.encrypt = function(plaintext) {
		return this.cipher.encrypt(plaintext, this.key, {
			mode: this.mode,
			padding: this.padding
		});
	}
};