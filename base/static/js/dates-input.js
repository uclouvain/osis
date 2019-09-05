function set_config(config, input, input_type) {
    config.minDate = input.data("mindate");
    config.maxDate = input.data("maxdate");
    config.format = input.data('format');
    config.showToday = false;
    config.useCurrent = false;
    config.autoApply = true;

    if (input_type === "daterangepicker"){
        input.daterangepicker(config);
    } else {
      input.datetimepicker(config)
    }
}

$(document).ready(function() {
    const user_language = document.documentElement.lang;

    const defaultConfig = {
            pickTime: false,
            language: user_language
        };


    $('.datepicker').each(function () {
        set_config(defaultConfig, $(this));
    });

    $('.timepicker').each(function () {
        set_config(defaultConfig, $(this));
    });

    $('.datetimepicker').each(function () {
        var config = {
            language: user_language
        };
        set_config(config, $(this));
    });

    $('.daterange').each(function () {

        var format =  $(this).data('format');

        var config = {
            autoUpdateInput: false,
            locale: {
                format: format,
                language: user_language,
                cancelLabel: 'Clear'
            }
        };

        set_config(config, $(this), "daterangepicker");

        $(this).on('apply.daterangepicker', function(ev, picker) {
            $(this).val(picker.startDate.format(format)
                + ' - ' + picker.endDate.format(format)
            );
        });
        $(this).on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
        });
    });
});