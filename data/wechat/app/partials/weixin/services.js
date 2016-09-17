angular.module('weixinapi', [])
.factory('Signature', ['$resource', 'API',
    function($resource, API){
        return $resource(API + 'api/v1/signature', {}, {
            get: {method:'GET', responseType:'json'},
        });
    }
])
.factory('WXI', ['$rootScope', '$window', '$q', 'Signature',
function($rootScope, $window, $q, Signature){
    var loc = $window.location.href;
    var defer = $q.defer();
    var WXI = {};

    Signature.get({location: loc}, function (success){
        var tmp;
        tmp = wx.config({
            debug: false,
            appId: success.appId,
            timestamp: success.timestamp,
            nonceStr: success.noncestr,
            signature: success.signature,
            jsApiList: ['getLocation',
                        'onMenuShareTimeline',
                        'onMenuShareAppMessage']
        });

        defer.resolve(tmp);

        wx.error(function(res){
            $rootScope.error = res;
            $rootScope.$apply();
        });
    });

    WXI.get_location = function(){
        var inner = $q.defer();
        defer.promise.then(function success(){

            wx.getLocation({
                success: function (res) {
                    inner.resolve({latitude: res.latitude, longitude: res.longitude});
                }
            });
        });
        return inner.promise;
    };
    WXI.set_on_share = function(description, image_url){
        defer.promise.then(function success(){
            var page_title = '@衣橱：女神岂能随意——非常有趣的掌上衣橱！';

            wx.onMenuShareTimeline({
                title: page_title, // Sharing title
                //link: '', // Sharing link
                imgUrl: image_url, // Sharing image URL
                success: function () {
                    // Callback function executed after a user confirms sharing
                    $rootScope.alerts.push({ type: 'info', msg: '成功'});
                    $rootScope.$apply();
                }

            });

            wx.onMenuShareAppMessage({
                title: page_title, // Sharing title
                desc: description, // Sharing description
                imgUrl: image_url, // Sharing image URL
                success: function () {
                    $rootScope.alerts.push({ type: 'info', msg: '成功'});
                    $rootScope.$apply();
                }
            });

        });
    }


    return WXI;
}]);
