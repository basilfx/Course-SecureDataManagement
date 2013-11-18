var paySafeControllers = angular.module('paySafeControllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope', '$http', '$location','$sce',
	function($scope,$http, $location,$sce) {
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

					
					var decrypted_data = decrypt(transaction["data"]);
					decrypted_data.id = transaction.id;
					decrypted_data.editMode = false;
					decrypted_data.update = $scope.updateTransaction;
					decrypted_data.delete = $scope.deleteTransaction;
					console.log(decrypted_data);
					$scope.transactions.push(decrypted_data);
				}
			}
		}).error(function(data, status, headers, config) {
			$scope.errordata = data;
		});

		$scope.createTransaction = function() {
			$scope.transactions.push({
				id: -1, sender: "", receiver: "", amount: 0,
				description: "", date: "", editMode: true, update: $scope.updateTransaction , delete: $scope.deleteTransaction
			});
		}

		$scope.updateTransaction = function(t){
			t.editMode = false;
			$http({
			    method: 'POST',
			    url: '/search/createtransaction/',
			    data: "id=" + t.id + "&data=" + encryptTransaction(t) + "&amount_bucket=" + amount_bucket.value(t.amount) + "&date_bucket=" + date_bucket.value(t.date),
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				$scope.testdata =  $sce.trusted(data);
			}).error(function(data, status, headers, config) {
				$scope.errordata =  $sce.trusted(data);
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
			}).success(function(data, status, headers, config) {
				$scope.testdata =  $sce.trusted(data);
			}).error(function(data, status, headers, config) {
				$scope.errordata =  $sce.trusted(data);
			});
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
		amount_bucket.min = amount_bucket.bucket_list[0];
		amount_bucket.max = amount_bucket.bucket_list[amount_bucket.bucket_list.length -1];
		date_bucket.min = date_bucket.bucket_list[0];
		date_bucket.max = date_bucket.bucket_list[date_bucket.bucket_list.length -1];

		$scope.search_url = "";
		$scope.search = function() {
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
						var decrypted_data = decrypt(transaction["data"]);
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
			$scope.show_table = true;
		};
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