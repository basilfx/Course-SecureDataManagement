function decrypt(data){
	return angular.fromJson(data);
}

function encryptTransaction(data){
	return JSON.stringify(data);
}