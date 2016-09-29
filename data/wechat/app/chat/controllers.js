angular.module('chat.controllers', ['chat.services', 'ngCookies'])
    .controller('CtrlChat', ['$scope', '$rootScope', '$http', '$cookies',
        '$location', '$route', '$window', 'Chat',
        function ($scope, $rootScope, $http, $cookies, $location, $route, $window, Chat) {
            var CONFIG = {
                debug: {mode: 1}
            };
            $rootScope.title = 'CHAT Yo-hoo';
            $scope.credentials = Chat.create_session(function(success){
                QB.init(success.token, success.app_id, CONFIG);
            });

            $scope.destroy_session = function(){
                Chat.destroy_session({'token': $scope.credentials.token});
            }
        }
    ]);