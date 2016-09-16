angular.module('commodity.directives', ['commodity.services'])
    .directive('stockSet', ['PATH', 'Color', 'Size',
        function(PATH) {
            return {
                restrict: 'AC',
                scope: {
                    stockstr: '=',
                    category: '=',
                },
                templateUrl: PATH + 'commodity/templates/include/stock_set_create.html',
                controller: function($scope, Color, Size) {

                    $scope.color_list = Color.query();

                    $scope.$watch('category',
                        function(newValue, oldValue) {
                            if (newValue){
                                $scope.size_list = Size.query({category: $scope.category});
                            }
                        }
                    );

                    $scope.placeholder_list = [{
                        color: null,
                        size: null,
                        amount: 0
                    }];

                    $scope.refresh_stock_set = function() {
                        var data = $scope.placeholder_list.slice(),
                            len = data.length,
                            i = 0;
                        for (i; i < len; i++) {
                            if (data[i]['size'] == null && data[i]['color'] == null) {
                                data.splice(i, 1);
                            }
                        }
                        $scope.stockstr = angular.toJson(data);

                    };

                    $scope.add_stock = function() {
                        $scope.placeholder_list.push({
                            color: null,
                            size: null,
                            amount: 0
                        });
                    };
                }
            }
        }

    ])
    .directive('stockSetUpdate', ['PATH', 'Color', 'Size', 'Commodity', 'Stock',
        function(PATH) {
            return {
                restrict: 'AC',
                scope: {
                    stockset: '=',
                    commodity: '=',
                    category: '=',
                },
                templateUrl: PATH + 'commodity/templates/include/stock_set_update.html',
                controller: function($scope, Color, Size, Commodity, Stock) {
                    $scope.color_list = Color.query();


                    $scope.$watch('category',
                        function(newValue, oldValue) {
                            if (newValue){
                                $scope.size_list = Size.query({category: $scope.category});
                            }
                        }
                    );



                    $scope.add_stock = function() {
                        $scope.stockset.push({
                            color: null,
                            size: null,
                            amount: 0
                        });
                    };

                    $scope.update = function() {
                        // TODO: Write error handler
                        var data = $scope.stockset,
                            len = data.length,
                            i = 0;
                        for (i; i < len; i++) {
                            if (data[i]['size'] == null && data['color'] == null) {
                                data.splice(i, 1);
                            }
                        }

                        Commodity.update_stocks({
                                pk: $scope.commodity
                            }, data,
                            function(success) {
                                console.log('SUCCESS');
                            }
                        );

                    };

                    $scope.remove = function(index) {
                        stock = $scope.stockset[index];
                        if (stock.hasOwnProperty('id')) {
                            Stock.remove({
                                    pk: stock.id
                                },
                                function(success) {
                                    $scope.stockset.splice(index, 1);
                                }
                            );

                        } else {
                            $scope.stockset.splice(index, 1);
                        }

                    };
                }
            }
        }

    ]);
