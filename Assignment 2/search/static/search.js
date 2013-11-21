var symmetric_key = "";

var amount_bucket = {
        max: 0,
        min: 0,
        map: [0,1000,2000,3000,4000,5000,6000,7000,8000,9000],

        generateAmountQuery: function(lower_amount, upper_amount){
           var lower_index = amount_bucket.amountToIndex(lower_amount);
           var upper_index = amount_bucket.amountToIndex(upper_amount);           
           return indexToBucketValues(lower_index, upper_index, amount_bucket.map.length/2, "amount");
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
        max: 1387461777260, //1 Dec 2013
        min: 0,

        generateDateQuery: function(lower_date, upper_date){
           var lower_index = new Date(lower_date).getMonth();
           var upper_index = new Date(upper_date).getMonth();
           return indexToBucketValues(lower_index, upper_index, 6, "date");
        },

        dateToIndex: function(date){
                return new Date(date).getMonth() % 6;
        }
};

function indexToBucketValues(lower_index, upper_index, number_of_buckets, field) {
    var values = [];
    for (i = lower_index; i < upper_index + 1; i++){
        values.push(indexToBucketValue(i%number_of_buckets,field));
    }        
    values.sort();
    
    var result = values.filter(function(elem, pos) {
                return values.indexOf(elem) == pos;
        });
    return result.join();
}
     
function indexToBucketValue(index, field){
    result = sha3(index + field + symmetric_key)
    return result[0];
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
                enabled: false
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
                }],
                enabled: false,
                single_date: {
                        date: new Date()
                },
                from_date: {
                        date: new Date()
                },
                to_date: {
                        date: new Date()
                }
        },

        generate_url: function(){
                result = "?"
                if (search_form.amount.enabled){
                        result = result + "amount=" + search_form.amount.operation.list_buckets() + "&";
                }
                if (search_form.date.enabled){
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