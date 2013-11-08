function addRow(id, sender, receiver, amount, description) {
	var container = $("#output tbody");
	container.append("<tr><td>" + id + "</td><td>" + sender + "</td><td>" + receiver + "</td><td>" + amount + "</td><td>" + description +"</td></tr>" );
}

function addDataToForm(sender, receiver, amount, description) {
	$("#visible_form #id_sender").val(sender);			
	$("#visible_form #id_receiver").val(receiver);
	$("#visible_form #id_amount").val(amount);
	$("#visible_form #id_description").val(description);
}

function addData(data) {
	var sender = $("#output #sender");
	sender.append(data["sender"]);
	var receiver = $("#output #receiver");
	receiver.append(data["receiver"]);
	var amount = $("#output #amount");
	amount.append(data["amount"]);
	var description = $("#output #description");
	description.append(data["description"]);
	var miliseconds = $("#output #miliseconds");
	miliseconds.append(data["miliseconds"]);
}

function decrypt(data){
	return JSON.stringify(data);
}

function encrypt(input){
	return JSON.stringify(input);
}

function hash(input){
	return input;
}




function amountMappingFunction(input){
	input = parseInt(input);
	input = (input - input % 1000)/1000;
	if (input < 0) {
		input = 0;
	} 
	if (input > 10) {
		input = 10;
	}
	return hash(input);
}

function clientMappingFunction(user_id){
	return user_id;
}

function dateMappingFunction(input){
	var year = 1000*60*60*24*365;
	input = parseInt(input);
	input = (input - input % year)/year;
	return hash(input);
}
