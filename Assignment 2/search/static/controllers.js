var global = {
	privateKey: "",
	crypto: undefined,
	userId: undefined
};

function checkUser(loc) {
	if(!global.userId || !global.crypto) loc.path("/login");
}

var paySafeControllers = angular.module('paySafeApp.controllers', []);

paySafeControllers.controller('TransactionListCtrl', ['$scope', '$http', '$location',
    function($scope,$http, $location) {
    	checkUser($location);

        $scope.transactions = [];
        $scope.testdata = "";
        $scope.errordata = "";

        $http({method: 'GET', url: '/transactions/'
        }).success(function(data, status, headers, config) {
			checkUser($location);
            if(data["login_successful"] == false){
                $location.path("/login");
            }
            else{
                for (i = 0; i < data.length; i++){
                    var transaction = data[i];
                    console.log("trans");
                    console.log(transaction["data"]);
                    var decrypted_data = global.crypto.decrypt(transaction["data"]);
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
            var temp = {sender:t.sender, receiver:t.receiver, amount:t.amount, date:t.date, id: t.id};
            console.log("update");
            console.log(global.crypto.encrypt(temp));
            $http({
                method: 'POST',
                url: '/transactions/create/',
                data: "id=" + t.id + "&data=" + global.crypto.encrypt(temp) + "&amount_bucket=" + amountToBucket(t.amount) + "&date_bucket=" + dateToBucket(t.date),
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
                url: '/transactions/delete/',
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

paySafeControllers.controller('ClientListCtrl', ['$scope', '$http', '$location',
    function($scope,$http, $location) {
    	checkUser($location);

        $scope.clients = [];
        $scope.testdata = "";
        $scope.errordata = "";

        $http({method: 'GET', url: '/clientlist/'
        }).success(function(data, status, headers, config) {
            if(data["login_successful"] == false){
                $location.path("/login");
            }
            else{
                for (i = 0; i < data.length; i++){
                    var client = data[i];
                    client.view_transactions = function(){
                        //TODO
                    }
                    $scope.clients.push(client);
                }
            }
        }).error(function(data, status, headers, config) {
            $scope.errordata = data;
        });
    }
]);

paySafeControllers.controller('TransactionSearchCtrl', ['$scope', '$http','$rootScope', '$location',
    function($scope,$http,$rootScope,$location) {
    	checkUser($location);

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
                $http({method: 'GET', url: '/search/' + $scope.search_url
                }).success(function(data, status, headers, config) {
                    if(data["login_successful"]==false){
                        $location.path("/login");
                    }
                    else{
                        for (i = 0; i < data.length; i++){
                            var transaction = data[i];
                            var decrypted_data = global.crypto.decrypt(transaction['data']);
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
		$scope.isConsultant = false;

		$scope.successdata = "";
		$scope.errordata = "";
		$scope.login = function(){
			$scope.successdata = "";
			$scope.errordata = "";
			var url = $scope.isConsultant ? "/consultant-login/" : "/client-login/";
			$http({
			    method: 'POST',
			    url: url,
			    data: "username=" +$scope.user.username + "&password=" +$scope.user.password,
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				if(data["login_successful"]==true){
					if($scope.isConsultant) {
						global.privateKey = $scope.privKey;
					} else {
						global.userId = 1;
						global.crypto = new Crypto(CryptoJS.SHA3($scope.password).toString());
					}

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
        $scope.consultants = [];
        $http({method: 'GET', url: '/consultants/'
        }).success(function(data, status, headers, config) {
            for (i = 0; i < data.length; i++){
                var consultant = data[i];
                $scope.consultants.push(consultant);
            }
            $scope.consultant = $scope.consultants[0];    
        }).error(function(data, status, headers, config) {
            $scope.errordata = data;
        });


        $scope.register = function(){
        	// First hash and then encrypt the symmetric key
            var hashed_key = CryptoJS.SHA3($scope.user.password);
            var rsa = new RSAKey();
            rsa.setPublic($scope.consultant.public_mod, $scope.consultant.public_exp);
            var encrypted_key = rsa.encrypt(hashed_key);

            $http({
                method: 'POST',
                url: '/client-register/',
                data: "username=" +$scope.user.username + "&password=" +$scope.user.password + "&consultant_id=" + $scope.consultant.id + "&key=" + encrypted_key,
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

        $http({method: 'GET', url: '/logout/'
        }).success(function(data, status, headers, config) {
            $location.path("/login");
        }).error(function(data, status, headers, config) {
            $location.path("/login");
        });
        }

]);

paySafeControllers.controller('ConsultantRegisterCtrl', ['$scope','$http','$location',
	function($scope, $http, $location) {
		$scope.isGenerated = false;
		$scope.user = { username: "", password: "" }

		$scope.generateKey = function() {
			var rsa = new RSAKey();
			rsa.generate(2048, '10001');
			$scope.pubExp = rsa.e.toString(16);
			$scope.pubMod = rsa.n.toString(16);
			$scope.privKey = rsa.d.toString(16);
			$scope.isGenerated = true;
		}

		$scope.register = function() {
			$http({
                method: 'POST',
                url: '/consultant-register/',
                data: "username=" +$scope.user.username + "&password=" +$scope.user.password + "&public_exp=" + $scope.pubExp + "&public_mod=" + $scope.pubMod,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(data, status, headers, config) {
                if(data["registered_successful"]==true){
                    $location.path("/login");
                }
            }).error(function(data, status, headers, config) {

            });
		}
		
	}
])
