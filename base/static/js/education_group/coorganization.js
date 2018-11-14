$(document).ready(function () {
    function bindCountryChange(){
        $(':input[name$=country]').on('change', function() {
            var prefix = $(this).getFormPrefix();
            // Clear the autocomplete organization with the same prefix
            $(':input[name=' + prefix + 'organization]').val(null).trigger('change');
        });
    }

    var formElem = document.querySelector("#coorganization-form");
    formElem.addEventListener("formAjaxSubmit:error", function(){
        bindCountryChange();
    });
    bindCountryChange();
});