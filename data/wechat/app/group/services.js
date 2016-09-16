angular.module('group.services', ['ngResource'])
.constant('source_path', 'api/v1/')
.factory('Group', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'group/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            photo_list: {method:'GET', params:{action: 'photo_list'}, responseType:'json'},
            member_add: {method:'POST', params:{action: 'member_add'}, responseType:'json'},
            member_remove: {method:'POST', params:{action: 'member_remove'}, responseType:'json'},
            tag_create: {method:'POST', params:{action: 'tag_create'}, responseType:'json'},
            visitor_list: {method:'GET', params:{pk: null, action: 'visitor_list'},
                           responseType:'json', isArray:true},
            my: {method:'GET', params:{pk: null, action: 'my_groups'}, responseType:'json'},
            my_short_list: {method:'GET', params:{pk: null, action: 'my_groups_short'},
                responseType:'json', isArray: true},
            follow: {method: 'GET', params: {action:'follow'}},
            unfollow: {method: 'GET', params: {action:'unfollow'}},
            get_follows: {method:'GET', params:{pk: null, action: 'follow_groups'}, responseType:'json'},
    });
}])
.factory('GroupPhoto', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'group-photo/:pk/', {}, {
            update: {method: 'PATCH'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Tag', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'tag/:pk/:action/', {}, {
            update: {method: 'PATCH'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Member', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API + source_path + 'member/short_list/', {}, {
            query: {method:'GET', responseType:'json', isArray:true},
    });
}])
.factory('Visitor', ['$resource', 'source_path', 'API',
    function($resource, source_path, API){
        return $resource(API, source_path + 'visitor/:pk/:action/', {}, {
            follow_user: {method: 'GET', params: {action:'follow_user'}},
            unfollow_user: {method: 'GET', params: {action:'unfollow_user'}},
            get_follow_users: {method:'GET', params:{pk: null, action: 'follow_users'}, responseType:'json'},
            get_followers: {method:'GET', params:{pk: null, action: 'followers'}, responseType:'json'},
        });
}])
.factory('MultipartForm', ['$http', 'API', function ($http, API){
    return function(method, form_id, url){
        url = API + url;
        if (form_id){
            var form = document.querySelector(form_id);
            var formData = new FormData(form);
        }
        else{
            var formData = null;
        }
        var req = {
            method: method,
            url: url,
            headers: {'Content-Type': undefined, 'X-Requested-With': 'XMLHttpRequest'},
            data: formData,
        };
        return $http(req);
    }
}]);
