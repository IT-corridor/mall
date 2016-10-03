angular.module('chat.controllers', ['chat.services', 'ngCookies'])
    .controller('CtrlChat', ['$scope', '$rootScope', '$http', '$cookies',
        '$location', '$route', '$window', 'Quickblox',
        function ($scope, $rootScope, $http, $cookies, $location, $route, $window, Quickblox) {
            var CONFIG = {
                debug: {mode: 1}
            };
            $rootScope.title = 'CHAT Yo-hoo';
            Quickblox.connect();

            var dialogs_p = Quickblox.get_dialogs();

            dialogs_p.then(function(result){
                $scope.dialogs = result;
            });

            $scope.destroy_session = function(){
                Quickblox.disconnect();
            }


            $scope.users = [];
            $scope.contacts = Quickblox.contacts;
            $scope.subscribers = Quickblox.subscribers;

            $scope.get_users = function(){
                var promise = Quickblox.get_users();
                promise.then(function(success){
                    $scope.users = success;
                });
            };
            $scope.subscribe = function(user_id){
                Quickblox.roster.add_user(user_id);
            };
            $scope.unsubscribe = function(user){
                Quickblox.roster.remove_user(user);
            };

            $scope.confirm_subscription = function(user){
                Quickblox.roster.confirm_user(user);
            };
        }
    ]);