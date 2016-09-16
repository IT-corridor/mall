var footer = angular.module('footer', [])
.directive('dFooter', ['PATH', '$anchorScroll', '$location' ,
    function(PATH, $anchorScroll, $location) {
        return {
            restrict: 'A',
            templateUrl: PATH + 'partials/footer/footer.html',
            controller: function($scope, $anchorScroll, $location){


                $scope.go_to_top = function(x) {
                    var hash = 'content';
                    if ($location.hash() != hash){
                        $location.hash(hash);
                    }
                    else{
                        $anchorScroll();
                    }

                };
            }
        }
    }

]);