angular.module('common.services', ['ngResource'])
.factory('PopParamString', function(){
    return function (obj, key) {
        if (Object.keys(obj).length == 0){ return '';}
        var str = [];
        for(var p in obj){
            /* Maybe needs to fix */
            if (p != key) {
                str.push(encodeURIComponent(p) + '=' + encodeURIComponent(obj[p]));
            }
        }
        return str.join('&');
    }
})
.factory('GetPageLink',['PopParamString', '$location',
    function(PopParamString, $location){
        return function(){
            var page_link = '#!' +$location.path() + '/?';
            var url_params = PopParamString($location.search(), 'page');
            page_link += url_params ? url_params +'&' : ''
            return page_link;
        }
    }
])
.factory('IsMember',
    function(){
         return function(list, id, fieldname){
            if (fieldname === undefined){
                field = 'visitor';
            }
            else{
                field = fieldname;
            }
            var i = 0;
            for (i; i < list.length; i++){
                if (list[i][field] == id){
                    return true;
                }
            }
            return false;
        }
    }
)
.factory('RemoveItem',
    function(){
        return function (list, id, fieldname){
            var i = 0;
            if (!fieldname){
                var fieldname = 'id';
            }
            /* Check this */
            for (i; i < list.length; i++){
                if (list[i][fieldname] == id){
                    list.splice(i, 1);
                    break;
                }
            }
        }
    }
)
.factory('MultipartForm', ['$http', function ($http){
    return function(method, form_id, url){
        if (form_id){
            var form = document.querySelector(form_id);
            var formData = new FormData(form);
        }
        else{
            var formData = null;
        }
        var req = {
            method: method,
            url: url,
            headers: {'Content-Type': undefined, 'X-Requested-With': 'XMLHttpRequest'},
            data: formData,
        };
        return $http(req);
    }
}])
.factory('WindowScroll', ['$window', function($window){
    // Perform action when scroll touch the document bottom
    return function(scope, callback){
        var window = angular.element($window);

        function scroll_more(){
            if (!scope.enough && scope.page != undefined){
                var bodyHeight = this.document.body.scrollHeight;
                if (bodyHeight == (this.pageYOffset + this.innerHeight)){
                    callback();
                }
            }
        }
        window.bind('scroll', scroll_more);

        scope.$on('$destroy', function(e){
            window.unbind('scroll', scroll_more);
        });
    }

}]);
