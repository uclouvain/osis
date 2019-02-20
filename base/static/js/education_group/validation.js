/**
 * Send ajax request to validate if the field has no error.
 * If the field has an error, display the according message.
 */
function validate_field() {
    const field_name = $(this).attr('name');

    const url = $('.education_group_form').data('validate-url');
    var parameters = {
        'academic_year': $("#id_academic_year").val()
    };
    parameters[field_name] = $(this).val();

    $.get(url, parameters, function(data) {
        var $parent = $(".education_group_form [name='" + field_name + "']").parent();
        $parent.removeClass('has-error');
        $parent.removeClass('has-warning');
        $parent.children(".help-block").remove();

        if (!(field_name in data)){
            return;
        }

        cls = 'has-warning';
        if (data[field_name].level === 'error') {
            cls = 'has-error'
        }
        $parent.addClass(cls);
        $parent.append("<div class='help-block'>" + data[field_name].msg+ "</div>");
    });
}

$(document).ready(function() {
        $("#id_acronym").change(validate_field);
        $("#id_partial_acronym").change(validate_field);

        // Revalidate acronym and partial acronym when modifying academic year
        $("#id_academic_year").change(function () {
            $("#id_acronym").trigger("change");
            $("#id_partial_acronym").trigger("change");
        })

    }
);