angular.module('group.directives', ['group.services'])
.directive('memberList', ['PATH', 'Group', function(PATH, Group) {
return {
  restrict: 'E',
  replace: true,
  templateUrl: PATH + 'group/templates/member_dropdown.html',
  scope: {member:'=', placeholder:'='},
  controller: function($scope, PATH, Group){

        $scope.active = 0;
        $scope.results = [];
        $scope.is_visible = false;
        $scope.set_active = function (index) {$scope.active = index;};

        $scope.get_results = function (text) {
            $scope.results = Group.vendor_list({q: text});
        };

        $scope.on_focus = function(){
            if (!$scope.is_visible){
                $scope.is_visible = true;
            }
        };

        $scope.on_blur = function(){
            $scope.is_visible = false;
        };

        $scope.select_item = function (index) {
            if ($scope.results.length > 0) {
                $scope.member = $scope.results[index].username;
                $scope.results.length = 0;
            }
        };
    }
}
}])
.directive('memberChoice', ['PATH', 'Group', function(PATH, Group) {
return {
  restrict: 'E',
  replace: true,
  templateUrl: PATH + 'group/templates/member_dropdown.html',
  scope: {member:'=', placeholder:'=', members: '='},
  controller: function($scope, PATH, Group){

        $scope.active = 0;
        $scope.results = [];
        $scope.is_visible = false;
        $scope.set_active = function (index) {$scope.active = index;};

        $scope.get_results = function (text) {
            $scope.results = Group.vendor_list({q: text});

        };

        $scope.on_focus = function(){
            if (!$scope.is_visible){
                $scope.is_visible = true;
            }
        };

        $scope.on_blur = function(){
            $scope.is_visible = false;
        };

        $scope.select_item = function (index) {
            if ($scope.results.length > 0) {
                $scope.members.push($scope.results[index]);
                $scope.member = '';
                $scope.results.length = 0;
            }
        };
    }
}
}]);