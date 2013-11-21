var symmetric_key = "";

var amount_bucket = {
	max: 0,
	min: 0,
	map: [0,1710,2436,2927,3316,3651,3951,4229,4493,4748,5000,5251,5506,5770,6048,6348,6683,7072,7563,8289],

	generateAmountQuery: function(lower_amount, upper_amount){
		var lower_index = amount_bucket.amountToIndex(lower_amount);
   		var upper_index = amount_bucket.amountToIndex(upper_amount);	   
   		var r = indexToBucketValues(lower_index, upper_index, amount_bucket.map.length/2, "amount");
   		console.log(r);
   		return r;
	},

	amountToIndex: function(amount) { 
	    var index = amount_bucket.map.length -1;
	    for (i = 0; i < amount_bucket.map.length -1; i++) {
	        if (amount_bucket.map[i] <= amount && amount < amount_bucket.map[i+1]) {
	            index = i;
	            break;
	        }
	    }
	    return index;
	}	
};
var date_bucket = {
	max: "2013-12-1", //1 Dec 2013
	min: "1970-1-1",

	generateDateQuery: function(lower_date_str, upper_date_str){
		if(lower_date_str && upper_date_str) {		// Check if not empty strings
			var lower_date_month = parseInt(lower_date_str.split("-")[1]) - 1;
			var upper_date_month = parseInt(upper_date_str.split("-")[1]) - 1;
			if(lower_date_month + 1 && upper_date_month + 1) {		// Check if both are not NaN
				return indexToBucketValues(lower_date_month, upper_date_month, 6, "date")
			}
		}
		return "";
	},

    dateToIndex: function(date_str) {
        return new Date(date_str).getMonth()%6;
    }
};

function indexToBucketValues(lower_index, upper_index, number_of_buckets, field) {
    var values = [];
    for (i = lower_index; i <= upper_index; i++){
        values.push(indexToBucketValue(i%number_of_buckets,field));
    }        
    values.sort();
    console.log(values);
    var result = values.filter(function(elem, pos) {
		return values.indexOf(elem) == pos;
	});
	console.log(result);
    return result.join();
}
     
function indexToBucketValue(index, field){
    var sha = CryptoJS.SHA3(index + field + symmetric_key);
    return sha.toString()[0];
}

function amountToBucket(amount){
    return indexToBucketValue(amount_bucket.amountToIndex(amount),"amount");
}

function dateToBucket(date){
    return indexToBucketValue(date_bucket.dateToIndex(date),"date");
}

var search_form = {
	amount: {
		operations: [
		{
			name: "Greater than",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.generateAmountQuery(search_form.amount.single_amount, amount_bucket.max);
			},
			is_valid_result: function(transaction){
				return transaction.amount > parseInt(search_form.amount.single_amount);
			}
		},
		{	
			name: "Less than",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.generateAmountQuery(amount_bucket.min, search_form.amount.single_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount < search_form.amount.single_amount;
			}
		},
		{
			name: "Equal to",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.amountToIndex(search_form.amount.single_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount == search_form.amount.single_amount;
			}
		},
		{
			name: "Between",
			is_between: true,
			list_buckets: function(){
				return amount_bucket.generateAmountQuery(search_form.amount.from_amount, search_form.amount.to_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount > search_form.amount.from_amount && transaction.amount < search_form.amount.to_amount;
			}
		}],
	},
	date: {
		operations: [
		{
			name: "After",
			is_between: false,
			list_buckets: function(){
				return date_bucket.generateDateQuery(search_form.date.single_date.date, date_bucket.max);
			},
			is_valid_result: function(transaction){
				return transaction.date.valueOf() > new Date(search_form.date.single_date.date).valueOf();
			}
		},
		{	
			name: "Before",
			is_between: false,
			list_buckets: function(){
				return date_bucket.generateDateQuery(date_bucket.min, search_form.date.single_date.date);
			},
			is_valid_result: function(transaction){
				return transaction.date.valueOf() < new Date(search_form.date.single_date.date).valueOf();

			}
		},
		{
			name: "On",
			is_between: false,
			list_buckets: function(){
				return date_bucket.dateToIndex(search_form.date.single_date.date);
			},
			is_valid_result: function(transaction){
				return transaction.date.valueOf() == new Date(search_form.date.single_date.date).valueOf();
			}
		},
		{
			name: "Between",
			is_between: true,
			list_buckets: function(){
				return date_bucket.generateDateQuery(search_form.date.from_date.date, search_form.date.to_date.date);
			},
			is_valid_result: function(transaction){
				return transaction.date.valueOf() > new Date(search_form.date.from_date.date).valueOf() && transaction.date.valueOf() < new Date(search_form.date.to_date.date).valueOf();
			}
		}]
	},

	is_amount_ready: function() {
		return this.amount.single_amount > 0 || (this.amount.from_amount > 0 && this.amount.to_amount > 0);
	},

	is_date_ready: function() {
		return this.date.single_date || (this.date.from_date && this.date.to_date);
	},

	// Checks if the available parameters are enough to make a search
	is_ready_for_search: function() {
		return this.is_amount_ready() || this.is_date_ready();
	},

	generate_url: function(){
		result = "?"
		if (this.is_amount_ready()){
			result = result + "amount=" + search_form.amount.operation.list_buckets() + "&";
		}
		if (this.is_date_ready()){
			result = result + "date=" + search_form.date.operation.list_buckets();
		}
		return result;
	},

	is_valid_result: function(transaction){
		is_valid_amount = !search_form.amount.enabled || search_form.amount.operation.is_valid_result(transaction);
		is_valid_date = !search_form.date.enabled || search_form.date.operation.is_valid_result(transaction);
		return is_valid_amount && is_valid_date;
	}
};