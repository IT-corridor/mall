angular.module('user.services', ['ngResource'])
.constant('user_path', 'visitor/profile/')
.factory('User', ['$resource', 'user_path',
    function($resource, user_path){
        return $resource(user_path + ':pk/:action/', {}, {
            query: {method:'GET', params:{pk: null}, responseType:'json'},
            me: {method:'GET', params:{pk: null, action: 'me'}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            edit: {method: 'PATCH', params: {action: 'edit'}, responseType: 'json'},
            change_password: {method: 'POST', params: {action: 'change_password'}, responseType: 'json'},
            login: {method: 'POST', params: {action: 'login'}, responseType: 'json'},
            login_start: {method: 'POST', params: {action: 'login_start'}, responseType: 'json'},
            login_end: {method: 'POST', params: {action: 'login_end'}, responseType: 'json'},
            send_code: {method: 'POST', params: {action: 'send_code'}, responseType: 'json'},
            verify_code: {method: 'POST', params: {action: 'verify_code'}, responseType: 'json'},
            wechat_phone: {method: 'POST', params: {action: 'wechat_phone'}, responseType: 'json'},
            reset_password: {method: 'POST', params: {action: 'reset_password'}, responseType: 'json'},
    });
}]);
