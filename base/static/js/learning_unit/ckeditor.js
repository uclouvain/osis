/**
 * This function is needed because during the volumes' modification of a learning unit,
 * a volume with 2 decimals (eg. 1.00) gives a validation error because of the 0.5 step.
 * It is an issue linked to the jquery validator.
 */
    $(function () {
        var richText = $('#id_trans_text');
        var config = richText.data('config');
        CKEDITOR.replace('id_trans_text', config);
    });
