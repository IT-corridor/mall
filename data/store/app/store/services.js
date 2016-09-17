angular.module('store.services', ['ngResource'])
    .constant('store_path', 'account/stores/')
    .constant('catalog_path', 'catalog/')
    .factory('Store', ['$resource', 'store_path', 'API',
        function ($resource, store_path, API) {
            return $resource(API + store_path + ':pk/:action/', {}, {
                query: {method: 'GET', params: {pk: null, action: null}, responseType: 'json'},
                update: {method: 'PATCH'},
                save: {method: 'POST'},
                remove: {method: 'DELETE'},
                my_store: {method: 'GET', params: {pk: null, action: 'my_store'}, responseType: 'json'},
                overview: {method: 'GET', params: {action: 'overview'}, responseType: 'json'},
                my_brands: {method: 'GET', params: {pk: null, action: 'my_brands'}, responseType: 'json', isArray: true},
                my_commodities: {method: 'GET', params: {pk: null, action: 'my_commodities'}, responseType: 'json'},
                commodities: {method: 'GET', params: {action: 'commodities'}, responseType: 'json', isArray: true},
                update_photo: {method: 'PATCH', params: {action: 'update_photo'}, responseType: 'json'},
            });
        }]);