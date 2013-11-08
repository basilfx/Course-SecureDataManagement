$(document).ready(function() {

	data = decrypt(data);

	data = JSON.parse(data);
	for (i in data) {
		var id = data[i]["id"]
		var transaction = JSON.parse(data[i]["data"]);
		addRow(id, transaction["sender"], transaction["receiver"], transaction["amount"], transaction["description"]);
	}

});