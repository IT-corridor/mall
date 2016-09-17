angular.module('photo.directives', ['commodity.services'])
.directive('commodityChoice', ['PATH', 'Commodity', function(PATH, Commodity) {
return {
  restrict: 'E',
  replace: true,
  templateUrl: PATH + 'photo/templates/commodity_dropdown.html',
  scope: {member:'=', placeholder:'=', commodities: '=', lim: '=', photo: '='},
  controller: function($scope, PATH, Commodity){

        $scope.active = 0;
        $scope.results = [];
        $scope.is_visible = false;
        $scope.set_active = function (index) {$scope.active = index;};

        $scope.get_results = function (text) {
            if (text !== ''){
                $scope.results = Commodity.my({q: text, photo: $scope.photo});
            }
        };

        $scope.input_blur = function(){
            if($scope.city){ $scope.results.length = 0 }
            $scope.is_visible = false;
        };
        $scope.select_item = function (index) {
            if ($scope.results.length > 0) {
                if ($scope.lim > $scope.commodities.length){
                    $scope.commodities.push($scope.results[index]);
                    $scope.commodity = '';
                    $scope.results.length = 0;

                }
            }
        };
    }
}
}])
.directive('commodityGrid', ['PATH', 'Commodity', function(PATH, Commodity) {
return {
  restrict: 'E',
  replace: true,
  templateUrl: PATH + 'photo/templates/commodity_grid.html',
  scope: {member:'=', placeholder:'=', commodities: '=', lim: '=', photo: '='},
  controller: function($scope, PATH, Commodity){
        $scope.page = 1;

        $scope.get_results = function (text) {
            if (text !== ''){
                var params = {q: text, photo: $scope.photo, page: $scope.page};
                $scope.r = Commodity.my(params, function(success){

                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                    });
            }
        };

        $scope.get_more = function(text){
            $scope.page += 1;
            var params = {q: $scope.commodity, photo: $scope.photo, page: $scope.page};
            Commodity.my(params, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                }
            );
        }

        $scope.select_item = function (index) {
            if ($scope.r.results.length > 0) {
                if ($scope.lim > $scope.commodities.length){
                    $scope.commodities.push($scope.r.results[index]);
                    $scope.r.results.splice(index, 1);

                }
            }
        };
    }
}
}]);