angular.module('app.route', [
    'ngRoute',
    'common.controllers',
    'mirror.controllers',
    'photo.controllers',
    'user.controllers',
    'group.controllers',
    'article.controllers',
    'notification.controllers',
    'store.controllers',
])
.config(['$routeProvider','PATH',
    function($routeProvider, PATH) {
        $routeProvider.
        when('/', {
            templateUrl: PATH + 'group/templates/photo_list_new.html',
            controller: 'CtrlPhotoList',
            resolve: {
                title: function(){return 'Newest Photos';},
                kind: function(){return 'newest'},
            }
        }).
        when('/article/:pk', {
            templateUrl: PATH + 'article/templates/detail.html',
            controller: 'CtrlArticleDetail',
        }).                
        when('/mirror/', {
            templateUrl: PATH + 'mirror/templates/list.html',
            controller: 'CtrlMirrorList'}).
        when('/mirror/:pk', {
            templateUrl: PATH + 'mirror/templates/detail.html',
            controller: 'CtrlMirrorDetail'}).
        when('/article_photos', {
            templateUrl: PATH + 'group/templates/photo_list.html',
            controller: 'CtrlPhotoList',
            resolve: {
                title: function(){return 'Article Photos';},
                kind: function(){return 'articles'},
            }
        }).
        when('/photo/newest', {
            templateUrl: PATH + 'group/templates/photo_list_new.html',
            controller: 'CtrlPhotoList',
            resolve: {
                title: function(){return 'Newest Photos';},
                kind: function(){return 'newest'},
            }
        }).
        when('/photo/liked', {
            templateUrl: PATH + 'group/templates/photo_list_new.html',
            controller: 'CtrlPhotoList',
            resolve: {
                title: function(){return 'Liked Photos';},
                kind: function(){return 'liked'},
            }
        }).
        when('/photo/search', {
            templateUrl: PATH + 'group/templates/photo_list_new.html',
            controller: 'CtrlPhotoList',
            resolve: {
                title: function(){return 'Search results';},
                kind: function(){return 'list'},
            }
        }).
        when('/notifications', {
            templateUrl: PATH + 'notification/templates/notifications.html',
            controller: 'CtrlNotification'
        }).
        when('/photo/:pk', {
            templateUrl: PATH + 'photo/templates/detail_new.html',
            controller: 'CtrlPhotoDetail'}).
        when('/photo/:pk/edit', {
            templateUrl: PATH + 'photo/templates/edit.html',
            controller: 'CtrlPhotoEdit'}).
        when('/photo/:pk/share', {
            templateUrl: PATH + 'photo/templates/clone.html',
            controller: 'CtrlPhotoClone'}).
        when('/profile', {
            templateUrl: PATH + 'user/templates/user.html',
            controller: 'CtrlProfile'}).
        when('/group', {
            templateUrl: PATH + 'group/templates/list.html',
            controller: 'CtrlGroupList',
            resolve: {
                title: function(){return 'Groups';},
                my: function(){return false},
            }
        }).
        when('/group/:pk/photo', {
            templateUrl: PATH + 'group/templates/photo_list.html',
            controller: 'CtrlGroupPhotoList'}).
        when('/group/:pk/photo/add', {
            templateUrl: PATH + 'group/templates/photo_add.html',
            controller: 'CtrlGroupPhotoAdd'}).
        when('/group/create', {
            templateUrl: PATH + 'group/templates/create.html',
            controller: 'CtrlGroupAdd'}).
        when('/group/:pk/manage', {
            templateUrl: PATH + 'group/templates/manage.html',
            controller: 'CtrlGroupManage'}).
        when('/my_groups', {
            templateUrl: PATH + 'group/templates/my.html',
            controller: 'CtrlGroupList',
            resolve: {
                title: function(){return 'My Groups';},
                my: function(){return true;},
            }
        }).
        when('/follow_groups', {
            templateUrl: PATH + 'group/templates/follow.html',
            controller: 'CtrlFollowGroupList',
            resolve: {
                title: function(){return 'Follow Groups';},
                follow: function(){return true;},
            }
        }).
        when('/follow_users', {
            templateUrl: PATH + 'group/templates/follow_user.html',
            controller: 'CtrlFollowUserList',
            resolve: {
                title: function(){return 'Follow Users';},
            }
        }).
        when('/followers', {
            templateUrl: PATH + 'group/templates/follower.html',
            controller: 'CtrlFollowerList',
        }).
        when('/me', {
            templateUrl: PATH + 'user/templates/user.html',
            controller: 'CtrlProfile',
        }).
        when('/me/change_password', {
            templateUrl: PATH + 'user/templates/change_password.html',
            controller: 'CtrlChangePassword',
        }).
        when('/me/bind_phone', {
            templateUrl: PATH + 'user/templates/wechat_password.html',
            controller: 'CtrlWechatSetPassword',
        }).
        when('/commodities/:pk/', {
            templateUrl: PATH + 'store/templates/commodity_detail.html',
            controller: 'CtrlCommodityDetail'}).
        when('/store/:pk/', {
            templateUrl: PATH + 'store/templates/detail.html',
            controller: 'CtrlStoreDetail'}).
        when('/error/404/', {
            templateUrl: PATH + 'partials/error/templates/404.html'}).
        otherwise({
            redirectTo: '/error/404/'
        });
    }
]);
