angular.module('group.services', ['ngResource'])
.constant('api_path', '/api/v1/')
.factory('Group', ['$resource', 'api_path',
    function($resource, api_path){
        return $resource(api_path + 'group/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            photo_list: {method:'GET', params:{action: 'photo_list'}, responseType:'json'},
            member_add: {method:'POST', params:{action: 'member_add'}, responseType:'json'},
            member_remove: {method:'POST', params:{action: 'member_remove'}, responseType:'json'},
            tag_create: {method:'POST', params:{action: 'tag_create'}, responseType:'json'},
            vendor_list: {method:'GET', params:{pk: null, action: 'vendor_list'},
                           responseType:'json', isArray:true},
            my: {method:'GET', params:{pk: null, action: 'my_groups'}, responseType:'json'},
            my_short_list: {method:'GET', params:{pk: null, action: 'my_groups_short'},
                responseType:'json', isArray: true},
    });
}])
.factory('GroupPhoto', ['$resource', 'api_path',
    function($resource, api_path){
        return $resource(source_path + 'group-photo/:pk/', {}, {
            update: {method: 'PATCH'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Tag', ['$resource', 'api_path',
    function($resource, api_path){
        return $resource(api_path + 'tag/:pk/:action/', {}, {
            update: {method: 'PATCH'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Member', ['$resource', 'api_path',
    function($resource, api_path){
        return $resource(api_path + 'member/short_list/', {}, {
            query: {method:'GET', responseType:'json', isArray:true},
    });
}]);