// Configuratie app
var paySafeApp = angular.module('paySafeApp', [
	'ngRoute', '$strap.directives', 
	'paySafeApp.controllers'
]);

// Routes
paySafeApp.config(['$routeProvider',
	function($routeProvider, $routeParams) {
		$routeProvider.
			when('/', {
				templateUrl: staticUrl + 'partials/transaction-list.html',
				controller: 'TransactionListCtrl'
			}).
			when('/search', {
				templateUrl: staticUrl + 'partials/transaction_search.html',
				controller: 'TransactionSearchCtrl'
			}).
			when('/login',{
				templateUrl: staticUrl + 'partials/login.html',
				controller: 'LoginCtrl'
			}).
			when('/register',{
				templateUrl: staticUrl + 'partials/client_register.html',
				controller: 'ClientRegisterCtrl'
			}).
			when('/register-consultant', {
				templateUrl: staticUrl + 'partials/consultant_register.html',
				controller: 'ConsultantRegisterCtrl'
			}).
			when('/clients',{
				templateUrl: staticUrl + 'partials/client_list.html',
				controller: 'ClientListCtrl'
			}).
			when('/logout',{
				templateUrl: staticUrl + 'partials/login.html',
				controller: 'LogoutCtrl'
			}).
			otherwise({
				redirectTo: '/'
			});
	}
]);