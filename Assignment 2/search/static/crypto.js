// This class is used for encryption/decryption
var Crypto = function(key) {

	this.decrypt = function(ciphertext) {
		try {
			var decrypted_data = CryptoJS.enc.Utf8.stringify(CryptoJS.AES.decrypt(atob(ciphertext), key));
			}
		catch (err){
			return false;
		}
		if (decrypted_data.indexOf(this.testString) == 0){
			return JSON.parse(decrypted_data.substring(this.testString.length, decrypted_data.length));
		}
		return false;
	}

	this.encrypt = function(jsObj) {
		return btoa(CryptoJS.AES.encrypt(this.testString + JSON.stringify(jsObj), key).toString());
	}

	this.bucket = function(input) {
		return CryptoJS.SHA3(input + this.key).toString()[0];
	}

	this.testString = "testString"
};