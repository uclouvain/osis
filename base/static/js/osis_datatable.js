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
    var contentType = "undefined";
    if (url.includes("learning_units")){
        contentType = "base_learningunityear";
    }else if(url.includes("educationgroups")){
        contentType = "base_educationgroupyear";
    }
    let object_id = getIdFromUrl(url).toString();
    localStorage.setItem("quickSearchSelection", JSON.stringify({"id": object_id, "content_type": contentType}));
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
            const elementName = e.target.getAttribute('data-name');
            const d = {
                element_name: elementName
            };
            const fmt = gettext("Element selected \"%(element_name)s\": You cannot attach the same child multiple times.");
            const s = interpolate(fmt, d, true);
            $("#message_info_modal").attr("style", "").text(s);
            const url = e.target.getAttribute('data-url');
            select_element_from_url(url);
        })
    });
};

function attachModal(url){
    return function(){
        const parameters = JSON.parse(localStorage.getItem("quickSearchSelection"));
        const paramString = new URLSearchParams(parameters);
        const urlWithParameters = `${url}?${paramString.toString()}`;

        document.getElementById("modal_dialog_id").classList.add("modal-lg");
        $('#form-modal-ajax-content').load(urlWithParameters, function (response, status, xhr) {
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
