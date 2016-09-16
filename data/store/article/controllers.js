angular.module('article.controllers', ['article.services', 'common.services', 'checklist-model'])
.controller('CtrlArticleCreate', ['$scope', '$rootScope','$http',
'$location', '$translate', '$routeParams', 'Photo', 'Article',
    function($scope, $rootScope, $http, $location, $translate, $routeParams, Photo, Article) {

        $scope.wait = false;
        $scope.r = Photo.my({pk:$routeParams.pk}, function(success) {});

        $scope.create = function() {
            Article.save($scope.data, 
                function(success){
                    $location.path('/article');
                },
                function(error){
                    $scope.error = error.data;
                }
            );
        };
    }
])
.controller('CtrlArticleUpdate', ['$scope', '$rootScope','$http',
'$location', '$translate', '$routeParams', '$window', 'Photo', 'Article','$sce',
    function($scope, $rootScope, $http, $location, $translate, $routeParams, $window, Photo, Article,$sce) {

        $scope.wait = false;

        $scope.data = Article.detail({pk: $routeParams.pk},
            function(success) {
                $scope.description = $sce.trustAsHtml(success.description);
                $scope.r = Photo.my({}, function(success_sub) {
                    success_sub.results = success_sub.results.concat(success.photos);
                });
            }
        );        

        $scope.remove_article = function(){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    Article.remove({pk: $scope.data.id},
                        function(success){
                            $location.path('/article');
                        },
                        function(error){
                            $translate('FAIL').then(function (msg) {
                                $rootScope.alerts.push({ type: 'info', msg:  msg});
                            });
                        }
                    );
                }
            });
        };

        $scope.update = function() {
            Article.update({pk: $routeParams.pk}, $scope.data, function(success) {
                    $location.path('/article/'+ $routeParams.pk);
                },
                function(error){
                    $translate('ERROR').then(function (msg) {
                        $rootScope.alerts.push({ type: 'danger', msg:  msg});
                    });
                }
            );
        };
    }
])
.controller('CtrlArticleList', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', 'Article',
    function($scope, $rootScope, $http, $window, $location, $routeParams, Article) {
        $scope.r = Article.query($routeParams,
            function(success){
            },
            function(error){
            }
        );
    }
])
.controller('CtrlArticleDetail', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', 'Article', '$sce',
    function($scope, $rootScope, $http, $window, $location, $routeParams, Article,$sce) {
        $scope.article = Article.detail({pk: $routeParams.pk},
            function(success) {
                $scope.description = $sce.trustAsHtml(success.description);
            }
        );        
    }
]);
