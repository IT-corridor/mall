angular.module('user.controllers', ['user.services', 'auth.services'])
.controller('CtrlProfile', ['$scope', '$rootScope','$http',
'$location', '$translate', '$route', 'User', 'MultipartForm',
    function($scope, $rootScope, $http, $location, $translate, $route, User,
    MultipartForm) {

        $scope.wait = false;
        $scope.me = User.me();
        $scope.random = Math.floor((Math.random()*1000));
        $scope.sync_profile = function(){

            /* TODO: implement connecting weixin account
            to our visitors profile */
        };

        $scope.update_profile = function(){
        var data = {
            username: $scope.me.username,
            phone: $scope.me.phone,
            email: $scope.email
        };
            User.edit(data, function(success){
                $scope.me = success;
                $translate('SUCCESS').then(function (msg) {
                    $rootScope.alerts.push({ type: 'success', msg:  msg});
                });
            });
        };

        $scope.update_avatar = function(){

            if( document.getElementById("avatar").files.length > 0){
                $scope.wait = true;
                var url = '/visitor/profile/edit/';
                MultipartForm('PATCH', '#avatar_form', url).then(function(response) {
                        $scope.random = Math.floor((Math.random()*1000));
                        $scope.me = response.data;
                        clear_input();
                        $scope.wait = false;
                    },
                    function(error) {
                        $scope.wait = false;
                        $scope.error = error.data;
                    }
                );
            }

        };

        function clear_input(){
            var input = document.querySelector("#avatar");
            angular.element(input).val(null);
        }
    }
])
.controller('CtrlChangePassword', ['$scope', '$rootScope','$http',
'$location', '$translate', '$route', 'User',
    function($scope, $rootScope, $http, $location, $translate, $route, User) {

        User.me();

        $scope.wait = false;
        $scope.data = {};
        $scope.change_password = function(){
            $scope.wait = true;
            User.change_password($scope.data, function(success){
                    $translate('SUCCESS').then(function (msg) {
                        $rootScope.alerts.push({ type: 'success', msg:  msg});
                    });
                    $location.path('/me');
                },
                function(error){
                    $scope.wait = false;
                    $scope.error = error.data;
                }
            );
        };
    }

])
.controller('CtrlWechatSetPassword', ['$scope', '$rootScope','$http',
'$location', '$translate', '$route', 'User',
    function($scope, $rootScope, $http, $location, $translate, $route, User) {

        $scope.wait = false;
        $scope.step = 0;
        $scope.data = {};
        $scope.set_password = function(){
            if ($scope.step == 2){
                $scope.wait = true;
                User.wechat_phone($scope.data, function(success){
                        $translate('SUCCESS').then(function (msg) {
                            console.log('hello');
                            $rootScope.alerts.push({ type: 'success', msg:  msg});
                        });
                        $scope.wait = false;
                        $location.path('/me');
                    },
                    function(error){
                        $scope.wait = false;
                        $scope.error = error.data;
                    }
                );
            }
        };

        $scope.send_code = function(phone){
            /* Sends a random code to the phone */
            if ($scope.step == 0){
                $scope.wait = true;
                User.send_code({phone: phone}, function(success){
                    $scope.step = 1;
                    $scope.wait = false;
                },
                error_handler);
            }
        };

        $scope.verify_code = function(code){
            /* Send code to compare on the backend side */
            if ($scope.step == 1){
                $scope.wait = true;
                User.verify_code({code: code}, function(success){
                    $scope.step = 2;
                    $scope.wait = false;
                },
                error_handler);
            }

        };

        function error_handler (error) {
            if (error.data instanceof Object){
                $scope.error = error.data;
            }
            else{
                $translate('ERROR').then(function (msg) {
                    $scope.detail = msg;
                });
            }
            $scope.wait = false;
        }
    }

]);