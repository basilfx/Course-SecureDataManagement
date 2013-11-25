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
				templateUrl: 'partials/transaction-list.html',
				controller: 'TransactionListCtrl'
			}).
			when('/search', {
				templateUrl: 'partials/transaction_search.html',
				controller: 'TransactionSearchCtrl'
			}).
			when('/login',{
				templateUrl: 'partials/client_login.html',
				controller: 'ClientLoginCtrl'
			}).
			when('/register',{
				templateUrl: 'partials/client_register.html',
				controller: 'ClientRegisterCtrl'
			}).
			when('/register-consultant', {
				templateUrl: 'partials/consultant_register.html',
				controller: 'ConsultantRegisterCtrl'
			}).
			when('/logout',{
				templateUrl: 'partials/client_login.html',
				controller: 'ClientLogoutCtrl'
			}).
			otherwise({
				redirectTo: '/'
			});

	}
]);
