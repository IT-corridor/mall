angular.module('common.controllers', ['auth.services', 'ngCookies'])
    .controller('CtrlDummy', ['$scope', '$rootScope', '$http', '$cookies',
        '$location', '$route', '$window', 'Auth', 'Logout', 'WXI',
        function ($scope, $rootScope, $http, $cookies, $location, $route, $window, Auth, Logout, WXI) {

            $rootScope.title = 'Dummy page';

            var promise = WXI.get_location();
            promise.then(function (success) {
                $scope.lat = success.latitude;
                $scope.lon = success.longitude;
            });

            $scope.logout = function () {
                $scope.r = Logout.query(function (r) {
                    $rootScope.alerts.push({type: 'info', msg: 'Good by.'});
                    $route.reload();
                });
            };
        }
    ]);