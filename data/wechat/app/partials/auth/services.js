var auth = angular.module('auth.services', ['ngResource', 'ngCookies']);

auth.factory('Login', ['$resource', 'API',
    function ($resource, API) {
        return $resource(API + 'visitor/', {}, {
            query: {method: 'GET', responseType: 'json'},
        });
    }
]);
auth.factory('ProfileSync', ['$resource', 'API',
    function ($resource, API) {
        return $resource(API + 'visitor/update/', {}, {
            post: {method: 'POST', responseType: 'json'},
        });
    }
]);
auth.factory('Logout', ['$resource', 'API',
    function ($resource, API) {
        return $resource(API + 'visitor/logout/', {}, {
            query: {method: 'GET', responseType: 'json'},
        });
    }
]);
auth.factory('Me', ['$resource', 'API',
    function ($resource, API) {
        return $resource(API + 'visitor/me/', {}, {
            get: {method: 'GET', responseType: 'json'},
        });
    }
]);

auth.factory('IsAuthenticated', ['$resource', 'API',
    function ($resource, API) {
        return $resource(API + 'visitor/is_authenticated/', {}, {
            get: {method: 'GET', responseType: 'json'},
        });
    }
]);
auth.factory('IsSmartDevice', ['$window',
    function ($window) {
        return function () {
            // Checks for iOs, Android, Blackberry, Opera Mini, and Windows mobile devices
            var ua = $window['navigator']['userAgent'] || $window['navigator']['vendor'] || $window['opera'];
            return (/iPhone|iPod|iPad|Silk|Android|BlackBerry|Opera Mini|IEMobile/).test(ua);
        }
    }
]);
auth.factory('Auth', ['$rootScope', '$cookies', '$window', '$location', '$route', '$translate', 'IsAuthenticated',
    'Me', 'Logout', 'IsSmartDevice', 'LoadScript', 'ProfileSync', 'API',
    function ($rootScope, $cookies, $window, $location, $route, $translate, IsAuthenticated,
              Me, Logout, IsSmartDevice, LoadScript, ProfileSync, API) {
        /* Logic set for authentication */
        var auth = {};
        auth.get = function (key) {
            return $cookies.getObject(key) ? $cookies.getObject(key) : null;
        };
        auth.set = function (user) {

            /* SETTING COOKIE FOR 20 minutes */
            var expires = new Date();
            expires.setMinutes(expires.getMinutes() + 20);
            $cookies.putObject('weixin', user, {expires: expires});
            this.refresh();
        };
        auth.refresh = function () {
            this.user = this.get('weixin');
        };
        auth.remove = function () {
            $cookies.remove('weixin');
            this.refresh();
        };
        auth.user = auth.get('weixin');
        auth.is_authenticated = function () {
            return IsAuthenticated.get().$promise;
        };
        auth.login_handler = function () {
            var WxLoginScript = LoadScript('http://res.wx.qq.com/connect/zh_CN/htmledition/js/wxLogin.js');
            WxLoginScript.then(function (success) {
                var url = encodeURIComponent(API + "visitor/openid?qr=1");
                var login = new WxLogin({
                    id: "qr",
                    appid: "wx6ad4cd8923e9ea5e",
                    scope: "snsapi_login",
                    redirect_uri: url,
                    state: Math.ceil(Math.random() * 1000),
                });
            });

        };
        auth.get_user = function () {
            /*The main authentication logic */
            console.log('get user trigger');
            var self = this;
            if (this.user && !$rootScope.visitor) {

                $rootScope.visitor_resolved = true;
                $rootScope.visitor = this.user;
            }
            else {
                var auth_promise = self.is_authenticated();
                auth_promise.then(function (result) {
                    if (!result.is_authenticated) {
                        if (IsSmartDevice()) {
                            $window.location.replace(API + "visitor/");
                        }
                        else {
                            self.login_handler();
                        }
                    }
                    else {
                        console.log('getting personal data');
                        Me.get(
                            function (success) {
                                self.set(success);
                                $rootScope.visitor_resolved = true;
                                $rootScope.visitor = success;
                            },
                            function (error) {
                                $translate('AUTHENTICATION.ERROR').then(function (msg) {
                                    $rootScope.alerts.push({type: 'error', msg: msg});
                                });
                            }
                        );
                    }
                });
            }
        };

        auth.logout = function () {
            var self = this;
            Logout.query(function (r) {
                $translate('AUTHENTICATION.LOGOUT').then(function (msg) {
                    $rootScope.alerts.push({type: 'info', msg: msg});
                });
                self.remove();
                $rootScope.visitor_resolved = false;
                $rootScope.visitor = null;
                //$route.reload();
                $location.path('/');
            });
        };

        auth.sync = function () {
            var self = this;
            var qr = (IsSmartDevice()) ? null : 1;
            ProfileSync.post({qr: qr}, function (success) {
                    self.set(success);
                    $rootScope.visitor = success;
                    $translate('AUTHENTICATION.PROFILE_UPDATE').then(function (msg) {
                        $rootScope.alerts.push({type: 'info', msg: msg});
                    });
                    $location.path('/my_groups');

                },
                function (error) {
                    $translate('FAIL').then(function (msg) {
                        $rootScope.alerts.push({type: 'danger', msg: msg});
                        console.log(msg);
                    });
                }
            );
        };
        return auth;
    }]);