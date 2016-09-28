var navbar = angular.module('navbar', ['auth.services'])
    .directive('dNavbar', ['$window', '$location', '$routeParams', '$translate', 'PATH', 'Auth', '$uibModal',
        function ($window, $location, $routeParams, $translate, PATH, Auth, $uibModal) {
            return {
                restrict: 'A',
                templateUrl: PATH + 'partials/navbar/templates/navbar_d.html',
                controller: function ($scope, $rootScope, $window, $location, $routeParams,
                                      $translate, PATH, Auth) {
                    $rootScope.visitor_resolved = false;
                    $scope.brand_text = 'ATYICHU';
                    $scope.p = $routeParams;
                    var auth_promise = Auth.is_authenticated();

                    auth_promise.then(function (result) {
                        if (!result.is_authenticated) {

                            $translate('AUTHENTICATION.REQUIRED').then(function (msg) {
                                $rootScope.alerts.push({type: 'danger', msg: msg});
                            });

                        }
                        else {
                            // Visitor means Vendor here!
                            // User instance logic migrated to the Auth factory
                            // This action should set $rootScope.visitor
                            Auth.get_user();
                        }
                    });

                    $rootScope.$on("$routeChangeStart", function (event, next, current) {
                        $scope.isCollapsed = false;
                    });

                    $scope.logout = function () {
                        Auth.logout();
                    }

                    $scope.animationsEnabled = true;

                    $scope.open = function () {

                        var modalInstance = $uibModal.open({
                            animation: $scope.animationsEnabled,
                            templateUrl: PATH + 'partials/navbar/templates/modal.html',
                            controller: 'ModalInstanceCtrl',
                            size: 'sm',
                        });

                        modalInstance.result.then(function (auth) {
                            //$rootScope.alerts.push({ type: 'info', msg: 'Welcome, ' + auth.username + '!'});
                        });
                    }
                    $scope.toggleAnimation = function () {
                        $scope.animationsEnabled = !$scope.animationsEnabled;
                    };

                    $scope.search = function (keyEvent) {
                        //search
                        if (keyEvent.which == 13) {
                            $scope.search_c();
                        }
                    };

                    $scope.search_c = function () {
                        if ($scope.p.q) {
                            $location.path('/photo/search').search({q: $scope.p.q});
                        }
                    };
                }
            };
        }]);

navbar.controller('ModalInstanceCtrl', ['$scope', '$rootScope', '$uibModalInstance', 'Login', 'Auth', '$window', '$http', 'API', 
    function ($scope, $rootScope, $uibModalInstance, Login, Auth, $window, $http, API) {

        $scope.authenticate = function (u, p) {
            var promise = Auth.login(u, p);

            promise.then(
                function (success) {
                    $rootScope.visitor = success;
                    $rootScope.visitor_resolved = true;
                    $scope.error = null;
                    Auth.set(success);
                    $uibModalInstance.close(Auth);

                    // configuration for chat and notification
                    $window.currentUser = {
                        login: '0' + success.pk,
                        pass: 'atyichu@3212',
                        full_name: success.brand_name
                    };
                    connectToChat(currentUser);

                    var pusher = new Pusher('4c8e6d909a1f7ccc44ed');
                    var notificationsChannel = pusher.subscribe('nf_channel_' + success.pk);

                    $rootScope.notifications = success.notifications;

                    notificationsChannel.bind('new_notification', function (notification) {
                        // show notification toaster
                        var message = notification.message;
                        if (notification.type == 'success')
                            toastr.success(message);
                        else if (notification.type == 'warning')
                            toastr.warning(message);
                        else if (notification.type == 'chat_request') {
                            message = message.split('@');

                            var r = confirm(message[0]);
                            if (r == true) {
                                var user_id = message[1];
                                $http.post(API+'api/v1/notification/', {
                                    type: 'chat_reply',
                                    message: $rootScope.visitor.brand_name + ' accepts your request!@0' + $rootScope.visitor.pk,
                                    user_id: user_id,
                                });
                            }
                            // set the notification read
                        } else if (notification.type == 'chat_reply') {
                            message = message.split('@');
                            alert(message[0]);
                            var user_id = message[1];
                            var dialogName = message[0].split(' accepts');
                            // create the dialog
                            createNewDialog_real(user_id, dialogName[0]);
                        }

                        $rootScope.notifications.unshift(notification);
                    });
                },
                function (error) {
                    $scope.error = error.data.error;
                }
            );
        }
        $scope.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        }
    }]);