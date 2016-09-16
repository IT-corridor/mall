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
                    //$rootScope.alerts.push({ type: 'info', msg: 'Welcome, ' + auth.username + '!'});
                });
            };
        }
    };
}]);

user.controller('LoginInstanceCtrl', ['$scope','$rootScope', '$translate', '$uibModalInstance' , 'User',
                                        function ($scope, $rootScope, $translate, $uibModalInstance, User) {

    $scope.data = {};
    $scope.data_two = {};
    $scope.sent = false;

    $scope.auth_step_one = function(){
        User.login_start($scope.data,
            function(success){
                //$uibModalInstance.close(success);
                $scope.sent = true;
            },
            function(error){
                if (error.data instanceof Array){
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

    $scope.auth_step_two = function(){
        if ($scope.sent){
            console.log($scope.data_two);
            User.login_end($scope.data_two,
                function(success){
                    $uibModalInstance.close(success);
                },
                function(error){
                    if (error.data instanceof Array){
                        $scope.error = error.data;
                    }
                    else{
                        $translate('AUTHENTICATION.ERROR').then(function (msg) {
                            $scope.detail = msg;
                        });
                    }
                }
            );
        }
    };

    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    }
}]);

user.controller('RegInstanceCtrl', ['$scope','$rootScope', '$translate', '$uibModalInstance' , 'MultipartForm',
                                        function ($scope, $rootScope, $translate, $uibModalInstance, MultipartForm) {
    $scope.wait = false;
    $scope.authenticate = function(phone, password){
        $scope.wait = true;
        var url = '/visitor/profile/';
        MultipartForm('POST', '#reg_form', url).then(function(response) {
                $uibModalInstance.close(response.data);
                $scope.wait = false;
            },
            function(error) {
                if (error.data instanceof Object){
                    $scope.error = error.data;
                }
                else{
                    $translate('AUTHENTICATION.ERROR').then(function (msg) {
                        $scope.detail = msg;
                    });
                }
                $scope.wait = false;
            }
        );
    }
    $scope.cancel = function () {
        $uibModalInstance.dismiss('cancel');
    }
}]);