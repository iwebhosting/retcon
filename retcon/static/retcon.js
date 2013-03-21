var confirm_ack, count_x, create_element, dict_to_css_mapping, perform_ack, populate_box, populate_more_info, refresh, update_all, update_more_info;

dict_to_css_mapping = {
  critical: 'Crit',
  issues: 'Issue',
  flapping: 'Flapping',
  notes: 'Note',
  github: 'Github'
};

perform_ack = function(datum, duration) {
  return $.post('/api/ack', {
    backend: datum.backend,
    host: datum.host,
    service: datum.service,
    duration: duration
  });
};

confirm_ack = function(event) {
  var datum, issuediv;
  issuediv = $(this).parent().parent();
  datum = this.datum;
  return $("#ack_dialog").dialog({
    autoOpen: true,
    modal: true,
    buttons: {
      "OK": function(event) {
        perform_ack(datum, $("#ack_duration").val());
        issuediv.fadeOut("slow", function() {
          return issuediv.remove();
        });
        return $(this).dialog("close");
      },
      "Cancel": function() {
        return $(this).dialog("close");
      }
    }
  });
};

populate_more_info = function(e) {
  var d, mi;
  d = e.find('.ack')[0].datum;
  mi = e.find('.moreinfo');
  if (d.status_information) {
    mi.append("Information: " + d.status_information + " <br/>");
  }
  if (d.duration) mi.append("Duration : " + d.duration + " <br/>");
  if (d.last_check) mi.append("Last check: " + d.last_check + " <br/>");
  return e;
};

update_more_info = function(e) {
  e.find('.moreinfo').empty();
  return populate_more_info(e);
};

create_element = function(css_class, datum, outer_container) {
  var ack, container, matches, more, n;
  if (datum.hash) {
    matches = $('#' + datum.hash);
    if (matches.length > 0) {
      update_more_info(matches);
      return;
    }
  }
  more = $('<a href="#">More</a>');
  more.click(function() {
    return $(this).parent().parent().find('.moreinfo').slideToggle();
  });
  ack = $('<a href="#" class="ack">Ack</a>');
  ack[0].datum = datum;
  ack[0].onclick = confirm_ack;
  container = $('<div style="float: right" class="container"></div>').append(ack).append(' ').append(more);
  n = $("<div class='Box " + css_class + "' id='" + datum.hash + "'>");
  n.hide();
  if (datum.img) n.append($("<img height='24' src='" + datum.img + "'/>"));
  if (datum.host) {
    n.append("Host: <a class='url' href='ssh://" + datum.host + "'>" + datum.host + "</a> &mdash; ");
  }
  if (datum.service) n.append("Service: " + datum.service);
  if (datum.note) n.append("Note: " + datum.note);
  n.append(container).append($('<div class="moreinfo"></div>').hide()).mouseover(function() {
    return this.style.backgroundColor = '#bbb';
  }).mouseout(function() {
    return this.style.backgroundColor = '';
  }).fadeIn('slow');
  update_more_info(n);
  return outer_container.append(n);
};

populate_box = function(container, css_class, values) {
  var value, _i, _len, _results;
  _results = [];
  for (_i = 0, _len = values.length; _i < _len; _i++) {
    value = values[_i];
    _results.push(create_element(css_class, value, container));
  }
  return _results;
};

refresh = function(api, mapping, callback) {
  return $.getJSON(api, function(data) {
    var css_class, k, v;
    for (k in data) {
      v = data[k];
      css_class = mapping[k];
      populate_box($('#' + k), css_class, v);
    }
    return callback();
  });
};

count_x = function(x) {
  return $("#count_" + x).html($("#" + x + " .Box").length);
};

update_all = function() {
  $('#loading_notes').show();
  $('#loading_data').show();
  refresh('/api/notes', dict_to_css_mapping, function() {
    $('#loading_notes').hide();
    return count_x('notes');
  });
  refresh('/api/data', dict_to_css_mapping, function() {
    var x, _i, _len, _ref, _results;
    $('#loading_data').hide();
    _ref = ['critical', 'flapping', 'issues'];
    _results = [];
    for (_i = 0, _len = _ref.length; _i < _len; _i++) {
      x = _ref[_i];
      _results.push(count_x(x));
    }
    return _results;
  });
  refresh('/api/github', dict_to_css_mapping, function() {
    $('#loading_github').hide();
    return count_x('github');
  });
  return true;
};

$.doTimeout(30000, update_all);

$(update_all);
