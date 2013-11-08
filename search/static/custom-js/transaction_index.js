$(document).ready(function() {

	function addRow(id, sender, receiver, amount, description) {
		var container = $("#output tbody");

		container.append("<tr><td>" + id + "</td><td>" + sender + "</td><td>" + receiver + "</td><td>" + amount + "</td><td>" + description +"</td></tr>" );
	}
	function decrypt(data){
		return data;
	}

	data = decrypt(data);


	for (i in data) {
		var id = data[i]["id"]
		var transaction = JSON.parse(data[i]["data"]);
		addRow(id, transaction["sender"], transaction["receiver"], transaction["amount"], transaction["description"]);
	}

});