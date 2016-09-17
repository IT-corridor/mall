angular.module('photo.controllers', ['photo.services', 'photo.directives',
'group.services', 'common.services',
'store.services', 'tencent'])
.controller('CtrlPhotoList', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', '$translate', 'GetPageLink' , 'Photo', 'WindowScroll',
    function($scope, $rootScope, $http, $window, $location, $routeParams,
    $translate, GetPageLink, Photo, WindowScroll) {
        // Controller for searching photos
        // TODO: Merge with newest controller

        $scope.enough = false;
        $scope.is_owner = false;

        $scope.new_message = '';

        $rootScope.photo_refer = $location.url();
        $scope.r = Photo.query($routeParams,
            function(success){
                $scope.enough = success.total > 1 ? false : true;
                $scope.page_link = GetPageLink();
                $scope.page = success.current;
            },
            function(error){
                console.log(error.data);
            }
        );

        $scope.get_more = function(){
            $scope.page += 1;
            var params = {page: $scope.page, q: $routeParams.q};
            Photo.query(params, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                }
            );
        }

        WindowScroll($scope, $scope.get_more);

        $scope.like = function(index, photo_id){
            Photo.like({pk: photo_id},
                function(success){
                    $scope.r.results[index].like_count = success.like_count;
                },
                function(error){
                    $translate('PHOTO.LIST.LIKED').then(function (msg) {
                        $rootScope.alerts.push({ type: 'danger', msg: msg});
                    });
                }
            );
        };

        $scope.snapshot = function(){
            // TODO: implement screen animation, while waiting for shot
            // First: we set hidden block with "waiting" warn visible.
            Photo.save({},
                function(success){
                    // we can wait for 3 seconds here,
                    $translate('PHOTO.LIST.CREATED').then(function (msg) {
                            $rootScope.alerts.push({ type: 'success', msg:  msg});
                    });
                    $location.path('/photo/'+ success.id);
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger',  msg: error.data.error});
                }
            );
        };
    }
])
.controller('CtrlPhotoDetail', ['$scope', '$rootScope', '$http', '$routeParams',
                                '$window', '$location', '$translate', 'Photo', 'Comment',
                                'Store', 'WindowScroll',
    function($scope, $rootScope, $http, $routeParams, $window, $location, $translate,
    Photo, Comment, Store, WindowScroll) {
        $scope.is_owner = false;
        function handle_error(error){
            $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
            $location.path('/photo');
        }

        $scope.photo = Photo.get({pk: $routeParams.pk},
            function(success){
                if ($rootScope.visitor.pk == success.visitor){
                    $scope.is_owner = true;
                }
                if (success.is_store === true){
                    $scope.store = Store.overview({pk: success.owner.pk},
                        function (success){
                            create_empty_array(success);
                        }
                    );
                }
            },
            handle_error
        );

        /* "Similar photos block. Need to be cleaned */

        $scope.enough = false;
        $scope.r = Photo.similar({pk: $routeParams.pk}, function(success){
            $scope.page = success.current;
            $scope.enough = ($scope.page >= success.total) ? true : false;
        });

        $scope.get_more = function(){
            $scope.page += 1;
            Photo.similar({pk: $routeParams.pk, page: $scope.page}, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                }
            );
        }
        WindowScroll($scope, $scope.get_more);
        /* End of similar photos block */

        $scope.back = function(){
            if ($rootScope.photo_refer){
                $location.url($rootScope.photo_refer);
            }
            else{
                $location.url('/photo/newest');
            }
            console.log($rootScope.photo_refer);
            $rootScope.refer = undefined;
            console.log($rootScope.refer);
        };

        $scope.remove = function(){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    Photo.remove({pk: $routeParams.pk}, {},
                        function(success){
                            $translate('PHOTO.DETAIL.DELETED').then(function (msg) {
                                $rootScope.alerts.push({ type: 'danger', msg: msg});
                            });
                            $location.path('/group/'+ $scope.photo.group + '/photo');
                        },
                        handle_error
                    );
                }
            });
        };

        $scope.comment = function(){
            data = {photo: $routeParams.pk, message: $scope.new_message};
                Comment.save(data, function(success){
                    $scope.photo.comments.push(success);
                    $scope.new_message = '';
                },
                handle_error
            );
        }
        $scope.like_photo = function(){
            Photo.like({pk: $routeParams.pk},
                function(success){
                    $scope.photo.like_count = success.like_count;
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
                }
            );
        }

        $scope.like_comment = function(index, comment_id){
            Comment.like({pk: comment_id},
                function(success){
                    $scope.photo.comments[index].like = success.like;
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
                }
            );
        }

        function create_empty_array(obj){
            var len = obj.overview.length;
            var empty = 4 - len;
            obj.empty_array = [];
            var l = 0;
            for (l; l < empty; l++){ obj.empty_array.push(l);}
        }
    }
])
.controller('CtrlPhotoEdit', ['$scope', '$rootScope', '$http', '$routeParams',
                                '$window', '$translate', '$location', 'Photo', 'RemoveItem',
    function($scope, $rootScope, $http, $routeParams, $window, $translate,
    $location, Photo, RemoveItem) {
        function handle_error(error){
            $rootScope.alerts.push({ type: 'danger', msg: error.data.error});
            $location.path('/photo');
        }

        $scope.photo = Photo.get({pk: $routeParams.pk},
            function(success){ $scope.lim = 3 - success.link_set.length },
            handle_error
        );

        $scope.commodities = [];

        $scope.update = function(){
            data = {title: $scope.photo.title, description: $scope.photo.description};
            Photo.edit({pk: $routeParams.pk}, data,
                function(success){
                    $translate('PHOTO.EDIT.DATA_UPDATED').then(function (msg) {
                        $rootScope.alerts.push({ type: 'danger', msg: msg});
                    });
                    $location.path('/photo/' + $routeParams.pk);
                },
                handle_error
            );
        }

        $scope.remove_candidate = function(index){
            $scope.commodities.splice(index, 1);
        };

        $scope.remove_link = function(link_id){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    Photo.remove_link({pk: $routeParams.pk}, {link: link_id},
                        function(success){
                            $translate('PHOTO.EDIT.LINK_REMOVED').then(function (msg) {
                                $rootScope.alerts.push({ type: 'info', msg:  msg});
                            });
                            RemoveItem($scope.photo.link_set, link_id);
                        },
                        function(error){
                            $rootScope.alerts.push({ type: 'danger', msg: error.data.error });
                        }
                    );
                }
            });
        }

        $scope.add_links = function(){
            var c_ids = [];
            var i = 0;
            for (i; i < $scope.commodities.length; i++){
                c_ids.push($scope.commodities[i].pk);
            }
            Photo.add_links({pk: $scope.photo.id}, {commodities: c_ids},
                function(success){
                    $translate('PHOTO.EDIT.LINKS_ADDED').then(function (msg) {
                        $rootScope.alerts.push({ type: 'info', msg:  msg});
                    });
                    $scope.photo.link_set = $scope.photo.link_set.concat(success);
                    $scope.commodities = [];
                },
                function(error){
                    $rootScope.alerts.push({ type: 'danger', msg: error.data.error });
                }
            );
        };

    }
])
.controller('CtrlPhotoNewest', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', '$translate', 'GetPageLink' , 'Photo',
'title', 'kind', 'WindowScroll',
    function($scope, $rootScope, $http, $window, $location, $routeParams,
    $translate, GetPageLink, Photo, title, kind, WindowScroll) {
        // Controller for newest photos and for the liked photos

        $rootScope.title = title;
        var query = (kind === 'newest') ? Photo.newest : Photo.liked_list;

        $scope.enough = false;
        $scope.is_owner = false;

        $scope.new_message = '';

        $rootScope.photo_refer = $location.url();
        $scope.r = query(
            function(success){
                $scope.enough = success.total > 1 ? false : true;
                $scope.page_link = GetPageLink();
                $scope.page = success.current;
            },
            function(error){
                console.log(error.data);
            }
        );

        $scope.show_current = function(index){
            $scope.current = index;
            $scope.show_detail = true;
            console.log($scope.current);
        }

        $scope.get_more = function(){
            $scope.page += 1;
            var params = {page: $scope.page};
            query(params, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                },
                function(error){
                    for (var e in error.data){
                        $rootScope.alerts.push({ type: 'danger', msg: error.data[e]});
                    }
                    $scope.error = error.data;
                }
            );
        }
        WindowScroll($scope, $scope.get_more);
        $scope.like = function(index, photo_id){
            Photo.like({pk: photo_id},
                function(success){
                    $scope.r.results[index].like_count = success.like_count;
                },
                function(error){
                    $translate('PHOTO.LIST.LIKED').then(function (msg) {
                        $rootScope.alerts.push({ type: 'danger', msg: msg});
                    });
                }
            );
        }
    }
])
.controller('CtrlPhotoClone', ['$scope', '$rootScope', '$http', '$routeParams',
                                '$window', '$location', '$translate', 'Photo', 'Group',
    function($scope, $rootScope, $http, $routeParams, $window, $location,
    $translate, Photo, Group) {
        $scope.wait = false;
        $scope.photo = Photo.get({pk: $routeParams.pk});
        $scope.r = {};

        $scope.groups = Group.my_short_list();
        $scope.clone = function(){
            $scope.wait = true;
            Photo.clone({pk: $routeParams.pk}, $scope.r,
                function(success){
                    $translate('PHOTO.CLONE.CLONED').then(function (msg) {
                        $rootScope.alerts.push({ type: 'success', msg: msg});
                    });
                    $location.path('/photo/' + success.id);
                },
                function(error){
                    $translate('FAIL').then(function (msg) {
                        $rootScope.alerts.push({ type: 'danger', msg: msg});
                    });
                    $scope.wait = false;
                }
            );
        }
    }
]);