angular.module('dashboard.controllers', ['dashboard.services', 'ui.load', 'ui.jq'])
    .constant('JQ_CONFIG', {
        plot: ['../static/lib/jquery/flot/jquery.flot.js',
            '../static/lib/jquery/flot/jquery.flot.pie.js',
            '../static/lib/jquery/flot/jquery.flot.resize.js',
            '../static/lib/jquery/flot.tooltip/js/jquery.flot.tooltip.min.js',
            '../static/lib/jquery/flot.orderbars/js/jquery.flot.orderBars.js',
            '../static/lib/jquery/flot-spline/js/jquery.flot.spline.min.js'],
    })
    .controller('CtrlFlotChart', ['$scope', '$rootScope', 'Dashboard',
        function ($scope, $rootScope, Dashboard) {
            $rootScope.data = {};
            $scope.data.year = 2016;
            $scope.data.month = 8;
            $scope.years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];
            $scope.months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

            $scope.date_change = function () {
                refresh();
            }
            refresh();

            function refresh() {
                Dashboard.store_followers({year: $scope.data.year, month: $scope.data.month}, function (success) {
                    $scope.data.store_followers = success;
                });
                Dashboard.group_followers({year: $scope.data.year, month: $scope.data.month}, function (success) {
                    $scope.data.group_followers = success;
                    $scope.data.groups = Object.keys($scope.data.group_followers);
                    // remove $promise, $resolved
                    $scope.data.groups.splice($scope.data.groups.length-2, 2);
                    $scope.data.group_now = $scope.data.groups[0];
                });
                Dashboard.photo_fans({year: $scope.data.year, month: $scope.data.month}, function (success) {
                    $scope.data.photo_fans = success;
                    $scope.data.photos = Object.keys($scope.data.photo_fans);
                    // remove $promise, $resolved
                    $scope.data.photos.splice($scope.data.photos.length-2, 2);
                    $scope.data.photo_now = $scope.data.photos[0];
                });
                Dashboard.photo_clones({year: $scope.data.year, month: $scope.data.month}, function (success) {
                    $scope.data.photo_clones = success;
                    $scope.data.photos_c = Object.keys($scope.data.photo_clones);
                    // remove $promise, $resolved
                    $scope.data.photos_c.splice($scope.data.photos_c.length-2, 2);
                    $scope.data.photo_c_now = $scope.data.photos_c[0];
                });
            }
        }]);
