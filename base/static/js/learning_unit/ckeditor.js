$(function () {
    var richText = $('#id_trans_text');
    var config = richText.data('config');
    CKEDITOR.replace('id_trans_text', config);
});
