var global = {
	privateKey: "",
	crypto: undefined,
	clientId: undefined,
	clientName: ""
};
/**
 * This function ask the user whether he realy meant to refresh the page.
 * Instance variables are lost at refresh, such as the asymetric key, 
 * therefore a user has to login after refresh.
 */
window.onbeforeunload = function (e) {
    e = e || window.event;

    // Don't confirm when not required
    if (!global.clientId) {
        return;
    }

    // For others
    return "When you confirm reloading, you will log out.";
};
/**
 * Checks if the user is correctly logged in, redirects to login if he is not.
*/
function checkUser(loc) {
	if(!global.clientId || !global.crypto) loc.path("/login");
}

/**
 * Decrypts the symmetric key of the client with the private key of the consultant.
*/
function decryptClientKey(encKeyHexStr) {
    var encKey = encKeyHexStr;
    var rsa = new RSAKey();
    var p = global.privateKey.split("|");
    rsa.setPrivateEx(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7]);
    var res = rsa.decrypt(encKey);
    return res;
}

var paySafeControllers = angular.module('paySafeApp.controllers', []);

/**
 * Transaction List Controller
 * This controller handles the listing, creating and updating of transactions.
 * It fetches transactions from the database, and pushes changes to the database whenever needed.
*/
paySafeControllers.controller('TransactionListCtrl', ['$scope', '$http', '$location',
    function($scope,$http, $location) {
    	checkUser($location);

    	$scope.isConsultant  = global.privateKey.length > 0;
    	$scope.clientName = global.clientName;

        $scope.transactions = [];
        $scope.testdata = "";
        $scope.errordata = "";

        $http({method: 'GET', url: '/transactions/?client_id=' + global.clientId
        }).success(function(data, status, headers, config) {
			checkUser($location);
            if(data["login_successful"] == false){
                $location.path("/login");
            }
            else{
                for (i = 0; i < data.length; i++){
                    var transaction = data[i];
                    var decrypted_data = global.crypto.decrypt(transaction["data"]);
                    if (decrypted_data){
                        decrypted_data.id = transaction.id;
                        decrypted_data.editMode = false;
                        $scope.transactions.push(decrypted_data);
                    }
                }
            }
        }).error(function(data, status, headers, config) {
            $scope.errordata = data;
        });

        $scope.createTransaction = function() {
            var now = new Date();
            $scope.transactions.push({
                id: -1, sender: "", receiver: "", amount: "",
                description: "", date: now.getFullYear() + "-" + now.getMonth() + "-" + now.getDay()
                , editMode: true
            });
        }

        $scope.updateTransaction = function(t){
            var temp = {sender:t.sender, receiver:t.receiver, amount:t.amount, date:t.date, id: t.id, description:t.description};
            $http({
                method: 'POST',
                url: '/transactions/create/',
                data: "client_id=" + global.clientId + "&id=" + t.id + "&data=" + global.crypto.encrypt(temp) + "&amount_bucket=" + amountToBucket(t.amount) + "&date_bucket=" + dateToBucket(t.date),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(data, status, headers, config) {
                t.editMode = false;
                t.id = parseInt(data["id"]);
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
                data: "id=" + t.id + "&client_id=" + global.clientId,
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
/**
 * Client List Controller
 * Generates a list of clients for the logged in Consultant. 
 * This allows the consultant to switch to a specific client and view, update and search their transactions.
*/
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
                    client.switch = function(){
                        global.clientId = this.id;
                        global.crypto = new Crypto(decryptClientKey(this.sym_key_cons));
                        global.clientName = this.name;
                        $location.path("/transactions");
                    }

                    $scope.clients.push(client);
                }
            }
        }).error(function(data, status, headers, config) {
            $scope.errordata = data;
        });
    }
]);
/**
 * Transaction Searhc Controller
 * This controller converts a search query into bucket values and sends these values to the server.
 * The response is filtered to match the search query and displayed to the user.
*/
paySafeControllers.controller('TransactionSearchCtrl', ['$scope', '$http','$rootScope', '$location',
    function($scope,$http,$rootScope,$location) {
    	checkUser($location);

    	$scope.isConsultant  = global.privateKey.length > 0;
    	$scope.clientName = global.clientName;

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
                $http({method: 'GET', url: '/search/' + $scope.search_url + '&client_id=' + global.clientId
                }).success(function(data, status, headers, config) {
                    if(data["login_successful"]==false){
                        $location.path("/login");
                    }
                    else{
                        for (i = 0; i < data.length; i++){
                            var transaction = data[i];
                            var decrypted_data = global.crypto.decrypt(transaction['data']);
                            if (decrypted_data){
                                decrypted_data.id = transaction.id;
                                decrypted_data.editMode = false;
                                decrypted_data.update = $scope.updateTransaction;
                                decrypted_data.delete = $scope.deleteTransaction;
                                if($scope.search_form.is_valid_result(decrypted_data)){
                                    $scope.transactions.push(decrypted_data);
                                }
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
/**
 * Login Controller
 * Sends the username + hashed password to the server, switches to transactions if server returns "login_sucessful"
*/
paySafeControllers.controller('LoginCtrl', ['$scope', '$http', '$location',
	function($scope,$http,$location){
		$scope.user = { username: "", password: ""};
		$scope.isConsultant = false;

		$scope.successdata = "";
		$scope.errordata = "";
		$scope.login = function(){
			$scope.successdata = "";
			$scope.errordata = "";
			var url = $scope.isConsultant ? "/consultant-login/" : "/client-login/";
			console.log(CryptoJS.SHA3($scope.user.password));
			$http({
			    method: 'POST',
			    url: url,
			    data: "username=" +$scope.user.username + "&password=" + CryptoJS.SHA3($scope.user.password),
			    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
			}).success(function(data, status, headers, config) {
				if(data["login_successful"]==true){
					if($scope.isConsultant) {
						global.privateKey = $scope.privKey;
						global.clientName = data["client_name"];
						global.crypto = new Crypto(decryptClientKey(data["client_key"]));
					} else {
						global.crypto = new Crypto(CryptoJS.SHA3($scope.user.username + $scope.user.password).toString());
					} 
					global.clientId = parseInt(data["client_id"]);

					$location.path("/");
				}
			}).error(function(data, status, headers, config) {
				$scope.loginFailed = true;
			});
		}
	}
]);
/**
 * Client Register Controller
 * Shows a list of consultants to the new client.
 * Sends the username, hashed password, and aes-key encrypted with the public key of the selected consultant.
 * Redirects to login if registered successfully.
*/
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
        });


        $scope.register = function(){
        	// First hash and then encrypt the symmetric key
            var hashed_key = CryptoJS.SHA3($scope.user.username + $scope.user.password).toString();
            var rsa = new RSAKey();
            rsa.setPublic($scope.consultant.public_mod, $scope.consultant.public_exp);
            var encrypted_key = rsa.encrypt(hashed_key);
   			console.log(encrypted_key);

            $http({
                method: 'POST',
                url: '/client-register/',
                data: "username=" +$scope.user.username + "&password=" + CryptoJS.SHA3($scope.user.password) + "&consultant_id=" + $scope.consultant.id + "&key=" + encrypted_key,
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).success(function(data, status, headers, config) {
                if(data["registered_successful"]==true){
                    $location.path("/login");
                }
            }).error(function(data, status, headers, config) {
            	$scope.registerFailed = true;
        	});
        }
    }

]);
/**
 * Logout Controller
 * Logs the current user out.
*/
paySafeControllers.controller('LogoutCtrl', ['$scope', '$http', '$location',
    function($scope,$http,$location){
    	global.privateKey = "";
    	global.clientId = undefined;
    	global.crypto = undefined;
    	global.clientName = "";
    	
        $http({method: 'GET', url: '/logout/'
        }).success(function(data, status, headers, config) {
            $location.path("/login");
        }).error(function(data, status, headers, config) {
            $location.path("/login");
        });
        }
]);
/**
 * Consultant Register Controller
 * Allows the new consultant to generate a RSA key pair and
 * sends the public key, username and hashed password to the server.
 * They private key is displayed, which the consultant has to store.
*/
paySafeControllers.controller('ConsultantRegisterCtrl', ['$scope','$http','$location',
	function($scope, $http, $location) {
		$scope.isGenerated = false;
		$scope.user = { username: "", password: "" }

		$scope.generateKey = function() {
			var rsa = new RSAKey();
			rsa.generate(2048, '10001');
			console.log(rsa);
			$scope.pubExp = rsa.e.toString(16);
			$scope.pubMod = rsa.n.toString(16);
			console.log($scope.pubMod);
			$scope.privKey = [
								rsa.n.toString(16), rsa.e.toString(16), rsa.d.toString(16), rsa.p.toString(16),
						      	rsa.q.toString(16), rsa.dmp1.toString(16), rsa.dmq1.toString(16), rsa.coeff.toString(16)
						      ].join("|");
			$scope.isGenerated = true;
		}

		$scope.register = function() {
			$http({
                method: 'POST',
                url: '/consultant-register/',
                data: "username=" +$scope.user.username + "&password=" + CryptoJS.SHA3($scope.user.password) + "&public_exp=" + $scope.pubExp + "&public_mod=" + $scope.pubMod,
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
