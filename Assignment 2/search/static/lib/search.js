var amount_bucket = {
	bucket_list: [0,1000,2000,3000,4000,5000,6000,7000,8000,9000],
	query: function(small, large){
		index_of_small = 0;
		for (i = 0; i < amount_bucket.bucket_list.length -1; i++){
			if (amount_bucket.bucket_list[i] <= small && small < amount_bucket.bucket_list[i+1] ){
				index_of_small = i;
				break;
			}
		}
		result = "" + index_of_small;
		for (i = index_of_small; i < amount_bucket.bucket_list.length ; i++){
			if (small < amount_bucket.bucket_list[i] && amount_bucket.bucket_list[i] <= large ){
				result = result + "," + i;
			}
		}
		return "amount/" + result + "/";
	},
	value: function(amount){
		return 5;
	}
};
var date_bucket = {
	bucket_list: [0,1,2,3,4,5,6,7,8,9],
	query: function(small, large){
		return "date/3,4,5,6/";
	},
	value: function(amount){
		return 5;
	}
};


var search_form = {
	amount: {
		operations: [
		{
			name: "Greater than",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.query(search_form.amount.single_amount, amount_bucket.max);
			},
			is_valid_result: function(transaction){
				return transaction.amount > parseInt(search_form.amount.single_amount);
			}
		},
		{	
			name: "Less than",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.query(amount_bucket.min, search_form.amount.single_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount < search_form.amount.single_amount;
			}
		},
		{
			name: "Equal to",
			is_between: false,
			list_buckets: function(){
				return amount_bucket.query(search_form.amount.single_amount, search_form.amount.single_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount == search_form.amount.single_amount;
			}
		},
		{
			name: "Between",
			is_between: true,
			list_buckets: function(){
				return amount_bucket.query(search_form.amount.from_amount, search_form.amount.to_amount);
			},
			is_valid_result: function(transaction){
				return transaction.amount > search_form.amount.from_amount && transaction.amount < search_form.amount.to_amount;
			}
		}],
		enabled: false
	},
	date: {
		operations: [
		{
			name: "After",
			is_between: false,
			list_buckets: function(){
				return date_bucket.query(search_form.date.single_date, date_bucket.max);
			},
			is_valid_result: function(transaction){
				return true;
			}
		},
		{	
			name: "Before",
			is_between: false,
			list_buckets: function(){
				return date_bucket.query(date_bucket.min, search_form.date.single_date);
			},
			is_valid_result: function(transaction){
				return true;
			}
		},
		{
			name: "On",
			is_between: false,
			list_buckets: function(){
				return date_bucket.query(search_form.date.single_date, search_form.date.single_date);
			},
			is_valid_result: function(transaction){
				return true;
			}
		},
		{
			name: "Between",
			is_between: true,
			list_buckets: function(){
				return date_bucket.query(search_form.date.from_date, search_form.date.to_date);
			},
			is_valid_result: function(transaction){
				return true;
			}
		}],
		enabled: false,
		single_date: {
			"date": "2012-09-01T00:00:00.000Z"
		},
		from_date: {
			"date": "2012-09-01T00:00:00.000Z"
		},
		to_date: {
			"date": "2012-09-01T00:00:00.000Z"
		}
	},

	generate_url: function(){
		result = "";
		if (search_form.amount.enabled){
			result = result + search_form.amount.operation.list_buckets();
		}
		if (search_form.date.enabled){
			result = result + search_form.date.operation.list_buckets();
		}
		return result;
	},

	is_valid_result: function(transaction){
		is_valid_amount = !search_form.amount.enabled || search_form.amount.operation.is_valid_result(transaction);
		is_valid_date = !search_form.date.enabled || search_form.date.operation.is_valid_result(transaction);
		return is_valid_amount && is_valid_date;
	}
};