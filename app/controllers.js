var paySafeControllers = angular.module('paySafeControllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope',
	function($scope) {
		$scope.transactions = [
			{ id: "1", sender: "Hou", receiver: "Hallow", amount: 3, description: "Oke"},
			{ id: "2", sender: "Hoi", receiver: "Hallow!", amount: 5, description: "Goed"},
		];
	}
]);