angular.module('store.services', ['ngResource'])
.constant('store_path', '/account/stores/')
.constant('catalog_path', '/catalog/')
.factory('Store', ['$resource', 'store_path',
    function($resource, store_path){
        return $resource(store_path + ':pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
            my_store: {method:'GET', params:{pk: null, action: 'my_store'}, responseType:'json'},
            overview: {method:'GET', params:{action: 'overview'}, responseType:'json'},
            my_brands: {method:'GET', params:{pk: null, action: 'my_brands'}, responseType:'json', isArray: true},
            my_colors: {method:'GET', params:{pk: null, action: 'my_colors'}, responseType:'json', isArray: true},
            my_sizes: {method:'GET', params:{pk: null, action: 'my_sizes'}, responseType:'json', isArray: true},
            my_commodities: {method:'GET', params:{pk: null, action: 'my_commodities'}, responseType:'json', isArray: true},
            commodities: {method:'GET', params:{action: 'commodities'}, responseType:'json', isArray: true},
            update_photo: {method:'PATCH', params:{action: 'update_photo'}, responseType:'json'},

    });
}])
.factory('Category', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'categories/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Kind', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'kinds/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Brand', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'brands/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Size', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'sizes/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Color', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'colors/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            update: {method: 'PATCH'},
            save: {method: 'POST'},
            remove: {method: 'DELETE'},
    });
}])
.factory('Commodity', ['$resource', 'catalog_path',
    function($resource, catalog_path){
        return $resource(catalog_path + 'commodities/:pk/:action/', {}, {
            query: {method:'GET', params:{pk: null, action: null}, responseType:'json'},
            verbose: {method: 'GET', params: {action: 'verbose'}, responseType: 'json'},
            nearby_stores: {method: 'GET', params: {action: 'nearby_stores'}, responseType: 'json', isArray: true},
    });
}]);