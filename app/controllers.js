var paySafeControllers = angular.module('paySafeControllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope',
	function($scope) {
		$scope.transactions = [
			{ id: "1", sender: "Hou", receiver: "Hallow", amount: 3, description: "Oke"},
			{ id: "2", sender: "Hoi", receiver: "Hallow!", amount: 5, description: "Goed"},
		];
	}
]);


paySafeControllers.controller('TransactionShowCtrl', ['$scope', '$routeParams',
	function($scope, $routeParams) {
		transaction_id = $routeParams.id;
		//Query server
		//Decrypt data
		//$scope.transaction = decrypted data
		$scope.transaction = { id: transaction_id, sender: "Hou", receiver: "Hallow", amount: 3, description: "Oke"};
	}
]);

paySafeControllers.controller('TransactionSearchCtrl', ['$scope',
	function($scope) {
		amount_mapping = [];
		var functions = {
			"amount": {
				"greater": function(amount){
					var temp = (amount - (amount % 1000))/1000;
					var result = "" + temp;
					for (i = temp+1; i < 10; i++){
						result = result + "," + i;
					}
					return result;
				},
				"equal": function(amount){
					return (amount - (amount % 1000))/1000;
				},
				"less": function(amount){
					var temp = (amount - (amount % 1000))/1000;
					var result = "" + temp;
					for (i = temp-1; i > -1; i--){
						result = result + "," + i;
					}
					return result;
				}
			},
			"date": {
				"greater": function(amount){
					var temp = (amount - (amount % 1000))/1000;
					var result = "" + temp;
					for (i = temp+1; i < 10; i++){
						result = result + "," + i;
					}
					return result;
				},
				"equal": function(amount){
					return (amount - (amount % 1000))/1000;
				},
				"less": function(amount){
					var temp = (amount - (amount % 1000))/1000;
					var result = "" + temp;
					for (i = temp-1; i > -1; i--){
						result = result + "," + i;
					}
					return result;
				}
			}
		}
		$scope.field = "amount";
		$scope.operation = "equal";
		$scope.show_table = false;
		$scope.query = function() {
			var query=$scope.field + "=" + functions[$scope.field][$scope.operation]($scope.search_field);
			window.alert(query);
			$scope.show_table = true;
		}
		//Query server
		//Decrypt data
		//$scope.transaction = decrypted data

		$scope.transactions = [
			{ id: "1", sender: "Hou", receiver: "Hallow", amount: 3, description: "Oke"},
			{ id: "2", sender: "Hoi", receiver: "Hallow!", amount: 5, description: "Goed"},
		];
	}
]);

paySafeControllers.controller('ClientLoginCtrl');
paySafeControllers.controller('ClientRegisterCtrl');