angular.module('chat.controllers', ['chat.services', 'ngCookies'])
    .controller('CtrlChat', ['$scope', '$rootScope', '$http', '$cookies',
        '$location', '$route', '$window', 'Quickblox',
        function ($scope, $rootScope, $http, $cookies, $location, $route, $window, Quickblox) {
            var CONFIG = {
                debug: {mode: 1}
            };
            $rootScope.title = 'CHAT Yo-hoo';
            Quickblox.create_session();

            $scope.destroy_session = function(){
                Chat.destroy_session({'token': $scope.credentials.token});
            }
        }
    ]);