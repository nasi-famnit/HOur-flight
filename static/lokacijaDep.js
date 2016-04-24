function getLocation() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        //x.innerHTML =
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition(position) {
    var latlon = position.coords.latitude + "," + position.coords.longitude;
    var prazan = [];
    //var img_url = "http://maps.googleapis.com/maps/api/staticmap?center="
    //+ latlon + "&zoom=14&size=400x300&sensor=false";
    //document.getElementById("mapholder").innerHTML = "<img src='" + img_url + "'>";
    //alert(position.coords.latitude + "," + position.coords.longitude);
    getJson(prazan, position.coords.latitude, position.coords.longitude);
    document.getElementById("dep1").innerHTML = prazan[0].name + " - " + prazan[0].email;
    document.getElementById("dep2").innerHTML = prazan[1].name + " - " + prazan[1].email;
    document.getElementById("dep3").innerHTML = prazan[2].name + " - " + prazan[2].email;
    document.getElementById("dep4").innerHTML = prazan[3].name + " - " + prazan[3].email;
    document.getElementById("dep5").innerHTML = prazan[4].name + " - " + prazan[4].email;
}

function getLocation1() {

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition1, showError);
    } else {
        //x.innerHTML =
        alert("Geolocation is not supported by this browser.");
    }
}

function showPosition1(position) {
    var latlon = position.coords.latitude + "," + position.coords.longitude;
    var prazanArr = [];
    //var img_url = "http://maps.googleapis.com/maps/api/staticmap?center="
    //+ latlon + "&zoom=14&size=400x300&sensor=false";
    //document.getElementById("mapholder").innerHTML = "<img src='" + img_url + "'>";
    //alert(position.coords.latitude + "," + position.coords.longitude);
    getJson(prazanArr, position.coords.latitude, position.coords.longitude);
    document.getElementById("arr1").innerHTML = prazanArr[0].name + " - " + prazanArr[0].email;
    document.getElementById("arr2").innerHTML = prazanArr[1].name + " - " + prazanArr[1].email;
    document.getElementById("arr3").innerHTML = prazanArr[2].name + " - " + prazanArr[2].email;
    document.getElementById("arr4").innerHTML = prazanArr[3].name + " - " + prazanArr[3].email;
    document.getElementById("arr5").innerHTML = prazanArr[4].name + " - " + prazanArr[4].email;
}


function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            x.innerHTML = "User denied the request for Geolocation."
            break;
        case error.POSITION_UNAVAILABLE:
            x.innerHTML = "Location information is unavailable."
            break;
        case error.TIMEOUT:
            x.innerHTML = "The request to get user location timed out."
            break;
        case error.UNKNOWN_ERROR:
            x.innerHTML = "An unknown error occurred."
            break;
    }
}




