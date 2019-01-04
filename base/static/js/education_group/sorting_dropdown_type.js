$(document).ready(function () {
    sort_dropdown_type("id_education_group_type");
});

$("#id_category").click(function() {
    sort_dropdown_type("id_education_group_type");
});

function sort_dropdown_type(id_elem){
    let select_edu_group_type = $("#" + id_elem);
    let my_options = $("#" + id_elem + " option");
    let selected = select_edu_group_type.val();

    my_options.sort(function(a,b) {
        return a.text.localeCompare(b.text);
    });

    select_edu_group_type.empty().append( my_options );
    select_edu_group_type.val(selected);
}