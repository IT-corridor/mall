angular.module('selfie', ['auth.services'])
.directive('wxSelf', ['PATH', function(PATH, Auth) {
    return {
        restrict: 'E',
        replace: true,
        transclude: true,
        templateUrl: PATH + 'partials/selfie/templates/block.html',
        scope: {visitor:'='},
        controller: function($scope, Auth){

            $scope.logout = function(){
                Auth.logout();
            }

            $scope.sync_profile = function(){
                Auth.sync();
            }
        }
    }
}]);
