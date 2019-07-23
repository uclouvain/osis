$(function () {
    var richText = $('#id_trans_text_fr');
    var config = richText.data('config');
    CKEDITOR.replace('id_trans_text_fr', config);

    var richText = $('#id_trans_text_en');
    var config = richText.data('config');
    CKEDITOR.replace('id_trans_text_en', config);
});