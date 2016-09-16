angular.module('photo.directives', ['photo.services'])
.directive('photoBlock', ['PATH', '$window', 'Photo', 'Comment',
function(PATH, $window, Photo, Comment) {
    return {
        restrict: 'E',
        replace: true,
        transclude: true,
        templateUrl: PATH + 'photo/detail_block.html',
        scope: {
            current: '=',
            photos: '=',
            show_detail: '=',
        },
        controller: function($scope, $rootScope, $window, Photo, Comment) {

        $scope.is_owner = false;
        $scope.new_message = '';
        function handle_error(error){
            console.log(error);
            $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
        }

        $scope.back = function(){
            $scope.current = null;
            $scope.$apply();
            //$scope.show_detail = false;
        }

        $scope.$watch('current', function(new_value, old_value){
            console.log($scope.photos[new_value]);
            if (new_value != undefined){
                $scope.photo = Photo.get({pk: $scope.photos[new_value].id},
                    function(success){
                        console.log(success);
                        var title = (success.title) ? success.title : 'Untitled';
                        if ($rootScope.visitor.pk == success.visitor){
                            $scope.is_owner = true;
                        }
                    },
                    function(error){
                        console.log(error);
                    }
                );
            }
            else{
                delete $scope.photo;
            }

        });

        $scope.remove = function(){
            var confirm = $window.confirm('Are you sure you want to remove that photo?');
            if (confirm){
                Photo.remove({pk: $scope.photo.id}, {},
                    function(success){
                        $rootScope.alerts.push({ type: 'info', msg: 'Photo has been deleted!'});
                        delete $scope.photos[$scope.current];
                        $scope.show_detail = false;
                    },
                    handle_error
                );
            }
        }
        $scope.comment = function(){
            data = {photo: $scope.photo.id, message: $scope.new_message};
            console.log(data);
                Comment.save(data, function(success){
                    $scope.photo.comments.push(success);
                    $rootScope.alerts.push({ type: 'info', msg: 'Thanks for the comment!'});
                    $scope.new_message = '';
                },
                handle_error
            );
        }
        $scope.like_photo = function(){
            Photo.like({pk: $scope.photo.id},
                function(success){
                    $scope.photo.like_count = success.like_count;
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
                }
            );
        }

        $scope.like_comment = function(index, comment_id){
            Comment.like({pk: comment_id},
                function(success){
                    $scope.photo.comments[index].like = success.like;
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
                }
            );
        }
    }
    }
}]);
