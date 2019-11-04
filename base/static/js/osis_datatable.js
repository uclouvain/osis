function initializeDataTable(formId, tableId, storageKey, pageNumber, itemsPerPage, ajaxUrl, columnDefs){
    setEventKeepIds(tableId, storageKey);
    let domTable = $('#' + tableId);
    return domTable.DataTable(
    {
        'createdRow': function (row, data, dataIndex) {
            let url = "";
            if (data['osis_url']) {
                url = data['osis_url'];
            } else {
                url = data['url'];
            }
            $(row).attr('data-id', url);
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
                let querystring = getDataAjaxTable(formId, domTable, d, pageNumber);
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

function select_element_from_url(url){
    let egy_id = getIdFromUrl(url);
    console.log("selected");
}

// FIXME This method is copy pasted Refactor
function getIdFromUrl(url){
    let split = url.split("/");
    for(let i=split.length-1; i--; i >= 0){
        if(!isNaN(split[i])){
            return parseInt(split[i]);
        }
    }
    return NaN;
}

function onDraw(){
    $("input[name=selected-item]").each(function(index, element){
        element.addEventListener('click', function(e){
            const url = e.target.getAttribute('data-url');
            select_element_from_url(url);
        })
    });
};

function attachModal(url){
    return function(){
        document.getElementById("modal_dialog_id").classList.add("modal-lg");
        $('#form-modal-ajax-content').load(url, function (response, status, xhr) {
            if (status === "success") {
                let form = $(this).find('form').first();
                formAjaxSubmit(form, '#form-ajax-modal');
            }

        });
    };
}


function reloadEducationGroupSearchResult(tableId){
    $('#table-education-group').DataTable().ajax.reload();
}

function reloadLearningUnitSearchResult(tableId){
    $('#table-learning-unit').DataTable().ajax.reload();
}
