function initializeDataTable(tableId, storageKey, pageNumber, itemsPerPage, ajaxUrl, columnDefs){
    setEventKeepIds(tableId, storageKey);
    let domTable = $('#' + tableId);
    domTable.DataTable(
    {
        'createdRow': function (row, data, dataIndex) {
            $(row).attr('data-id', data['osis_url']);
            $(row).attr('data-value', data['acronym']);
        },
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
        'processing': true,
        "language": {
            "oAria": {
                "sSortAscending":  gettext("activate to sort column ascending"),
                "sSortDescending": gettext("activate to sort column descending")
            },
            'processing': gettext("Loading...")
        }
    });
}

function prepare_xls(e, action_value){
    e.preventDefault();
    document.dispatchEvent(new CustomEvent("prepareXls:onClick", {
        "detail": $(e.target)
    }));
    let status = $("#xls_status");
    status.val(action_value);
    $("#search_form").submit();
    status.val('');
}
