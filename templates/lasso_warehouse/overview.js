{% load adminmedia %}
{% load admin_list %}
{% load i18n %}
{% load i18next %}
{% load datatypes %}

{% block data %}
  customers = {{ customers|jsonify|safe }};
  entries = {{ entries|jsonify|safe }};
  warehouses = {{ warehouses|jsonify|safe }};
  rows = {{ rows|jsonify|safe }};
  pallet_spaces = {{ pallet_spaces|jsonify|safe }};

  empty_pallet_space_change_uri = '{% url admin:lasso_warehouse_emptypalletspace_change "%id%" %}';
  filled_pallet_space_change_uri = '{% url admin:lasso_warehouse_filledpalletspace_change "%id%" %}';

{% endblock %}

{% block update_svg %}
  $(document).ready(function () {
    var onImageLoad = function () {
      var image = $($('#overview-image')[0].contentDocument);

      for (pallet_space_id in pallet_spaces) {
	var pallet_space = pallet_spaces[pallet_space_id];
	var row = rows[pallet_space.fields.row];
	var warehouse = warehouses[row.fields.warehouse];
	var pallet_space_shape_id = "#" + encodeURI(warehouse.fields.name + "-" + row.fields.name + "-" + pallet_space.fields.name);
	var pallet_space_shape = image.find(pallet_space_shape_id);

	var color = '#00ff00';
	if (pallet_space.fields.entry != null) {
	  color = '#ff0000';
	}

	var old_style = pallet_space_shape.attr('style');
	pallet_space_shape.attr('style', old_style.replace(new RegExp("fill: [^;]*;", "g"), 'fill: ' + color + ';'));
	pallet_space_shape.click(
          function (pallet_space) {
            return function() {
	      if (pallet_space.fields.entry == null) {
	        document.location = empty_pallet_space_change_uri.replace("%id%", pallet_space.pk);
	      } else {
	        document.location = filled_pallet_space_change_uri.replace("%id%", pallet_space.pk);
	      }
            }
          }(pallet_space)
        );
      };
    };

    // Ok, this uggly stuff is here since onload doesn't seem to work :(
    var checkImageLoad = function () {
      var image_content = $('#overview-image')[0].contentDocument;
      if (image_content == null) {
	  setTimeout(checkImageLoad, 300);
      } else {
	  onImageLoad();
      }
    };

    checkImageLoad();
  });
{% endblock %}
