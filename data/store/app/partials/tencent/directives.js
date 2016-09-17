angular.module('tencent', [])
.directive('mapCoords', function() {
  return {
    restrict: 'AC',
    scope: {
      title: '=',
      lat: '=',
      lon: '='
    },
    link: function(scope, element, attrs) {
      // Set up center coordinates
      var center = new qq.maps.LatLng(scope.lat, scope.lon);
      var container = element[0];
      var map = new qq.maps.Map(container, {
        center: center,
        zoom: 16
      });
      var marker = new qq.maps.Marker({
        position: center,
        map: map
      });

      //marker.setAnimation(qq.maps.MarkerAnimation.DOWN);

      var anchor = new qq.maps.Point(16, 32),
        size = new qq.maps.Size(32, 32),
        origin = new qq.maps.Point(0, 0),
        icon = new qq.maps.MarkerImage(
          "http://i.imgur.com/vafhQrk.png",
          size,
          origin,
          anchor
        );

      marker.setIcon(icon);
      //Title visible on marker hover
      marker.setTitle(scope.title);

      var info = new qq.maps.InfoWindow({
        map: map
      });
      //open popup on with map initialization
      info.open();
      info.setContent('<span style="color: darkred; padding: 10px;">' + scope.title + '</span>');
      info.setPosition(marker.getPosition());
      //scope.$apply();

    },
  };
})
.directive('mapAddress', ['LoadScript', function(LoadScript) {
  return {
    restrict: 'AC',
    scope: {
      title: '=',
      address: '=',
      img: '=',
    },
    link: function(scope, element, attrs) {
      // Set up center coordinates
      var callback_name = 'init_lazy';
      var script = new LoadScript('http://map.qq.com/api/js?v=2.exp&callback='+callback_name, callback_name, true);
      var unwatch = scope.$watch('address', function(newValue, oldValue) {
          if (newValue){
            script.then(function(success){
                render_map();
            });

            unwatch();
          }
      });
      function render_map(){
        var geocoder = new qq.maps.Geocoder();
        var container = element[0];
        var map, marker = null;
        geocoder.getLocation(scope.address);

        geocoder.setComplete(function(result) {
        map = new qq.maps.Map(container, {
          center: result.detail.location,
          zoom: 16,
          zoomControl: false,
          panControl: false,
          mapTypeControl: false,
        });

        marker = new qq.maps.Marker({
          map: map,
          position: result.detail.location
        });

        marker.setTitle(scope.address);

        var info = new qq.maps.InfoWindow({
          map: map
        });
        info.open();
        info.setContent('<span style="color: darkred; padding: 10px;"> <img style="width: 48px; height: auto; margin-right: 5px;" src="'+scope.img+ '"> ' +scope.title + '</span>');
        info.setPosition(marker.getPosition());
        scope.$apply();

        });

        geocoder.setError(function() {
          console.log("Error! Wrong address!");
          scope.$apply();
        });

      }

    },
  };
}]);
