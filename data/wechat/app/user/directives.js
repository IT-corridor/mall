var user = angular.module('user.directives', ['user.services', 'auth.services', 'common.services'])
.directive('userSign', ['$window', '$location', '$routeParams', '$translate', 'PATH', 'User', 'Auth', '$uibModal',
                        function($window, $location, $routeParams, $translate, PATH, User, Auth, $uibModal) {
    return {
        restrict: 'A',
        templateUrl: PATH + 'user/templates/bar.html',
        controller: function($scope, $rootScope, $window, $location, $routeParams,
            $translate, PATH, Auth ){
            $scope.p = $routeParams;


            $scope.animationsEnabled = true;

            $scope.open_login = function () {

                var modalInstance = $uibModal.open({
                    animation: true,
                    templateUrl: PATH + 'user/templates/modal-login.html',
                    controller: 'LoginInstanceCtrl',
                    size: 'sm',
                });

                modalInstance.result.then(function (success) {
                    Auth.set(success);
                    $rootScope.visitor_resolved = true;
                    $rootScope.visitor = success;
                    //$rootScope.alerts.push({ type: 'info', msg: 'Welcome, ' + auth.username + '!'});
                });
            };

            $scope.open_reg = function () {

                var modalInstance = $uibModal.open({
                    animation: true,
                    templateUrl: PATH + 'user/templates/modal-reg.html',
                    controller: 'RegInstanceCtrl',
                });

                modalInstance.result.then(function (success) {
                    Auth.set(success);
                    $rootScope.visitor_resolved = true;
                    $rootScope.visitor = success;
                });
            };
            $scope.open_reset = function(){
                var modalInstance = $uibModal.open({
                    animation: true,
                    templateUrl: PATH + 'user/templates/modal-reset.html',
                    controller: 'ResetPasswordCtrl',
                });

                modalInstance.result.then(function (success) {
                    console.log(success);
                });

            };
        }
    };
}]);

user.controller('LoginInstanceCtrl', ['$scope','$rootScope', '$translate', '$uibModalInstance' , 'User',
                                        function ($scope, $rootScope, $translate, $uibModalInstance, User) {

    $scope.data = {};

    $scope.authenticate = function(){
        /* Simple one-step auth.*/
        User.login($scope.data,
            function(success){
                $uibModalInstance.close(success);
            },
            function(error){
                if (error.data instanceof Object){
                    $scope.error = error.data;
                }
                else{
                    $translate('AUTHENTICATION.ERROR').then(function (msg) {
                        $scope.detail = msg;
                    });
                }
            }
        );
    };



    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    }
}]);

user.controller('RegInstanceCtrl', ['$scope','$rootScope', '$translate', '$uibModalInstance' , 'MultipartForm', 'User',
                                        function ($scope, $rootScope, $translate, $uibModalInstance, MultipartForm, User) {
    $scope.wait = false;
    $scope.step = 0;

    $scope.register = function(){
        if ($scope.step == 2){
            $scope.wait = true;
            var url = '/visitor/profile/';
            MultipartForm('POST', '#reg_form', url).then(function(response) {
                    $uibModalInstance.close(response.data);
                    $scope.wait = false;
                },
                error_handler
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

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
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
}])
user.controller('ResetPasswordCtrl', ['$scope','$rootScope', '$translate', '$uibModalInstance' , 'User',
                                        function ($scope, $rootScope, $translate, $uibModalInstance, User) {
    $scope.wait = false;
    $scope.step = 0;
    $scope.data = {};
    $scope.reset_password = function(){
        if ($scope.step == 2){
            $scope.wait = true;
            User.reset_password($scope.data, function(success){
                    $scope.wait = false;
                    $translate('SUCCESS').then(function (msg) {
                        $rootScope.alerts.push({ type: 'success', msg:  msg});
                        $uibModalInstance.close(msg);
                    });
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
            User.send_code({phone: phone, is_exists: true}, function(success){
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

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
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
}]);