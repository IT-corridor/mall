angular.module('commodity.controllers', ['commodity.services', 'common.services', 'commodity.directives'])
.controller('CtrlCommodityCreate', ['$scope', '$rootScope','$http',
'$location', '$translate', 'MultipartForm', 'Store', 'Category', 'Kind', 'Size', 'Color',
    function($scope, $rootScope, $http, $location, $translate, MultipartForm,
    Store, Category, Kind, Size, Color) {

        $scope.wait = false;

        $scope.category_list = Category.query();
        $scope.brand_list = Store.my_brands();
        $scope.stock_set = ''; // this is a json string;

        $scope.year = 2016;


        $scope.get_kind_list = function(){
            $scope.kind_list = Kind.query({category: $scope.category});
        }

        $translate(['COMMODITY.SEASONS.WINTER',
                    'COMMODITY.SEASONS.SPRING',
                    'COMMODITY.SEASONS.SUMMER',
                    'COMMODITY.SEASONS.AUTUMN',
                    ])
        .then(function (translations) {
            $scope.season_list = [
                {id: 0, title: translations['COMMODITY.SEASONS.WINTER']},
                {id: 1, title: translations['COMMODITY.SEASONS.SPRING']},
                {id: 2, title: translations['COMMODITY.SEASONS.SUMMER']},
                {id: 3, title: translations['COMMODITY.SEASONS.AUTUMN']}
            ];
        });

        $scope.create = function() {
            $scope.wait = true;
            var url = '/catalog/commodities/';
            MultipartForm('POST', '#commodity_form', url).then(function(response) {
                    $translate('COMMODITY.CREATE.SUCCESS').then(function (msg) {
                        $rootScope.alerts.push({ type: 'info', msg:  msg});
                    });
                    $location.path('/commodities/'+ response.data.id + '/edit');
                },
                function(error) {
                    $scope.error = error.data;
                    $scope.wait = false;
                }
            );

        };

    }
])
.controller('CtrlCommodityUpdate', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', '$translate', 'MultipartForm', 'Store',
'Category', 'Kind', 'Size', 'Color', 'Commodity', 'Gallery',
    function($scope, $rootScope, $http, $window, $location, $routeParams, $translate,
    MultipartForm, Store, Category, Kind, Size, Color, Commodity, Gallery) {
        /* Updating commodity data and manage photos */
        $scope.wait = false;
        /* First of all query the Commodity */
        $scope.commodity = Commodity.get({pk: $routeParams.pk },
            function(success){
                success.year = Number(success.year);

                if(success.store != $rootScope.visitor.store){
                    // If user is not store owner then we redirect it to other safe page.
                    $location.path('/');
                }
                else{
                    // In other case we start performing queries to retrieve a reference data.
                    $scope.category_list = Category.query(function(success){
                        $scope.get_kind_list();
                    });
                    $scope.brand_list = Store.my_brands();
                    $scope.size_list = Size.query();
                    $scope.color_list = Color.query();
                    $scope.photo_list = Gallery.query({commodity: success.id},
                        get_free_photo_list
                    );

                }
            }

        );

        function get_free_photo_list(photo_list){
            /*Make a new dummy list to generate file inputs after photo list received */
            var photo_limit = 5;
            var extra_length = photo_limit - photo_list.length;
            $scope.free_photo_list = [];
            var i = 0;
            for (i; i < extra_length; i++){ $scope.free_photo_list.push(i);}

        };


        $scope.get_kind_list = function(clear){
            if ($scope.commodity.category){
                $scope.kind_list = Kind.query({category: $scope.commodity.category});
                if (clear){
                    $scope.commodity.kind = null;
                };
            }
        };

        $translate(['COMMODITY.SEASONS.WINTER',
                    'COMMODITY.SEASONS.SPRING',
                    'COMMODITY.SEASONS.SUMMER',
                    'COMMODITY.SEASONS.AUTUMN',
                    ])
        .then(function (translations) {
            $scope.season_list = [
                {id: 0, title: translations['COMMODITY.SEASONS.WINTER']},
                {id: 1, title: translations['COMMODITY.SEASONS.SPRING']},
                {id: 2, title: translations['COMMODITY.SEASONS.SUMMER']},
                {id: 3, title: translations['COMMODITY.SEASONS.AUTUMN']}
            ];
        });

        $scope.add_photo = function() {
            $scope.wait = true;
            var url = '/catalog/galleries/save_many/';
            MultipartForm('POST', '#photo_form', url).then(function(response) {
                    /*Success*/
                    $scope.photo_list = $scope.photo_list.concat(response.data);
                    get_free_photo_list($scope.photo_list);
                    $translate('COMMODITY.UPDATE.SUCCESS').then(function (msg) {
                        $rootScope.alerts.push({ type: 'info', msg:  msg});
                    });
                    clear_inputs();
                    //$location.path('/commodities/'+$scope.commodity.id+'/edit/');
                    $scope.wait = false;
                },
                function(error) {
                    $scope.error = error.data;
                    $scope.wait = false;
                }
            );
        };

        $scope.update = function (){
            $scope.wait = true;
            if ($scope.error){
                $scope.error = [];
            }
            $scope.commodity = Commodity.update({pk: $routeParams.pk},
            $scope.commodity, function(success){
                $translate('COMMODITY.UPDATE.SUCCESS').then(function (msg) {
                    $rootScope.alerts.push({ type: 'info', msg:  msg});
                });
                $scope.wait = false;
            },
            function(error){
                $scope.error = error.data;
                $scope.wait = false;
            }
            );
        };

        $scope.remove_photo = function(photo){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    Gallery.remove({pk: photo.id},
                        function(success){
                            var index = $scope.photo_list.indexOf(photo);
                            $scope.photo_list.splice(index, 1);
                            get_free_photo_list($scope.photo_list);
                        },
                        error_handler
                    );
                }
            });
        };
        $scope.remove_commodity = function(){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    Commodity.remove({pk: $scope.commodity.id},
                        function(success){
                            $location.path('/');
                        },
                        error_handler
                    );
                }
            });
        };

        function error_handler(){
            $translate('ERROR').then(function (msg) {
                $rootScope.alerts.push({ type: 'info', msg:  msg});
            });
        }

        function clear_inputs(){
            var elements = document.querySelectorAll(".file");
            console.log(elements);
            angular.forEach(
                elements,
                function(input) {
                  angular.element(input).val(null);
                }
            );
        }
    }
])
.controller('CtrlMyCommodityList', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', '$translate', 'Store',
'Category', 'Kind', 'Size', 'Color', 'Commodity', 'Gallery', 'GetPageLink',
    function($scope, $rootScope, $http, $window, $location, $routeParams, $translate,
    Store, Category, Kind, Size, Color, Commodity, Gallery, GetPageLink) {
        /* Representation of the user`s (store`s) list of commodities */
        /* Later, need to add filter, search and navigation */
        $scope.r = Store.my_commodities($routeParams, function(success){
            $scope.enough = success.total > 1 ? false : true;
            $scope.page_link = GetPageLink();
            $scope.page = success.current;
            $scope.prev_pages = [];
            $scope.next_pages = [];
            var i = (success.current - 1 > 5) ? success.current - 5: 1;
            var next_lim = (success.total - success.current > 5) ? 5 + success.current : success.total;
            var j = success.current + 1;
            for (i; i < success.current; i++){ $scope.prev_pages.push(i);}
            for (j; j <= next_lim; j++){ $scope.next_pages.push(j);}
        });

        $scope.get_more = function(){
            $scope.page += 1;
            var params = $routeParams;
            params['page'] = $scope.page;
            Store.my_commodities(params, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                },
                function(error){
                    $scope.e = error.data.detail;
                }
            );
        }

        $scope.remove_commodity = function(index){
            $translate('CONFIRM').then(function (msg) {
                $scope.confirm = $window.confirm(msg);
                if ($scope.confirm){
                    commodity = $scope.r.results[index];
                    Commodity.remove({pk: commodity.id},
                        function(success){
                            $scope.r.results.splice(index, 1);
                        },
                        error_handler
                    );
                }
            });
        };

        function error_handler(){
            // TODO: remove duplicates
            $translate('ERROR').then(function (msg) {
                $rootScope.alerts.push({ type: 'info', msg:  msg});
            });
        }
    }
])
.controller('CtrlCommodityDetail', ['$scope', '$rootScope','$http',
'$location', '$routeParams', '$translate', 'Commodity',
    function($scope, $rootScope, $http, $location, $routeParams, $translate,
    Commodity) {
        $scope.commodity = Commodity.verbose({pk: $routeParams.pk});

    }
])
.controller('CtrlCommodityList', ['$scope', '$rootScope','$http', '$window',
'$location', '$routeParams', '$translate', 'Store',
'Category', 'Kind', 'Size', 'Color', 'Commodity', 'Gallery', 'GetPageLink',
    function($scope, $rootScope, $http, $window, $location, $routeParams, $translate,
    Store, Category, Kind, Size, Color, Commodity, Gallery, GetPageLink) {
        /* Representation of the user`s (store`s) list of commodities */
        /* Later, need to add filter, search and navigation */
        $scope.r = Commodity.query($routeParams, function(success){
            $scope.enough = success.total > 1 ? false : true;
            $scope.page_link = GetPageLink();
            $scope.page = success.current;
            $scope.prev_pages = [];
            $scope.next_pages = [];
            var i = (success.current - 1 > 5) ? success.current - 5: 1;
            var next_lim = (success.total - success.current > 5) ? 5 + success.current : success.total;
            var j = success.current + 1;
            for (i; i < success.current; i++){ $scope.prev_pages.push(i);}
            for (j; j <= next_lim; j++){ $scope.next_pages.push(j);}
        });

        $scope.get_more = function(){
            $scope.page += 1;
            var params = $routeParams;
            params['page'] = $scope.page;
            Store.my_commodities(params, function(success){
                    $scope.r.results = $scope.r.results.concat(success.results);
                    $scope.enough = ($scope.page >= $scope.r.total) ? true : false;
                },
                function(error){
                    $scope.e = error.data.detail;
                }
            );
        }
    }
]);
