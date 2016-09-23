angular.module('article.services', ['ngResource'])
    .constant('article_path', 'api/v1/')
    .factory('Article', ['$resource', 'article_path', 'API',
        function ($resource, article_path, API) {
            return $resource(API + article_path + 'article/:pk/:action/', {}, {
                query: {method: 'GET', params: {action: null}, responseType: 'json'},
                save: {method: 'POST'},
                detail: {method: 'GET', params: {action: null}, responseType: 'json'},
            });
        }]);
