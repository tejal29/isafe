// Provide access token
L.mapbox.accessToken = 'pk.eyJ1Ijoic2hhYmVtZGFkaSIsImEiOiIwckNSMkpvIn0.MeYrWfZexYn1AwdiasXbsg';

// Set up map characteristics and layers
var map = L.mapbox.map('map', 'shabemdadi.mmmfifm9')
        .addLayer(L.mapbox.tileLayer('shabemdadi.mmmfifm9'))
        .addControl(L.mapbox.geocoderControl('shabemdadi.mmmfifm9', { //user can enter in address
        autocomplete: true                                      // address will be autocompleted    
            }));
        L.control.locate().addTo(map); //allows user to locate themselves

console.log("map is set up");

// Set location to be San Francisco
var geocoder = L.mapbox.geocoder('mapbox.places');