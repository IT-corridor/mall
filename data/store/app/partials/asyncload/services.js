angular.module('asyncload.services', [])
.factory('LoadScript', ['$window', '$document', '$q', '$timeout', '$rootScope',
function($window, $document, $q, $timeout, $rootScope){
    /* This factory allow to load scripts asynchronous */
    return function (src, callback_name, is_api) {

        if (!$rootScope.deferedScripts){
          $rootScope.deferedScripts = [];
        }
        var i = 0, l = $rootScope.deferedScripts.length;

        for (i; i < l; i++ ){
          if ($rootScope.deferedScripts[i][0] == src){
            return $rootScope.deferedScripts[i][1];
          }
        }


        var deferred = $q.defer();
        $rootScope.deferedScripts.push([src, deferred.promise]);

        var doc = $document[0];
        var scripts = doc.querySelectorAll('script');


        angular.forEach(scripts,
            function(script) {
                if (script.src == src){
                    deferred.resolve();
                }
            }
        );
        if (deferred.promise.$$state.status == 0){
            var script = doc.createElement('script');
            script.src = src;
            script.onload = function (e) {
                $timeout(function () {
                    if (!is_api){
                        deferred.resolve(e);
                    }

                });
            };
            script.onerror = function (e) {
                $timeout(function () {
                    deferred.reject(e);
                });
            };
            doc.body.appendChild(script);
        }

        $window[callback_name] = function(){
            /* A small trick for api loaders trick.
            It will be called when the api script (not actual script) will be ready */
            deferred.resolve();
        }

        return deferred.promise;
    }
}]);