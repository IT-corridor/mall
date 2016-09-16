angular.module('article.services', ['ngResource'])
    .constant('article_path', '/api/v1/')
    .factory('Article', ['$resource', 'article_path',
        function ($resource, article_path) {
            return $resource(article_path + 'article/:pk/:action/', {}, {
                query: {method: 'GET', params: {action: null}, responseType: 'json'},
                save: {method: 'POST'},
                update: {method: 'PATCH'},
                remove: {method: 'DELETE'},
                detail: {method: 'GET', params: {action: null}, responseType: 'json'},
            });
        }])
    .directive('ckEditor', function () {
        return {
            require: '?ngModel',
            link: function (scope, elm, attr, ngModel) {
                var ck = CKEDITOR.replace(elm[0]);
                if (!ngModel) return;
                ck.on('instanceReady', function () {
                    ck.setData(ngModel.$viewValue);
                });
                function updateModel() {
                    scope.$apply(function () {
                        ngModel.$setViewValue(ck.getData());
                    });
                }

                ck.on('change', updateModel);
                ck.on('key', updateModel);
                ck.on('dataReady', updateModel);

                ngModel.$render = function (value) {
                    ck.setData(ngModel.$viewValue);
                };
            }
        };
    });
