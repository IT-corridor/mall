angular.module('store.directives', [])
    .directive('addressChoice', ['PATH', '$http', function(PATH, $http) {
        return {
            restrict: 'E',
            replace: true,
            templateUrl: PATH + 'store/templates/address_typeahead.html',
            scope: {
                store: '=',
            },
            controller: function($scope, $http) {

                $scope.get_location = function(val) {
                    return $http.jsonp('http://apis.map.qq.com/ws/place/v1/suggestion', {
                        params: {
                            region: $scope.store.state_title,
                            keyword: val,
                            key: 'NY6BZ-2IB35-AMFIV-QMWBJ-RKC2Z-6BFDG',
                            output: 'jsonp',
                            callback: 'JSON_CALLBACK',
                        }
                    }).then(function(response) {
                        console.log(response);
                        return response.data.data.map(function(item) {
                            return item;
                        });
                    });
                };

                $scope.get_item = function($item, $model, $label, $event) {
                    $scope.store.state_title = $item.province
                    $scope.store.city_title = $item.city
                    $scope.store.district_title = $item.district
                    $scope.store.lat = $item.location.lat
                    $scope.store.lng = $item.location.lng
                }
            }
        }
    }]);
