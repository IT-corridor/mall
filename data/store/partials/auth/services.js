var auth = angular.module('auth.services', ['ngResource', 'ngCookies']);

auth.factory('Login', ['$resource',
    function($resource){
        return $resource('/account/login/', {}, {
            query: {method:'POST', responseType:'json'},
        });
    }
]);
auth.factory('Logout', ['$resource',
    function($resource){
        return $resource('/account/logout/', {}, {
            query: {method:'GET', responseType:'json'},
        });
    }
]);
auth.factory('MyVendor', ['$resource',
    function($resource){
        return $resource('/account/my_vendor/', {}, {
            get: {method:'GET', responseType:'json'},
        });
    }
]);

auth.factory('IsAuthenticated', ['$resource',
    function($resource){
        return $resource('/account/is_authenticated/', {}, {
            get: {method:'GET', responseType:'json'},
        });
    }
]);
auth.factory('Auth', ['$rootScope', '$cookies', '$location', '$translate', 'IsAuthenticated',
                      'MyVendor', 'Login', 'Logout',
function($rootScope, $cookies, $location, $translate, IsAuthenticated,
         MyVendor, Login, Logout){
    var auth = {};
    auth.get = function(key){
        return $cookies.getObject(key) ? $cookies.getObject(key) : null;
    };
    auth.set = function(user){
        $cookies.putObject('user', user);
        this.refresh();
    };
    auth.refresh = function(){
        this.user = this.get('user');
    };
    auth.remove = function(){
        $cookies.remove('user');
        this.refresh();
    };
    auth.user = auth.get('user');
    auth.is_authenticated = function(){

        return IsAuthenticated.get().$promise;
        //return this.username !== null;
    };
    auth.get_user = function() {
        var self = this;
        if (this.user){
            $rootScope.visitor_resolved = true;
            $rootScope.visitor = this.user;
        }
        else {
            MyVendor.get(
                function(success){
                    self.set(success);
                    $rootScope.visitor_resolved = true;
                    $rootScope.visitor = success;
                },
                function(error){
                    $translate('AUTHENTICATION.ERROR').then(function (msg) {
                        $rootScope.alerts.push({ type: 'error', msg:  msg});
                    });
                }
            );
        }
    };

    auth.logout = function(){
        var self = this;
        Logout.query(function(r){
            $translate('AUTHENTICATION.LOGOUT').then(function (msg) {
                $rootScope.alerts.push({ type: 'info', msg:  msg});
            });
            self.remove();
            $rootScope.visitor_resolved = false;
            $rootScope.visitor = null;
            $location.path('/');
        });
    };

    auth.login = function(username, password){
        return Login.query({username: username, password: password }).$promise;
    }

    return auth;
}]);
