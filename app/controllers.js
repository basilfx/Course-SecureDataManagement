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

paySafeControllers.controller('TransactionSearchCtrl', ['$scope', '$routeParams',
	function($scope, $routeParams) {
		$scope.field = "amount"
		$scope.operation = "equal"
		//Query server
		//Decrypt data
		//$scope.transaction = decrypted data
	}
]);

paySafeControllers.controller('ClientLoginCtrl');
paySafeControllers.controller('ClientRegisterCtrl');