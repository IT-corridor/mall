angular.module('chat.services', ['ngResource'])
.constant('chat_path', 'visitor/chat/')
.factory('Chat', ['$resource', 'chat_path', 'API',
    function($resource, chat_path, API){
        return $resource(API + chat_path + ':pk/:action/', {}, {
            create_session: {method:'POST', params:{action: 'create_session'}, responseType:'json'},
            destroy_session: {method:'POST', params:{action: 'destroy_session'}, responseType:'json'},

    });
}]);
