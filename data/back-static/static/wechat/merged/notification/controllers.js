angular.module('notification.controllers', ['notification.services'])
    .controller('CtrlNotification', ['$scope', '$rootScope', '$http', '$cookies',
        '$location', '$route', 'Notification',
        function ($scope, $rootScope, $http, $cookies, $location, $route, Notification) {
            $rootScope.title = 'Notification page';
            $scope.background_color = function(type) {
                if (type == 'success')
                    return '#5cb85c';
                else
                    return '#ec971f';
            }
        }
    ]);