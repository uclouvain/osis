// FIXME this method has been override by another script block

$(document).ready(function()
{
    $('#tbl_coorganization').DataTable(
        {
            columnDefs: [
                { targets: 1, type: 'diacritics-neutralise'},
                { orderable: false, targets: [1]}
            ],
            "stateSave": true,
            "paging" : false,
            "ordering" : true,
            "info"  : false,
            "searching" : false,
            "language": {
                "oAria": {
                    "sSortAscending":  "{% trans 'datatable_sortascending'%}",
                    "sSortDescending": "{% trans 'datatable_sortdescending'%}",
                }
            }
        })
    ;});
