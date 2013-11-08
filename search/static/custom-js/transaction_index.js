$(document).ready(function() {

	data = decrypt(data);

	data = JSON.parse(data);
	for (i in data) {
		var id = data[i]["id"]
		var transaction = JSON.parse(data[i]["data"]);
		addRow(id, transaction["sender"], transaction["receiver"], transaction["amount"], transaction["description"]);
	}
	$('input.filter').on('keyup', function() {
    var rex = new RegExp($(this).val(), 'i');
    $('.searchable tr').hide();
        $('.searchable tr').filter(function() {
            return rex.test($(this).text());
        }).show();
    });
});