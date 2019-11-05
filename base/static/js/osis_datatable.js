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
    if (url == null){
        return {"id": "", "content_type": ""};
    }
    var contentType = "undefined";
    if (url.includes("learning_units")){
        contentType = "base_learningunityear";
    }else if(url.includes("educationgroups")){
        contentType = "base_educationgroupyear";
    }
    let object_id = getIdFromUrl(url).toString();
    return {"id": object_id, "content_type": contentType};
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


function attachModal(checkUrl, attachUrl){
    return function(){
        const elementUrl = $("input[name=selected-item]:checked").attr("data-url");
        const parameters = select_element_from_url(elementUrl);
        const paramString = new URLSearchParams(parameters);

        $.ajax({
            url: `${checkUrl}?${paramString.toString()}`,
        }).done(function(jsonResponse){
            const error_messages = jsonResponse["error_messages"];
            if (error_messages.length > 0){
                const $span_messages = $("#message_info_modal");
                $span_messages.removeAttr("style");
                error_messages.forEach(function(message){
                    $span_messages.append(`<p>${message}</p>`);
                });
            } else {
                document.getElementById("modal_dialog_id").classList.add("modal-lg");
                $('#form-modal-ajax-content').load(`${attachUrl}?${paramString.toString()}`, function (response, status, xhr) {
                    if (status === "success") {
                        let form = $(this).find('form').first();
                        formAjaxSubmit(form, '#form-ajax-modal');
                    }
                });
            }
        });
    };
}

function submit_with_page(page) {
    $("input[name='page']").val(page);
    $('#form-modal').submit();
}