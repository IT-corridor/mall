angular.module('photo.services', ['ngResource'])
.constant('api_path', 'api/v1/')
.factory('Photo', ['$resource', 'api_path', 'API',
    function($resource, api_path, API){
        return $resource(API + api_path + 'photo/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            like: {method: 'GET', params: {action:'like'}},
            newest: {method: 'GET', params: {action: 'newest'}, responseType: 'json'},
            edit: {method: 'PATCH', params: {action: 'edit'}, responseType: 'json'},
            clone: {method: 'POST', params: {action: 'clone'}, responseType: 'json'},
            liked_list: {method: 'GET', params: {action: 'liked_list'}, responseType: 'json'},
            add_links: {method: 'POST', params: {action: 'add_links'}, responseType: 'json', isArray: true},
            remove_link: {method: 'POST', params: {action: 'remove_link'}, responseType: 'json'},
            similar: {method: 'GET', params: {action: 'similar'}, responseType: 'json'},
            my: {method: 'GET', params: {action: 'my_photos'}, responseType: 'json'},
    });
}])
.factory('Comment', ['$resource', 'api_path', 'API',
    function($resource, api_path, API){
        return $resource(API + api_path + 'comment/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            like: {method: 'GET', params: {action:'like'}}
    });
}]);
