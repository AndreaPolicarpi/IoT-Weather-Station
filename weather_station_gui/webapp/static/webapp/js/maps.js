// Initialize and add the map
function initMap(marker_list) {

  var jsonData = JSON.parse(document.querySelector('#jsonData').getAttribute('data-json'));

  var lat = jsonData.map((item) => item.lat);
  var long = jsonData.map((item) => item.long);
  var sensor_id = jsonData.map((item) => item.value);

  console.log(lat);
  console.log(long);
  console.log(parseFloat(lat[0]))

  // The location of Italy
  const italy = { lat: 41.90, lng: 13.29 }; //42.40461698248025, 13.294311585536779
  // The map, centered at Italy
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 5.4,
    center: italy,
  });

  for (let i = 0; i < lat.length; i++) {
    // The marker, positioned at Uluru
    var marker = new google.maps.Marker({
      position: { lat: parseFloat(lat[i]), lng: parseFloat(long[i]) },
      map: map,
      title: sensor_id[i]
    });

    var infowindow = new google.maps.InfoWindow({
      content: sensor_id[i]
    });

    // Now we are inside the closure or scope of this for loop,
    // but we're calling a function that was defined in the global scope.
    addMarkerListener(marker, infowindow, marker.title);

  }
}

function addMarkerListener(marker, infowindow, sensor_id) {

  marker.addListener('mouseover', function (e) {
    infowindow.open(map, marker);
  });

  marker.addListener('mouseout', function () {
    infowindow.close();
  });

  marker.addListener('click', function () {
    window.location = "/webapp/" + sensor_id + "/";
  });
}