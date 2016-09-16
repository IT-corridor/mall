angular.module('mirror.controllers', ['mirror.services'])
.controller('CtrlMirrorList', ['$scope', '$rootScope', '$http',
'$location', 'Auth', 'Mirror', 'MirrorUnlock', 'WXI',
    function($scope, $rootScope, $http, $location, Auth, Mirror, MirrorUnlock, WXI) {
        $rootScope.title = 'Mirror List';
        $rootScope.alerts.push({ type: 'info', msg: 'You  view mirror list!' });

        var promise = WXI.get_location();

        promise.then(function(result){
            $scope.mirrors = Mirror.query(result,
                function(success){
                    $rootScope.alerts.push({ type: 'info',
                        msg: 'Mirror list successfully fetched.'});
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger',
                        msg: error.data.error});
                }
            );
        });

        $scope.unlock = function(){
            MirrorUnlock.post(function(success){
                    $rootScope.alerts.push({ type: 'info',
                        msg: 'Your mirrors was unlocked.'});
                    $location.path('/#!/mirror');
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger',
                        msg: 'Fail trying unlocking mirrors.'});
                }

            );
        }
    }
])
.controller('CtrlMirrorDetail', ['$scope', '$rootScope', '$http', '$routeParams', 'Mirror',
    function($scope, $rootScope, $http, $routeParams, Mirror) {
        $scope.mirror = Mirror.get({pk: $routeParams.pk},
            function(success){
                $rootScope.title = 'Mirror -' + mirror.title;
                $rootScope.alerts.push({ type: 'info', msg: 'Mirror brief received.'});
            },
            function(error){
                $rootScope.alerts.push({ type: 'danger', msg: error.data.error });
            }
        );

        $scope.lock = function(){
            $scope.mirror = Mirror.update({pk: $routeParams.pk}, {},
                function(success){
                    $rootScope.alerts.push({ type: 'info', msg: 'Mirror has been locked'});
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error });
                }
            );
        }
    }
]);