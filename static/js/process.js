$(document).ready(function() { 
  $("ul.countries li a").click(function() {
    $('ul.countries li.active').removeClass('active');
    $(this).parent('li').addClass('active');
    var country = $(this).text();

    switch (country) {
      case "Singapore":
        processResults(rawData, "sg");
        break;
      case "Hong Kong":
        processResults(rawData, "hk");
        break;
      case "Taiwan":
        processResults(rawData, "tw");
        break;
      case "Australia":
        processResults(rawData, "au");
        break;
    }
  });
});

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