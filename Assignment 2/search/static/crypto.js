// This is where the user's crypto object is stored in
var userCrypto = undefined;

// This class is used for encryption/decryption
var Crypto = function(key) {
	this.key = key;

	var settings = {
		cipher: CryptoJS.AES,
		iv: window.crypto.getRandomValues(new Uint32Array(1))[0],
		mode: CryptoJS.mode.CFB,
		padding: CryptoJS.pad.Pkcs7,
		formatter: JsonFormatter
	};

	this.decrypt = function(ciphertext) { settings.cipher.decrypt(ciphertext, this.key); }

	this.encrypt = function(plaintext) { settings.cipher.encrypt(plaintext, this.key); }
};

// Creates the proper format for storage on server and the proper way to format decryption output
var JsonFormatter = {
	// Creates format for secure storage on remote server
	stringify: function(cipherParams) {
		// Create JSON object with given ciphertext
		var jsonObj = {
			ct: cipherParams.ciphertext.toString(CryptoJS.enc.Base64)
		};

		// Add iv if present
		if(cipherParams.iv) {
			jsonObj.iv = cipherParms.iv.toString();
		}
		// Add salt if prestent
		if(cipherParams.s) {
			jsonObj.s = cipherParms.s.toString();
		}

		return JSON.stringify(jsonObj);
	},

	// Reads server string to create format suitable for use client side
	parse: function(jsonStr) {
		var jsonObj = JSON.parse(jsonStr);

		// Extract cipherparams from string
		var cipherParams = CryptoJS.lib.CipherParams.create({
			ciphtertext: CryptoJS.enc.Base64.parse(jsonObj.ct)
		});

		// Add iv if present
		if(jsonObj.iv) {
			cipherParams.iv = CryptoJS.enc.Hex.parse(jsonObj.iv);
		}

		// Add salt if present
		if(jsonObj.s) {
			cipherParams.s = CryptoJS.enc.Hex.parse(jsonObj.s);
		}

		return cipherParams;
	}
};