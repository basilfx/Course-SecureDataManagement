// Configuratie app
var paySafeApp = angular.module('paySafeApp', [
	'ngRoute',
	'paySafeControllers'
]);

// Routes
paySafeApp.config(['$routeProvider',
	function($routeProvider) {
		$routeProvider.
			when('/', {
				templateUrl: 'partials/transaction-list.html',
				controller: 'TransactionListCtrl'
			}).
			otherwise({
				redirectTo: '/'
			});

	}
])