angular.module('common.controllers', ['auth.services', 'ngCookies'])
.controller('CtrlHome', ['$scope', '$rootScope','$http', '$cookies',
'$location', '$route', '$window', 'Auth', 'Logout',
    function($scope, $rootScope, $http, $cookies, $location, $route, $window, Auth, Logout) {

        $rootScope.title = 'The First Page';

    }
])
.controller('CtrlChat', ['$scope',
    function($scope) {
        if (chat_initialized) {
            // load chat dialogs
            retrieveChatDialogs();
            $scope.$apply();
        }
    }
]);
