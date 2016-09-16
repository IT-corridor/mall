angular.module('photo.controllers', ['photo.services', 'group.services',
        'store.services', 'common.services', 'tencent'
    ])
    .controller('CtrlPhotoList', ['$scope', '$rootScope', '$http', '$window',
        '$location', '$routeParams', 'GetPageLink', 'Photo',
        'WindowScroll', 'Visitor', 'RemoveItem', 'title', 'kind', 'ProcessExtraData',
        function($scope, $rootScope, $http, $window, $location, $routeParams,
            GetPageLink, Photo, WindowScroll, Visitor, RemoveItem, title, kind, ProcessExtraData) {
            // Controller for newest photos and for the liked photos

            $rootScope.title = title;
            var resource_map = {
                'list': Photo.query,
                'newest': Photo.newest,
                'liked': Photo.liked_list,
                'articles': Photo.article_photos,
            };

            var query = resource_map[kind];

            $scope.enough = false;
            $scope.is_owner = false;

            $scope.new_message = '';
            $rootScope.title = 'Newest photos';
            $rootScope.photo_refer = $location.url();
            // TODO: optimize it, move this to the $rootScope.

            $rootScope.follow_promise.then(function(list) {

                $scope.r = query($routeParams,
                    function(success) {
                        $scope.enough = success.total > 1 ? false : true;
                        $scope.page_link = GetPageLink();
                        $scope.page = success.current;
                        ProcessExtraData($rootScope.following.results, success.results);
                    },
                    function(error) {
                        console.log(error.data);
                    }
                );
            });

            $scope.get_more = function() {
                $scope.page += 1;
                var params = {
                    page: $scope.page
                };
                if ($routeParams.q){
                    params['q'] = routeParams.q;
                }
                query(params, function(success) {
                        ProcessExtraData($rootScope.following.results, success.results);
                        $scope.r.results = $scope.r.results.concat(success.results);
                        $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                    },
                    function(error) {
                        for (var e in error.data) {
                            $rootScope.alerts.push({
                                type: 'danger',
                                msg: error.data[e]
                            });
                        }
                        $scope.error = error.data;
                    }
                );
            };
            WindowScroll($scope, $scope.get_more);

            $scope.like = function(index, photo_id) {
                Photo.like({
                        pk: photo_id
                    },
                    function(success) {
                        $scope.r.results[index].like_count = success.like_count;
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: 'You have liked it already!'
                        });
                    }
                );
            }

            $scope.follow_user = function(user_id, index, is_creator) {
                console.log(user_id);
                Visitor.follow_user({
                        pk: user_id
                    },
                    function(success) {
                        $rootScope.following.results.push({
                            'pk': user_id
                        });
                        if (is_creator) {
                            $scope.r.results[index]['creator_followed'] = true;
                        } else {
                            $scope.r.results[index]['owner_followed'] = true;
                        }
                        ProcessExtraData($rootScope.following.results, $scope.r.results);
                    },
                    function(error) {
                        console.log(error);
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

            $scope.unfollow_user = function(user_id, index, is_creator) {
                Visitor.unfollow_user({
                        pk: user_id
                    },
                    function(success) {
                        RemoveItem($rootScope.following.results, user_id, 'pk');
                        if (is_creator) {
                            $scope.r.results[index]['creator_followed'] = false;
                        } else {
                            $scope.r.results[index]['owner_followed'] = false;
                        }
                        ProcessExtraData($rootScope.following.results, $scope.r.results);
                    },
                    function(error) {
                        //$rootScope.alerts.push({ type: 'danger', msg: 'You have followed it already!'});
                    }
                );
            };

            $scope.snapshot = function() {
                // TODO: implement screen animation, while waiting for shot
                // First: we set hidden block with "waiting" warn visible.
                Photo.save({},
                    function(success) {
                        // we can wait for 3 seconds here,
                        $rootScope.alerts.push({
                            type: 'success',
                            msg: 'Photo created.'
                        });
                        $location.path('/photo/' + success.id);
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

        }
    ])
    .controller('CtrlPhotoDetail', ['$scope', '$rootScope', '$http', '$routeParams',
        '$window', '$location', '$translate', 'Photo', 'Comment',
        'WXI', 'Store', 'WindowScroll',
        'Visitor', 'IsMember', 'RemoveItem', 'ProcessExtraData', '$sce', '$uibModal', 'PATH',
        function($scope, $rootScope, $http, $routeParams, $window, $location, $translate,
            Photo, Comment, WXI, Store, WindowScroll, Visitor, IsMember, RemoveItem, ProcessExtraData,
                 $sce, $uibModal, PATH) {

            $scope.is_owner = false;
            $scope.new_message = null;

            function handle_error(error) {
                $rootScope.alerts.push({
                    type: 'danger',
                    msg: error.data.error
                });
            }

            $rootScope.follow_promise.then(function(result) {

                $scope.photo = Photo.get({
                        pk: $routeParams.pk
                    },
                    function(success) {
                        var title = (success.title) ? success.title : 'Untitled'
                        $rootScope.title = 'Photo -' + success.title;
                        if ($rootScope.visitor.pk == success.visitor) {
                            $scope.is_owner = true;
                        }
                        if (success.is_store === true) {
                            $scope.store = Store.overview({
                                    pk: success.owner.pk
                                },
                                function(success) {
                                    create_empty_array(success);
                                }
                            );
                        }

                        success['owner_followed'] = IsMember($rootScope.following.results, success.visitor, 'pk');
                        success['creator_followed'] = IsMember($rootScope.following.results, success.creator, 'pk');
                        if (success['article']){
                            success['article']['descr'] = $sce.trustAsHtml(success['article']['descr']);
                        }


                        var title = (success.title) ? success.title : '品味和格调兼具';
                        var photo_desc = (success.description) ? success.description : '大家快来看，秀出你的品味和格调!';
                        var descr = title + ': ' + photo_desc;
                        WXI.set_on_share(descr, success.photo);
                    },
                    handle_error
                );
            });


            $scope.read_article = function(article_id) {
                $location.path('/article/' + article_id);
            }

            $scope.open_modal = function (resource) {
                var modalInstance = $uibModal.open({
                    animation: $scope.animationsEnabled,
                    templateUrl: PATH + 'photo/templates/modal_' + resource + '.html',
                    controller: 'PhotoModalInstanceCtrl',
                    size: 'md',
                    resolve: {
                        photo: function () {
                            return $scope.photo;
                        },
                        name: function () {
                            return resource;
                        }
                    }
                });

                modalInstance.result.then(
                    function (success) {
                        $translate('SUCCESS').then(function (msg) {
                            $rootScope.alerts.push({type: 'info', msg: msg});
                        });
                    }
                );
            };
            /* "Similar photos block. Need to be cleaned */

            $scope.enough = false;
            $scope.r = Photo.similar({
                pk: $routeParams.pk
            }, function(success) {
                ProcessExtraData($rootScope.following.results, success.results);
                $scope.page = success.current;
                $scope.enough = ($scope.page >= success.total) ? true : false;
            });

            $scope.get_more = function() {
                $scope.page += 1;
                Photo.similar({
                    pk: $routeParams.pk,
                    page: $scope.page
                }, function(success) {
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                    ProcessExtraData($rootScope.following.results, success.results);
                });
            }
            WindowScroll($scope, $scope.get_more);
            /* End of similar photos block */

            $scope.back = function() {
                if ($rootScope.photo_refer) {
                    $location.url($rootScope.photo_refer);
                } else {
                    $location.url('/photo/newest');
                }
                console.log($rootScope.photo_refer);
                $rootScope.refer = undefined;
                console.log($rootScope.refer);
            }
            $scope.remove = function() {
                var confirm = $window.confirm('Are you sure you want to remove that photo?');
                if (confirm) {
                    Photo.remove({
                            pk: $routeParams.pk
                        }, {},
                        function(success) {
                            $rootScope.alerts.push({
                                type: 'info',
                                msg: 'Photo has been deleted!'
                            });
                            $location.path('/group/' + $scope.photo.group + '/photo');
                        },
                        handle_error
                    );
                }
            }
            $scope.comment = function() {
                if (!$scope.new_message) {
                    $translate('PHOTO.DETAIL.EMPTY_COMMENT').then(function(msg) {
                        $rootScope.alerts.push({
                            type: 'warning',
                            msg: msg
                        });

                    });
                } else {
                    data = {
                        photo: $routeParams.pk,
                        message: $scope.new_message
                    };
                    Comment.save(data, function(success) {
                            $scope.photo.comments.push(success);
                            $translate('PHOTO.DETAIL.COMMENT').then(function(msg) {
                                $rootScope.alerts.push({
                                    type: 'info',
                                    msg: msg
                                });
                            });
                            $scope.new_message = null;
                        },
                        handle_error
                    );
                }

            }
            $scope.like_photo = function() {
                Photo.like({
                        pk: $routeParams.pk
                    },
                    function(success) {
                        $scope.photo.is_liked = true;
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

            $scope.dislike_photo = function (){
                Photo.dislike({pk: $routeParams.pk},
                    function(success){
                        $scope.photo.is_liked = false;
                    },
                    function(error){
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.detail
                        });
                    }
                )
            }

            $scope.like_comment = function(index, comment_id) {
                Comment.like({
                        pk: comment_id
                    },
                    function(success) {
                        $scope.photo.comments[index].like = success.like;
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

            function create_empty_array(obj) {
                var len = obj.overview.length;
                var empty = 4 - len;
                obj.empty_array = [];
                var l = 0;
                for (l; l < empty; l++) {
                    obj.empty_array.push(l);
                }
            }

            $scope.follow_user_main = function(user_id, index, is_creator) {
                Visitor.follow_user({
                        pk: user_id
                    },
                    function(success) {
                        $rootScope.following.results.push({
                            'pk': user_id
                        });
                        if (is_creator) {
                            $scope.photo['creator_followed'] = true;
                        } else {
                            $scope.photo['owner_followed'] = true;
                        }
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

            $scope.unfollow_user_main = function(user_id, index, is_creator) {
                Visitor.unfollow_user({
                        pk: user_id
                    },
                    function(success) {
                        RemoveItem($rootScope.followed.results, user_id, 'pk');
                        if (is_creator) {
                            $scope.photo['creator_followed'] = false;
                        } else {
                            $scope.photo['owner_followed'] = false;
                        }
                    },
                    function(error) {}
                );
            };

            $scope.follow_user = function(user_id, index, is_creator) {
                Visitor.follow_user({
                        pk: user_id
                    },
                    function(success) {
                        $rootScope.following.results.push({
                            'pk': user_id
                        });
                        if (is_creator) {
                            $scope.r.results[index]['creator_followed'] = true;
                        } else {
                            $scope.r.results[index]['owner_followed'] = true;
                        }
                        ProcessExtraData($rootScope.following.results, $scope.r.results);
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: error.data.error
                        });
                    }
                );
            };

            $scope.unfollow_user = function(user_id, index, is_creator) {
                Visitor.unfollow_user({
                        pk: user_id
                    },
                    function(success) {
                        RemoveItem($rootScope.following.results, user_id, 'pk');
                        if (is_creator) {
                            $scope.r.results[index]['creator_followed'] = false;
                        } else {
                            $scope.r.results[index]['owner_followed'] = false;
                        }
                        ProcessExtraData($rootScope.following.results, $scope.r.results);
                    },
                    function(error) {
                        //$rootScope.alerts.push({ type: 'danger', msg: 'You have followed it already!'});
                    }
                );
            };

        }
    ])
    .controller('CtrlPhotoEdit', ['$scope', '$rootScope', '$http', '$routeParams',
        '$window', '$location', 'Photo',
        function($scope, $rootScope, $http, $routeParams, $window, $location, Photo) {
            $rootScope.title = 'Edit Photo Data';

            function handle_error(error) {
                $rootScope.alerts.push({
                    type: 'danger',
                    msg: error.data.error
                });
            }

            $scope.photo = Photo.get({
                    pk: $routeParams.pk
                },
                function(success) {},
                handle_error
            );


            $scope.update = function() {
                data = {
                    title: $scope.photo.title,
                    description: $scope.photo.description
                };
                Photo.edit({
                        pk: $routeParams.pk
                    }, data,
                    function(success) {
                        $rootScope.alerts.push({
                            type: 'info',
                            msg: 'Data has been updated.'
                        });
                        $location.path('/photo/' + $routeParams.pk);
                    },
                    handle_error
                );
            }
        }
    ])
    .controller('CtrlPhotoClone', ['$scope', '$rootScope', '$http', '$routeParams',
        '$window', '$location', 'Photo', 'Group',
        function($scope, $rootScope, $http, $routeParams, $window, $location, Photo, Group) {
            $rootScope.title = 'Clone Photo';
            $scope.wait = false;
            $scope.photo = Photo.get({
                pk: $routeParams.pk
            });
            $scope.r = {};

            $scope.groups = Group.my_short_list();
            $scope.clone = function() {
                $scope.wait = true;
                Photo.clone({
                        pk: $routeParams.pk
                    }, $scope.r,
                    function(success) {
                        $rootScope.alerts.push({
                            type: 'info',
                            msg: 'Photo has been cloned.'
                        });
                        $location.path('/photo/' + success.id);
                    },
                    function(error) {
                        $rootScope.alerts.push({
                            type: 'danger',
                            msg: 'Fail!'
                        });
                        $scope.wait = false;
                    }
                );
            }
        }
    ])
    .controller('PhotoModalInstanceCtrl',
        ['$scope', '$rootScope', '$uibModalInstance', 'name', 'photo', '$translate', '$route', '$http', 'Photo', '$location',
            function ($scope, $rootScope, $uibModalInstance, name, photo, $translate, $route, $http, Photo, $location) {
                $scope.dict_data = {name: name};
                $scope.photo = photo;

                $scope.getLocation = function (val) {
                    return $http.jsonp('http://apis.map.qq.com/ws/place/v1/suggestion', {
                        params: {
                            keyword: val,
                            key: 'NY6BZ-2IB35-AMFIV-QMWBJ-RKC2Z-6BFDG',
                            output: 'jsonp',
                            callback: 'JSON_CALLBACK',
                        }
                    }).then(function (response) {
                        return response.data.data.map(function (item) {
                            return item.address;
                        });
                    });
                };

                function handle_error(error) {
                    $rootScope.alerts.push({
                        type: 'danger',
                        msg: error.data.error
                    });
                }

                $scope.update_address = function () {
                    data = {address: photo.address}
                    Photo.edit({
                            pk: photo.id
                        }, data,
                        function(success) {
                            $rootScope.alerts.push({
                                type: 'info',
                                msg: 'Data has been updated.'
                            });
                            // $location.path('/photo/' + $routeParams.pk);
                            $uibModalInstance.dismiss('cancel');
                        },
                        handle_error
                    );
                }
                $scope.cancel = function () {
                    $uibModalInstance.dismiss('cancel');
                }
            }
        ]);