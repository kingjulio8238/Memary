function retrieveLocation(callback) {
  if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(function(position) {
          const latitude = position.coords.latitude;
          const longitude = position.coords.longitude;
          console.log("Location succesfully retrieved. Latitude = " + latitude + ", Longitude = " + longitude);
          // Call the callback function with the location data
          callback(latitude, longitude);
      }, function(error) {
          console.error("Error occurred in retrieving location: ", error);
          // Handle error or call the callback with null values
          callback(null, null);
      });
  } else {
      console.error("Geolocation is not supported by this browser.");
      callback(null, null);
  }
}