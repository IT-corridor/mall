angular.module('article.controllers', ['article.services', 'common.services', 'checklist-model'])
.controller('CtrlArticleCreate', ['$scope', '$rootScope','$http',
'$location', '$translate', '$routeParams', 'Photo', 'Article',
    function($scope, $rootScope, $http, $location, $translate, $routeParams, Photo, Article) {

        $scope.wait = false;
        $scope.r = Photo.my({pk:$routeParams.pk}, function(success) {});

        $scope.create = function() {
            Article.save($scope.data, 
                function(success){
                    $location.path('/article/' + success.id + '/edit');
                },
                function(error){
                    $scope.error = error.data;
                }
            );
        };

    }
])
.controller('CtrlArticleList', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', 'Article',
    function($scope, $rootScope, $http, $window, $location, $routeParams, Article) {
        $scope.r = Article.query($routeParams);
    }
])
.controller('CtrlArticleDetail', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', 'Article', '$sce',
    function($scope, $rootScope, $http, $window, $location, $routeParams, Article, $sce) {
        $scope.article = Article.detail({pk: $routeParams.pk},
            function(success) {
                $scope.description = $sce.trustAsHtml(success.description);
            }
        );        
    }
]);
