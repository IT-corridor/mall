angular.module('photo.services', ['ngResource', 'common.services'])
.constant('source_path', 'api/v1/')
.factory('Photo', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'photo/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            like: {method: 'GET', params: {action:'like'}},
            dislike: {method: 'DELETE', params: {action:'dislike'}},
            newest: {method: 'GET', params: {action: 'newest'}, responseType: 'json'},
            edit: {method: 'PATCH', params: {action: 'edit'}, responseType: 'json'},
            clone: {method: 'POST', params: {action: 'clone'}, responseType: 'json'},
            liked_list: {method: 'GET', params: {action: 'liked_list'}, responseType: 'json'},
            similar: {method: 'GET', params: {action: 'similar'}, responseType: 'json'},
            my_photos: {method: 'GET', params: {action: 'my_photos'}, responseType: 'json'},
            article_photos: {method: 'GET', params: {action: 'article_photos'}, responseType: 'json'},
    });
}])
.factory('Comment', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'comment/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            like: {method: 'GET', params: {action:'like'}}
    });
}])
.factory('ProcessExtraData', ['$sce', 'IsMember',
    function($sce, IsMember){
        return function (base_arr, compare_arr) {
            /** USED ONLY WITH PHOTO LISTS**/
            var i = 0,
                l = compare_arr.length;
            for (i; i < l; i++) {
                compare_arr[i]['owner_followed'] = IsMember(base_arr, compare_arr[i].visitor, 'pk');
                compare_arr[i]['creator_followed'] = IsMember(base_arr, compare_arr[i].creator, 'pk');
            };

        };
}]);
