// Ajax request to update the city list
jQuery.fn.filterCityByCountry = function(city_node, campus_node, ajax_url){
    $(this).on('change', function () {

        $.getJSON(ajax_url,{country: $(this).val(), ajax: 'true'}, function(j){
            city_node.html('');
            campus_node.html('');
            let options = '';
            options += '<option value="">---------</option>';
            campus_node.html(options);
            for (let i = 0; i < j.length; i++) {
                options += '<option value="' + j[i].city + '">' + j[i].city + '</option>';
            }
            city_node.html(options);
        })
    });
};

// Ajax request to update the campus list
jQuery.fn.filterCampusByCity = function(campus_node, ajax_url){
    $(this).on('change', function () {
        $.getJSON(ajax_url,{city: $(this).val(), ajax: 'true'}, function(j){
            campus_node.html('');
            let options = '<option value="">---------</option>';
            for (let i = 0; i < j.length; i++) {
                options += '<option value="' + j[i].pk + '">' + j[i].organization__name + '</option>';
            }
            campus_node.html(options);
        })
    });
};
