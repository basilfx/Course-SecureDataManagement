// Configuratie app
var sdmApp = angular.module('sdmApp', []);

// Routes
sdmApp.config(['$routeProvider',
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