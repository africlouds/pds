tracking = function(page) {
	var markerCount = 0;
	var map;

	//Initializes the map…
	function initialize() {
	    var myLatlng = new google.maps.LatLng(46.855141, -96.8372664);
	    var map_canvas = $('#map-canvas');
	    var map_options = {
		center: myLatlng,
		zoom: 5,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	    }
	    map = new google.maps.Map(map_canvas, map_options);
	}    

	//When the window is loaded, run the initialize function to
	//setup the map
	google.maps.event.addDomListener(window, 'load', initialize);    

	//This function will add a marker to the map each time it 
	//is called.  It takes latitude, longitude, and html markup
	//for the content you want to appear in the info window 
	//for the marker.
	function addMarkerToMap(lat, long, htmlMarkupForInfoWindow){
	    var infowindow = new google.maps.InfoWindow();
	    var myLatLng = new google.maps.LatLng(lat, long);
	    var marker = new google.maps.Marker({
		position: myLatLng,
		map: map,
		animation: google.maps.Animation.DROP,
	    });
	    
	    //Gives each marker an Id for the on click
	    markerCount++;

	    //Creates the event listener for clicking the marker
	    //and places the marker on the map 
	    google.maps.event.addListener(marker, 'click', (function(marker, markerCount) {
		return function() {
		    infowindow.setContent(htmlMarkupForInfoWindow);
		    infowindow.open(map, marker);
		}
	    })(marker, markerCount));  
	    
	    //Pans map to the new location of the marker
	    map.panTo(myLatLng)        
	}
}
