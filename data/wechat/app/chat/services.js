angular.module('chat.services', ['ngResource'])
.constant('chat_path', 'visitor/chat/')
.factory('Chat', ['$resource', 'chat_path', 'API',
    function($resource, chat_path, API){
        return $resource(API + chat_path + ':pk/:action/', {}, {
            create_session: {method:'POST', params:{action: 'create_session'}, responseType:'json'},
            destroy_session: {method:'POST', params:{action: 'destroy_session'}, responseType:'json'},

    });
}])
.factory('Quickblox', ['$rootScope', '$window', '$q', 'Chat',
function($rootScope, $window, $q, Chat){
    var defer = $q.defer();
    var promise = defer.promise;
    var Quickblox = {};
    var CONFIG = {
        debug: {mode: 1}
    };

    $rootScope.credentials = Chat.create_session(function(success){
        defer.resolve();
    });
    Quickblox.create_session = function(){
        promise.then(function(success){
            $window.sessionToken = '4d870eb6b42f5087850d7a62c3006d4ad300ba1a';
            $window.appId = '47642';
            console.log(sessionToken, typeof sessionToken);
            console.log(appId);
            QB.init($window.sessionToken, $window.appId);
            QB.login({login: $rootScope.credentials.login, password: $rootScope.credentials.password}, function(err, res) {
              if (res) {
                QB.chat.connect({userId: $rootScope.credentials.qid, password: $rootScope.credentials.password}, function(err, roster) {
                  if (err) {
                      console.log(err);
                  } else {
                    console.log(res);
                  }
                });
              }else{
                console.log(err);
              }
            });
        });
    };



    return Quickblox;
}]);
