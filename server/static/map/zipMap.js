var geoPath = "../static/map/coloradoZipGeo.json";
var dataPath = "/emissions/getZipData";

var map;
var CO2ePerPop;

/* -------------------- Map Styling including alternate style ------------------- */
var colorScale = {
  "#6C001D": 400,
  "#DB0006": 200,
  "#FD990A": 100,
  "#FECB6C": 70,
  "#FFFF0D": 60,
  "#FFFFB0": 50,
  "#C8FF60": 40,
  "#8AE407": 30,
  "#5F9D05": 20,
  "#3C6104": 10,
};
// var colorScale = {'#3C6104': 10, '#5F9D05': 20, '#8AE407': 30, '#C8FF60': 40, '#FFFFB0': 50, '#FFFF0D': 60, '#FECB6C': 70, '#FD990A': 100, '#DB0006': 200, '#6C001D': 2000}

// Primary map styling created with Google Maps
// Styling Wizard at https://mapstyle.withgoogle.com/
var style = [
  {
    featureType: "administrative.land_parcel",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "administrative.neighborhood",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "poi",
    elementType: "labels.text",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "poi.business",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "poi.park",
    elementType: "labels.text",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "road",
    elementType: "labels",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "road.arterial",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "road.highway",
    elementType: "labels",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "road.local",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
  {
    featureType: "water",
    elementType: "labels.text",
    stylers: [
      {
        visibility: "off",
      },
    ],
  },
];

/* -------------------  Define actual Google Maps object ------------------ */
// Helper function
function convertToNum(item) {
  if (isNaN(item) || item == null) {
    return 0;
  } else {
    return item;
  }
}

function initMap() {
  // Initialize map
  var map = new google.maps.Map(document.getElementById("map"), {
    zoom: 8,
    mapTypeControl: false,
    streetViewControl: false,
    styles: style,
  });

  // Center map using geocoding
  var geocoder = new google.maps.Geocoder();
  var address = "Colorado";
  geocodeAddress(geocoder, map, address);

  function geocodeAddress(geocoder, map, address) {
    geocoder.geocode({ address: address }, function (results, status) {
      if (status === "OK") {
        map.setCenter(results[0].geometry.location);
      } else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
  }

  /* -------------------------------- Load JSON and create color labels array------------------------------- */

  // Load GeoJSON that contains zip code boundaries and geographic information
  // NOTE: This uses cross-domain XHR, and may not work on older browsers.
  map.data.loadGeoJson(geoPath);

  //  Import data file
  fetch(dataPath)
    .then((response) => {
      return response.json();
    })
    .then(function (ghgData) {
      // Colorize zip code areas based on average CO2e emissions
      map.data.setStyle(function (feature) {
        for (item in ghgData) {
          // Search geoJSON zip boundries file for the matching ghgData zip code.  OnLogn
          if (
            ghgData[item].zip.toString() !=
            feature.getProperty("GEOID10").substring(2)
          ) {
            continue;
          } else {
            CO2ePerPop =
              (ghgData[item].aviation +
                ghgData[item].cement_and_manufacturing +
                ghgData[item].electricity_commercial +
                ghgData[item].electricity_industrial +
                ghgData[item].electricity_residential +
                ghgData[item].naturalGas_commercial +
                ghgData[item].naturalGas_industrial +
                ghgData[item].naturalGas_residential +
                ghgData[item].transportation_PV_diesel +
                ghgData[item].transportation_PV_gas +
                ghgData[item].transportation_trucks_diesel +
                ghgData[item].transportation_trucks_gas +
                ghgData[item].waste) /
              ghgData[item].population2018;

            colorKeys = Object.keys(colorScale);
            colorValues = Object.values(colorScale);

            var color;
            var i = 0;
            while (i < colorValues.length) {
              if (CO2ePerPop < colorValues[i]) {
                color = colorKeys[i];
              }
              i++;
            }
          }
        }
        return {
          fillColor: color,
          fillOpacity: 0.7,
          strokeWeight: 1,
          strokeColor: color,
        };
      });

      // When the user hovers, outline zip code area.
      map.data.addListener("mouseover", function (event) {
        map.data.revertStyle();
        map.data.overrideStyle(event.feature, {
          strokeWeight: 4,
          strokeColor: "gray",
        });
      });

      map.data.addListener("mouseout", function (event) {
        map.data.revertStyle();
      });

      /* ------------------------------- INFO PANEL ------------------------------ */

      // When the user selects a zip code area,
      // display info window with more detailed information
      var infowindow = new google.maps.InfoWindow();
      map.data.addListener("click", function (event) {
        createInfoWindow(map, event, infowindow);
      });

      function createInfoWindow(map, event) {
        // Get properties from Data Layer to populate info window
        var zip = event.feature.getProperty("GEOID10").substring(2);

        var city = "Unknown";
        var county = "Unknown";
        var population2018 = "Unknown";
        var transportation_PV_diesel = "Unknown";
        var transportation_PV_gas = "Unknown";
        var transportation_trucks_diesel = "Unknown";
        var transportation_trucks_gas = "Unknown";
        var electricity_commercial = "Unknown";
        var electricity_industrial = "Unknown";
        var electricity_residential = "Unknown";
        var naturalGas_commercial = "Unknown";
        var naturalGas_industrial = "Unknown";
        var naturalGas_residential = "Unknown";
        var waste = "Unknown";
        var cement_and_manufacturing = "Unknown";
        var aviation = "Unknown";

        for (item in ghgData) {
          if (
            ghgData[item].zip.toString() !=
            event.feature.getProperty("GEOID10").substring(2)
          ) {
            continue;
          } else {
            city = ghgData[item].city;
            county = ghgData[item].county;
            population2018 = ghgData[item].population2018;
            transportation_PV_diesel = ghgData[item].transportation_PV_diesel;
            transportation_PV_gas = ghgData[item].transportation_PV_gas;
            transportation_trucks_diesel =
              ghgData[item].transportation_trucks_diesel;
            transportation_trucks_gas = ghgData[item].transportation_trucks_gas;
            electricity_commercial = ghgData[item].electricity_commercial;
            electricity_industrial = ghgData[item].electricity_industrial;
            electricity_residential = ghgData[item].electricity_residential;
            naturalGas_commercial = ghgData[item].naturalGas_commercial;
            naturalGas_industrial = ghgData[item].naturalGas_industrial;
            naturalGas_residential = ghgData[item].naturalGas_residential;
            waste = ghgData[item].waste;
            cement_and_manufacturing = ghgData[item].cement_and_manufacturing;
            aviation = ghgData[item].aviation;

            var transportationTotal =
              transportation_PV_diesel +
              transportation_PV_gas +
              transportation_trucks_diesel +
              transportation_trucks_gas +
              aviation;

            var electricityTotal =
              electricity_commercial +
              electricity_industrial +
              electricity_residential;

            var naturalGasTotal = 
              naturalGas_commercial +
              naturalGas_industrial +
              naturalGas_residential;

            var wasteTotal = waste + cement_and_manufacturing;

            // CO2ePerPop = (
            //   aviation +
            //   cement_and_manufacturing+
            //   electricity_commercial+
            //   electricity_industrial+
            //   electricity_residential+
            //   naturalGas_commercial+
            //   naturalGas_industrial+
            //   naturalGas_residential+
            //   transportation_PV_diesel+
            //   transportation_PV_gas+
            //   transportation_trucks_diesel+
            //   transportation_trucks_gas+
            //   waste
            //   ) / population2018;

            break;
          }
        }

        // Create content for info window
        var contentString =
          '<div id="infoWindow"><div id="siteNotice"></div>' +
          '<h2 id="infoWindowHeader" class="infoWindowText">Zip code: ' +
          zip +
          "</h2>" +
          '<h3 class="infoWindowText">City: ' +
          city +
          "</h3>" +
          '<h3 class="infoWindowText">County: ' +
          county +
          "</h3>" +
          '<h3 class="infoWindowText">Population: ' +
          population2018 +
          "</h3>" +
          '<h3 class="infoWindowText">Average CO<sub>2</sub>e Per Person: ' +
          CO2ePerPop.toFixed(2) +
          "</h3>" +
          // '<div id="bodyContent" style="font-size: 12pt;" >'+
          // '</br>Transportation Cars Using Diesel: ' + `<b>${transportation_PV_diesel}</b> Metric Tons CO2e/ Year` +
          // '</br>Transportation Cars Using Gas: ' + `<b>${transportation_PV_gas}</b> Metric Tons CO2e/ Year` +
          // '</br>Transportation Trucks Using Diesel: ' + `<b>${transportation_trucks_diesel}</b> Metric Tons CO2e/ Year` +
          // '</br>Transportation Trucks Using Gas: ' + `<b>${transportation_trucks_gas}</b> Metric Tons CO2e/ Year` +

          // '</br>Electricity Commercial Sector: '+ `<b>${electricity_commercial}</b> Metric Tons CO2e/ Year` +
          // '</br>Electricity Industrial Sector: '+ `<b>${electricity_industrial}</b> Metric Tons CO2e/ Year` +
          // '</br>Electricity Residential Sector: '+ `<b>${electricity_residential}</b> Metric Tons CO2e/ Year` +

          // '</br>Natural Gas Commercial Sector: '+ `<b>${naturalGas_commercial}</b> Metric Tons CO2e/ Year` +
          // '</br>Natural Gas Industrial Sector: '+ `<b>${naturalGas_industrial}</b> Metric Tons CO2e/ Year` +
          // '</br>Natural Gas Residential Sector: '+ `<b>${naturalGas_residential}</b> Metric Tons CO2e/ Year` +

          // '</br>Waste: '+ `<b>${waste}</b> Metric Tons CO2e/ Year` +
          // '</br>Aviation: '+ `<b>${aviation}</b> Metric Tons CO2e/ Year` +
          // '</br>Cement and Manufacturing: '+ `<b>${cement_and_manufacturing}</b> Metric Tons CO2e/ Year` +'</p>'+
          // '</div>'+
          '<div id="chart" style=""></div>' +
          "</div>";

        var contentStringNoData =
          '<div><div id="siteNotice"></div>' +
          '<h2 id="infoWindowHeader" class="infoWindowText">Zip code: ' +
          zip +
          "</h2>" +
          '<div><h2 class="infoWindowText">No Data</h2></div>' +
          "</div>";

        // Center info window on selected zip code area
        // Find center of zip code area by converting
        // the corresponding Polygon object to a
        // LatLngBounds object which has the getCenter function
        var bounds = new google.maps.LatLngBounds();
        var geometry = event.feature.getGeometry();

        geometry.forEachLatLng(function (point) {
          bounds.extend({
            lat: point.lat(),
            lng: point.lng(),
          });
        });
        var center = bounds.getCenter();

        // Create invisible marker for info window
        var marker = new google.maps.Marker({
          position: center,
          map: map,
          visible: false,
        });

        // Create info window and show no data for areas without data
        if (city == "Unknown" || population2018 == 0) {
          infowindow.setContent(contentStringNoData);
        } else {
          infowindow.setContent(contentString);

          /* ------------------------ Draw pie chart ---------------------------------------------- */

          google.charts.load("current", { packages: ["corechart"] });
          google.charts.setOnLoadCallback(drawChart);

          function drawChart() {
            var data = google.visualization.arrayToDataTable([
              ["Sector", "Metric Tons CO2e/ Year"],
              ["Transportation", convertToNum(transportationTotal)],
              ["Electricity", convertToNum(electricityTotal)],
              ["Natural Gas", convertToNum(naturalGasTotal)],
              ["Waste", convertToNum(wasteTotal)],
            ]);

            // Pie chart options
            var options = {
              title: "Economic Sector CO2e Contributions (MT/Y)",
              height: 250,
              width: 350,
              legend: { position: "bottom" },
              // bar: { groupWidth: '75%' },
              // isStacked: True
            };

            var chart = new google.visualization.PieChart(
              document.getElementById("chart")
            );
            chart.draw(data, options);
          }
        }

        infowindow.open(map, marker);

      }
    });

  /* --------------------------------- LEGEND --------------------------------- */

  // Create a color bar legend for the colored zip code areas.
  // By default, shows colors used for describing average CO2e emissions
  var legend = document.getElementById("legend");
  createLegend(legend, true);

  function createLegend(legend, useDensity) {
    // Legend for CO2e Per Person
    if (useDensity) {
      var div = document.createElement("center");
      div.innerHTML = "<h3>Metric Tons<br/>CO<sub>2</sub>e Per<br/>Person</center></h3>";
      legend.appendChild(div);
      for (let key in colorScale) {
        var color = key;
        var label = `<= ${colorScale[key]}`;
        var div = document.createElement("div");
        div.innerHTML =
          '<div class="cbox" style="background-color: ' +
          color +
          '; padding: 5px; box-sizing: border-box; opacity: 0.8;"><center>' +
          label +
          "</center>";
        legend.appendChild(div);
      }
      // Alternate Legend may go here
    }
  }
  map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legend);
}
