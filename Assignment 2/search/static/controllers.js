//// FIXME !!!!
userCrypto = new Crypto("key");

var paySafeControllers = angular.module('paySafeApp.controllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope', '$http', '$location',
	function($scope,$http, $location) {
		$scope.transactions = [];
		$scope.testdata = "";
		$scope.errordata = "";
		
		$http({method: 'GET', url: '/search/transactions/'
		}).success(function(data, status, headers, config) {
			if(data["login_successful"]==false){
				$location.path("/login");
			}
			else{
				for (i = 0; i < data.length; i++){
					var transaction = data[i];
					var decrypted_data = /*userCrypto.decrypt(*/JSON.parse(transaction["data"])/*)*/;
					decrypted_data.id = transaction.id;
					decrypted_data.editMode = false;
					$scope.transactions.push(decrypted_data);
				}
			}
		}).error(function(data, status, headers, config) {
			$scope.errordata = data;
		});

		$scope.createTransaction = function() {
			var now = new Date(); 
			$scope.transactions.push({
				id: -1, sender: "", receiver: "", amount: 0,
				description: "", date: now.getFullYear() + "-" + now.getMonth() + "-" + now.getDay()
				, editMode: true
			});
		}

		$scope.updateTransaction = function(t){
			$http({
			    method: 'POST',
			    url: '/search/createtransaction/',
			    data: "id=" + t.id + "&data=" + JSON.stringify(t) + "&amount_bucket=" + amountToBucket(t.amount) + "&date_bucket=" + dateToBucket(t.date),
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				t.editMode = false;
			}).error(function(data, status, headers, config) {
				$scope.errordata =  data;
			});
		}
		$scope.deleteTransaction = function(t){
			var index = $scope.transactions.indexOf(t);
			if (index > -1) {
				$scope.transactions.splice(index, 1);
			}
			$http({
			    method: 'POST',
			    url: '/search/deletetransaction/',
			    data: "id=" + t.id,
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).error(function(data, status, headers, config) {
				$scope.errordata =  data;
			});
		}
		// Checks whether any transaction is currently edited
		$scope.isEditMode = function() {
			return $scope.transactions.reduce(function(prev, curr) { return prev.editMode || curr.editMode; }, false);
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

paySafeControllers.controller('TransactionSearchCtrl', ['$scope', '$http',
	function($scope,$http) {
		$scope.search_form = search_form;
		$scope.search_form.amount.operation = $scope.search_form.amount.operations[0];
		$scope.search_form.date.operation = $scope.search_form.date.operations[0];
		amount_bucket.min = amount_bucket.map[0];
		amount_bucket.max = amount_bucket.map[amount_bucket.map.length -1];

		$scope.search_url = "";

		$scope.search = function() {
			if($scope.search_form.is_ready_for_search()) {
				$scope.search_url = $scope.search_form.generate_url();
				$scope.transactions = [];
				$http({method: 'GET', url: '/search/search/' + $scope.search_url
				}).success(function(data, status, headers, config) {
					if(data["login_successful"]==false){
						$location.path("/login");
					}
					else{
						for (i = 0; i < data.length; i++){
							var transaction = data[i];						
							var decrypted_data =/* userCrypto.decrypt(*/JSON.parse(transaction['data']) /*)*/;
							decrypted_data.id = transaction.id;
							decrypted_data.editMode = false;
							decrypted_data.update = $scope.updateTransaction;
							decrypted_data.delete = $scope.deleteTransaction;
							if($scope.search_form.is_valid_result(decrypted_data)){
								$scope.transactions.push(decrypted_data);
							}						
						}
					}
				}).error(function(data, status, headers, config) {
					$scope.errordata = data;
				});
			} else {
				$scope.transactions = [];
			}
		}
	}
]);

paySafeControllers.controller('ClientLoginCtrl', ['$scope', '$http', '$location',
	function($scope,$http,$location){
		$scope.user = { username: "", password: ""};
		$scope.successdata = "";
		$scope.errordata = "";
		$scope.login = function(){
			$scope.successdata = "";
			$scope.errordata = "";
			$http({
			    method: 'POST',
			    url: '/search/login/',
			    data: "username=" +$scope.user.username + "&password=" +$scope.user.password,
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				if(data["login_successful"]==true){
					$location.path("/");
				}
			}).error(function(data, status, headers, config) {
				
			});
		}
	}

]);
paySafeControllers.controller('ClientRegisterCtrl', ['$scope', '$http', '$location',
	function($scope,$http,$location){
		$scope.user = { username: "", password: ""};
		$scope.successdata = "";
		$scope.errordata = "";
		$scope.register = function(){
			$scope.successdata = "";
			$scope.errordata = "";
			$http({
			    method: 'POST',
			    url: '/search/register/',
			    data: "username=" +$scope.user.username + "&password=" +$scope.user.password,
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				if(data["registered_successful"]==true){
					$location.path("/login");
				}
			}).error(function(data, status, headers, config) {
				
			});
		}
	}

]);

paySafeControllers.controller('ClientLogoutCtrl', ['$scope', '$http', '$location',
	function($scope,$http,$location){
		
		$http({method: 'GET', url: '/search/logout/'
		}).success(function(data, status, headers, config) {
			$location.path("/login");
		}).error(function(data, status, headers, config) {
			$location.path("/login");
		});
		}

]);