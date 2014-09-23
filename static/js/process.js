$(document).ready(function() { 
  $("ul.countries li a").click(function() {
    $('ul.countries li.active').removeClass('active');
    $(this).parent('li').addClass('active');
    var country = $(this).text();
    processResults(rawData, mapCountry(country));
  });
  setTimeout(makeSockJSConnection(), 100);
});

function mapCountry(country) {
  switch (country) {
    case "Singapore":
      return "sg";
      break;
    case "Hong Kong":
      return "hk";
      break;
    case "Taiwan":
      return "tw";
      break;
    case "Australia":
      return "au";
      break;
  }  
}

function processResults(iPhoneData, country) {
  $('#iphone6plus').empty();
  $('#iphone6').empty();

  countryIPhoneData = iPhoneData[country];

  for (var i = 0;  i < countryIPhoneData.length; i++) {
    s = '<div class="col-sm-4">';

    if (countryIPhoneData[i]['availability'] == "No") {
      s += '<div class="panel panel-danger"><div class="panel-heading"><h3 class="panel-title">Unavailable</h3></div>'
    }
    else {
      s += '<div class="panel panel-success"><div class="panel-heading"><h3 class="panel-title">Available</h3></div>'
    }

    s += '<div class="panel-body">'
    s += "<strong>Colour:</strong> " + countryIPhoneData[i]['colour'] + '<br>'
    s += "<strong>Capacity:</strong> " + countryIPhoneData[i]['capacity'] + '<br>'
    s += "<strong>Price:</strong> $" + countryIPhoneData[i]['price'] + '<br>'
    s += '</div></div></div>'

    if (countryIPhoneData[i]['model'] == "iPhone 6 Plus") {
      $('#iphone6plus').append(s);
    }
    else {
      $('#iphone6').append(s); 
    }
  }
}

function processTime(iPhoneData) {
  lastUpdated = iPhoneData["last_updated"];
  d = new Date(lastUpdated);
  $('#lastUpdated').text(d);
}

function makeSockJSConnection() {
  var sock = new SockJS('http://' + window.location.host + '/data');
  sock.onopen = function(evt) { console.log('SockJS connection opened.') };
  sock.onmessage = function(evt) {
      data = $.parseJSON(evt.data);
      country = $('ul.countries li.active').text();
      processResults(data, mapCountry(country));
      processTime(data);
  };
  sock.onerror = function(evt) { };
  sock.onclose = function(evt) { console.log('SockJS connection closed.') };
}