function decrypt(data){
	return angular.fromJson(data);
}

function encryptTransaction(data){
	delete data.id;
	return JSON.stringify(data);
}