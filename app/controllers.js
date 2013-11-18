var paySafeControllers = angular.module('paySafeApp.controllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope',
	function($scope) {
		$scope.transactions = [
			{ id: 1, sender: "Hou", receiver: "Hallow", amount: 3, description: "Oke", editMode: false},
			{ id: 2, sender: "Hoi", receiver: "Hallow!", amount: 5, description: "Goed", editMode: false},
		];

		$scope.createTransaction = function() {
			$scope.transactions.push({
				id: newId(), sender: "", receiver: "", amount: 0,
				description: "", editMode: true
			});
		}

		$scope.updateTransaction = function(id) {
			$scope.transactions.forEach(function(t) {
				if(t.id === id) {
					t.editMode = false;
				}
			})
		}

		$scope.deleteTransaction = function(id) {
			$scope.transactions = $scope.transactions.filter( function(t) {
				return t.id !== id;
			})
		}

		function newId() {
			return 1 + Math.max.apply(null, $scope.transactions.map( function(t) { return t.id; }));
		}
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
		$scope.search_form = search_form;
		$scope.search_form.amount.operation = $scope.search_form.amount.operations[0];
		$scope.search_form.date.operation = $scope.search_form.date.operations[0];
		amount_bucket.min = amount_bucket.bucket_list[0];
		amount_bucket.max = amount_bucket.bucket_list[amount_bucket.bucket_list.length -1];
		date_bucket.min = date_bucket.bucket_list[0];
		date_bucket.max = date_bucket.bucket_list[date_bucket.bucket_list.length -1];

		$scope.search_url = "";
		$scope.search = function() {
			$scope.search_url = $scope.search_form.generate_url();
			
			var new_transactions = []; //TODO: Get results and store them in this variable
			$scope.transactions = [];
			for (var transaction in new_transactions){
				if ($scope.search_form.is_valid_result(transaction)){
					$scope.tranactions.push(tranaction);
				}
			}

			$scope.show_table = true;
		};
	}
]);

paySafeControllers.controller('ClientLoginCtrl');
paySafeControllers.controller('ClientRegisterCtrl');