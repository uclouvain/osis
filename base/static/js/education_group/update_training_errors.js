$(document).ready(function () {
    var tabs = ['identification', 'content', 'diploma'];
    tabs.forEach(function (tab_name) {
        var tab = document.getElementById('tab_' + tab_name);
        var spn_tab_errors = $("#spn_" + tab_name + "_errors");
        spn_tab_errors.empty();
        if (tab && tab.getElementsByClassName('has-error').length > 0) {
            spn_tab_errors.empty();
            spn_tab_errors.append('<i class="fa fa-circle" aria-hidden="true"></i>')
        }
    });
});