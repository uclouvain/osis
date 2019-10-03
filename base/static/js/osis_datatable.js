function initializeDataTable(tableId, storageKey, pageNumber, itemsPerPage, ajaxUrl, columnDefs){
    setEventKeepIds(tableId, storageKey);
    let domTable = $('#' + tableId);
    domTable.DataTable(
    {
        columnDefs: columnDefs,
        "stateSave": true,
        "paging" : false,
        "ordering" : true,
        "orderMulti": false,
        "order": [[1, 'asc']],
        "serverSide": true,
        "ajax" : {
            "url": ajaxUrl,
            "type": "GET",
            "dataSrc": "object_list",
            "data": function (d){
                let querystring = getDataAjaxTable(domTable, d, pageNumber);
                querystring["paginator_size"] = itemsPerPage;
                return querystring;
            },
            "traditional": true
        },
        "info"  : false,
        "searching" : false,
        "language": {
            "oAria": {
                "sSortAscending":  "{% trans 'activate to sort column ascending'%}",
                "sSortDescending": "{% trans 'activate to sort column descending'%}"
            }
        }
    });
}

function prepare_xls(e, action_value){
    e.preventDefault();
    var status = $("#xls_status");
    status.val(action_value);
    $("#download_xls").submit();
    status.val('');
}

