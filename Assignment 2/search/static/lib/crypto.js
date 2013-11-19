function decrypt(data){
	return angular.fromJson(data);
}

function encryptTransaction(data){
	delete data.id;
	data.date = data.date.valueOf();
	return JSON.stringify(data);
}

function sha3(data){
	return data;
}