angular.module('commodity.services', ['ngResource'])
.constant('catalog_path', 'catalog/')
.factory('Category', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'categories/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Kind', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'kinds/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Brand', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'brands/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Promotion', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'promotions/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Size', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'sizes/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Color', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'colors/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Commodity', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'commodities/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH', params: {action: null}},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            verbose: {method: 'GET', params: {action: 'verbose'}, responseType: 'json'},
            my: {method: 'GET', params: {action: 'my'}, responseType: 'json'},
            update_stocks: {method: 'PATCH', params:{action: 'update_stocks'}, responseType:'json', isArray: true,},

    });
}])
.factory('Gallery', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'galleries/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH', params: {action: null}},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            save_many: {method: 'POST', params:{pk: null, action: 'save_many'}, responseType:'json', isArray: true,},
    });
}])
.factory('Stock', ['$resource', 'catalog_path', 'API',
    function($resource, catalog_path, API){
        return $resource(API + catalog_path + 'stocks/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json', isArray: true},
            update: {method: 'PATCH', params: {action: null}},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}]);
