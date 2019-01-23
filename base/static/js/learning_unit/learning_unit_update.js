/**
 * This function is needed because during the volumes' modification of a learning unit,
 * a volume with 2 decimals (eg. 1.00) gives a validation error because of the 0.5 step.
 * It is an issue linked to the jquery validator.
 */
function check_simplified_volumes_form() {
    $('form[id="LearningUnitYearForm"]').validate({
        normalizer: function (value) {
            // we check first if the value is a numeric
            if ( $.isNumeric(value) ) {
                // test if the value is x.00
                if ( Math.floor(value.valueOf()) === value.valueOf() ) return value;
                // test if last character is 0. if yes, we remove it
                return ( value[value.length - 1] === '0' ? (Math.floor(value * 10) / 10) : value );
            }
            return value;
        },
        submitHandler: function (form) {
            form.submit();
        }
    });
}

$(document).ready(check_simplified_volumes_form);