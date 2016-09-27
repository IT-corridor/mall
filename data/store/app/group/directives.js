angular.module('group.directives', ['group.services'])
    .directive('memberChoice', ['PATH', 'Group', function(PATH, Group) {
        return {
            restrict: 'E',
            replace: true,
            templateUrl: PATH + 'group/templates/member_dropdown.html',
            scope: {
                member: '=',
                placeholder: '=',
                members: '='
            },
            controller: function($scope, PATH, Group) {

                $scope.active = 0;
                $scope.results = [];
                $scope.is_visible = false;
                $scope.set_active = function(index) {
                    $scope.active = index;
                };

                $scope.get_results = function(text) {
                    $scope.results = Group.visitor_list({
                        q: text
                    });

                };

                $scope.on_focus = function() {
                    if (!$scope.is_visible) {
                        $scope.is_visible = true;
                    }
                };

                $scope.on_blur = function() {
                    $scope.is_visible = false;
                };

                $scope.select_item = function(index) {
                    if ($scope.results.length > 0) {
                        $scope.members.push($scope.results[index]);
                        $scope.member = '';
                        $scope.results.length = 0;
                    }
                };
            }
        }
    }])
    .directive('memberTypeahead', ['PATH', 'Group', function(PATH, Group) {
        return {
            restrict: 'E',
            replace: true,
            templateUrl: PATH + 'group/templates/member_typeahead.html',
            scope: {
                member: '='
            },
            controller: function($scope, PATH, Group) {
                $scope.modelOptions = {
                    debounce: {
                        default: 500,
                        blur: 250
                    },
                    getterSetter: true
                };

                $scope.get_members = function(val) {
                    var promise = Group.vendor_list({
                        q: val
                    }).$promise;
                    return promise.then(function(success) {
                        return success.map(function(item) {
                            return item.username;
                        });
                    });

                };

            }
        }
    }]);
