angular.module('dashboard.services', ['ngResource'])
    .constant('source_path', '/api/v1/')
    .factory('Dashboard', ['$resource', 'source_path',
        function ($resource, source_path) {
            return $resource(source_path + 'dashboard/:year/:month/:action/', {}, {
                group_followers: {method: 'GET', params: {action: 'group_followers'}, responseType: 'json'},
                photo_fans: {method: 'GET', params: {action: 'photo_fans'}, responseType: 'json'},
                photo_clones: {method: 'GET', params: {action: 'photo_clones'}, responseType: 'json'},
                store_followers: {method: 'GET', params: {action: 'store_followers'}, responseType: 'json', isArray: true},
            });
        }]);