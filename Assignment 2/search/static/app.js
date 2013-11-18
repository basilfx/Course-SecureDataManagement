// Configuratie app
var paySafeApp = angular.module('paySafeApp', [
	'ngRoute', '$strap.directives', 
	'paySafeControllers'
]);

// Routes
paySafeApp.config(['$routeProvider',
	function($routeProvider, $routeParams) {
		$routeProvider.
			when('/', {
				templateUrl: 'partials/transaction-list.html',
				controller: 'TransactionListCtrl'
			}).
			when('/show/:id/', {
				templateUrl: 'partials/transaction_show.html',
				controller: 'TransactionShowCtrl'
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
			otherwise({
				redirectTo: '/'
			});

	}
])