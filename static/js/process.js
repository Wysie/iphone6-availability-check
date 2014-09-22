function processResults(iPhoneData) {
  $('#iphone6plus').empty();
  $('#iphone6').empty();

  for (var i = 0;  i < iPhoneData.length; i++) {
    s = '<div class="col-sm-4">';

    if (iPhoneData[i]['availability'] == "No") {
      s += '<div class="panel panel-danger"><div class="panel-heading"><h3 class="panel-title">Unavailable</h3></div>'
    }
    else {
      s += '<div class="panel panel-success"><div class="panel-heading"><h3 class="panel-title">Available</h3></div>'
    }

    s += '<div class="panel-body">'
    s += "<strong>Colour:</strong> " + iPhoneData[i]['colour'] + '<br>'
    s += "<strong>Capacity:</strong> " + iPhoneData[i]['capacity'] + '<br>'
    s += "<strong>Price:</strong> $" + iPhoneData[i]['price'] + '<br>'
    s += '</div></div></div>'

    if (iPhoneData[i]['model'] == "iPhone 6 Plus") {
      $('#iphone6plus').append(s);
    }
    else {
      $('#iphone6').append(s); 
    }
  }
}