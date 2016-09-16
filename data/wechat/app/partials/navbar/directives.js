var navbar = angular.module('navbar', ['auth.services'])
.directive('dNavbar', ['$window', '$location', '$routeParams', 'PATH','Logout', 'Auth',
                        function($window, $location, $routeParams, PATH, Logout, Auth) {
    return {
        restrict: 'A',
        templateUrl: PATH + 'partials/navbar/templates/navbar.html',
        controller: function($scope, $rootScope, $window, $location, $routeParams,
         PATH, Auth ){

            $scope.brand_text = 'ATYICHU';

            $scope.p = $routeParams;

            $rootScope.$on("$routeChangeStart", function(event, next, current) {
                $scope.isCollapsed = false;
            });

            $rootScope.$on("$routeChangeSuccess", function(event, next, current) {
                /* Authentication logic inside */
                Auth.get_user();
            });

            $scope.logout = function(){
                Auth.logout();
            }

            $scope.sync_profile = function(){
                Auth.sync();
                $scope.isCollapsed = false;

            }

            $scope.animationsEnabled = true;
            $scope.toggleAnimation = function () {
                $scope.animationsEnabled = !$scope.animationsEnabled;
            };

            $scope.search = function(keyEvent){
                //search
                if (keyEvent.which == 13){
                    $scope.search_c();
                }
            };

            $scope.search_c = function(){
                if ($scope.p.q){
                    $location.path('/photo/search').search({q: $scope.p.q});
                }
            };
        }
    };
}]);