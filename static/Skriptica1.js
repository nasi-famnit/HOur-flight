var dataFromGoogle = "";
var globalPosID = "";
var globalDestID = "";
function getFlightInfo(posID, destID)
{
var tmpPos = posID;
posID = destID;
destID = tmpPos;
console.log(posID + " " + destID);
var today = new Date();
var dd = today.getDate();
var mm = today.getMonth()+1; //January is 0!
var yyyy = today.getFullYear();

if(dd<10) {
    dd='0'+dd
} 

if(mm<10) {
    mm='0'+mm
} 

var datum = yyyy+'-'+mm+'-'+dd;
var dataObject = {
  "request": {
    "passengers": {
      "adultCount": 1
    },
    "slice": [
      {
        "origin": posID,
        "destination": destID,
        "date": datum,
        "maxStops": 1
      }
    ]
  }
};

$.ajax({
     type: "POST",
     //Set up your request URL and API Key.
     url: "https://www.googleapis.com/qpxExpress/v1/trips/search?key=AIzaSyBhwl24hGaUn1K7HJmNoKmWdj2wITW6t3s", 
     contentType: 'application/json', // Set Content-type: application/json
     dataType: 'json',
     data: JSON.stringify(dataObject),
     success: function (data) {
      if(data == null || data.trips == null || data.trips.tripOption == null)
      {
          alert("There is no direct flights between " + posID + " and " + destID);
          console.log("No info about your flights");
          return;
      }
      dataFromGoogle = data;
      var allFlights = data.trips.tripOption;
      console.log(allFlights.length);
      var validFlights = 0;
      for(i = 0; i < allFlights.length; i=i+1)
      {

          var segments = allFlights[i].slice[0].segment;
          //console.log(i);
          if(segments.length == 1)
          {
              validFlights ++;
              var idStr = "red".concat(i.toString());
              $("#tableId").append("<tr id="+idStr+" class=info style='cursor:pointer;'></tr>");
              var desc = segments[0].leg[0];
              var temporary = desc.departureTime.split("T");
              var printTime = "";
              printTime += temporary[1].substring(0,5) + " (";
              printTime += temporary[1].substring(5,temporary[1].length) + ") (" + temporary[0] +")";

              $("#"+idStr).append("<td>" + printTime + "</td>");
              $("#"+idStr).append("<td>" + desc.aircraft + "</td>");
              $("#"+idStr).append("<td>" + segments[0].flight.carrier + "</td>");
              $("#"+idStr).append("<td>" + segments[0].flight.number + "</td>");
              $("#"+idStr).append("<td>" + desc.originTerminal + "</td>");
          }
      }
      if(validFlights == 0)
      {
          alert("There is no direct flights between " + posID + " and " + destID);
      }
      console.log("Finished");
    },
      error: function(){
       alert("Access to Google QPX Failed.");
     }
    });
}



function findFlights()
{

    $posID = $('#select-to1')[0].selectize.getValue();
    $destID = $('#select-to')[0].selectize.getValue();
    if($posID == "" && $destID == "")
    {
        if(globalPosID != "" && globalDestID != "")
        {
            var temp = globalPosID.split(" ");
            $posID = temp[temp.length -1];
            temp = globalDestID.split(" ");
            $destID = temp[temp.length-1];
            getFlightInfo($posID, $destID);
        }
        return;
    }
    else if($posID != "" && $destID == "")
    {
        if(globalDestID != "")
        {
          var temp = globalDestID.split(" ");
          $destID = temp[temp.length-1];
          getFlightInfo($posID, $destID);
        }
        return;
    }
    else if($posID == "" && $destID != "")
    {
        if(globalPosID != "")
        {
            var temp = globalPosID.split(" ");
            $posID = temp[temp.length -1];
            getFlightInfo($posID, $destID);
        }
    }
    else
    {
        getFlightInfo($posID, $destID);
    }
    
}

document.onreadystatechange = function () {
    $('table').on('click', 'tr' , function (event) {
      var tmp = $(this).attr("id");
      var i = parseInt(tmp.substring(3,tmp.length));
      flightSelected(i);
    });

    $('.depBtn').click(function(){
        globalPosID = $(this).find("p").text();
        //$('#select-to1')[0].selectize.setValue($selectedAir);
    });

    $('.arrBtn').click(function(){
        globalDestID = $(this).find("p").text();
    });
}

function flightSelected(flightID)
{
    //alert(flightID);
    //var id = dataFromGoogle.tripOption[flightID].slice[0].segment[0].leg[0].origin
    var origin = dataFromGoogle.trips.tripOption[flightID].slice[0].segment[0].leg[0].origin;
    if(!(origin in airportsDB))
    {
        alert("Error: There is no airport in database");
        return;
    }
    var destination = dataFromGoogle.trips.tripOption[flightID].slice[0].segment[0].leg[0].destination;
    var departureTime = dataFromGoogle.trips.tripOption[flightID].slice[0].segment[0].leg[0].departureTime;
    var distance = dataFromGoogle.trips.tripOption[flightID].slice[0].segment[0].leg[0].mileage;
    
    var longitude = airportsDB[origin].lon;
    var latitude = airportsDB[origin].lat;
    var requestURL = "http://192.168.0.165:5000/predict?origin="+origin+
        "&destination="+destination+"&distance="+distance+"&departureTime="+departureTime+
        "&longitude="+longitude+"&latitude="+latitude;
    //alert(origin + " " + destination + " " + departureTime + " " + distance + " " + longitude + " " + latitude);
    getTimeDelay(requestURL, null);
    
    console.log(requestURL);
}

function getTimeDelay(requestURL, outputID)
{
    $.ajax({
     type: "GET",
     //Set up your request URL and API Key. // Set Content-type: application/json
     dataType: 'jsonp',
     crossOrigin: true,
     url: requestURL, 
     success: function (data) {
      //$("#probabHolder").text("Probability: " + data.prob);
      var prob = parseFloat(data.prob);
      prob = 1-prob;
      $("#probModal").modal('show');
      console.log(Math.floor(prob*100));
      if(Math.floor(prob*100) < 72)
      {
          $("#probHolder").addClass('progress-bar-warning');
      }
      else
      {

        $("#probHolder").addClass('progress-bar-info');
      }
      $("#probHolder").text(Math.floor(prob*100).toString()+"%");
      $(".progress-bar").animate({width: Math.floor(prob*100).toString()+"%"}, 2500);
      console.log("Done!");
      //alert("Probability for delay: " + data.prob);
    },
      error: function(){
       alert("Access to the system failed");
     }
    });
}

function findFlightsByID(flightID)
{
    
}

function nearestLocationDep()
{

}

 