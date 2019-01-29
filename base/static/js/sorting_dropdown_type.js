// initial sorting when the page is loaded
$(document).ready(function () {
    sort_dropdown_type("id_education_group_type");
});

// sorting when we change the category
$("#id_category").click(function() {
    sort_dropdown_type("id_education_group_type");
});


/**
 * Function to sort a <select> tag
 * @param id_elem element id of the select to sort
 */
function sort_dropdown_type(id_elem){
    // get the wanted select
    let select_edu_group_type = $("#" + id_elem);
    // extract the options from the select
    let my_options = $("#" + id_elem + " option");
    // to keep the selected value
    let selected = select_edu_group_type.val();

    my_options.sort(function(a,b) {
        // localCompare is used to compare String based on the current locale
        if(a.value) {
            return a.text.localeCompare(b.text);
        }else{
            // If no value -> equals to 'All' which has to be at the top of the dropdown  list
            return -1;
        }
    });
    // replace the old list with the sorted one
    select_edu_group_type.empty().append( my_options );
    // select the value from the original list
    select_edu_group_type.val(selected);
}