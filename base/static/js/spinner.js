let linkButtonNoSpinnerClicked = false;
//sync spinner is always active on page load
const spinnerActive = {sync: true, async: false};
let downloadInterval;

function showOverlaySpinner(async= false) {
    $('#loader, #overlay-fade-in').show();
    spinnerActive[async ? 'async' : 'sync'] = true;
}

function closeOverlaySpinner(async= false){
    // hide according to initial trigger
    if(spinnerActive[async ? 'async' : 'sync'] && !spinnerActive[!async ? 'async' : 'sync']) {
        $('#loader, #overlay, #overlay-fade-in').hide();
        spinnerActive[async ? 'async' : 'sync'] = false;
    }
}

//handle spinner for download file
function isDownloadCompleted(){
    if(document.cookie.includes('download')){
        closeOverlaySpinner();
        // delete cookie setting an expired date
        document.cookie = "download=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        if(downloadInterval) {
            clearInterval(downloadInterval)
        }
    }
}

$(document).ready(function() {
    closeOverlaySpinner();
    $('.no_spinner').click(() => {
        downloadInterval = setInterval(isDownloadCompleted, 2000);
    });
});

$(document).on('keyup', function (e) {
    if ( e.key === 'Escape' ) { // ESC
        closeOverlaySpinner();
    }
});

window.addEventListener('beforeunload', function (e) {
    if (! linkButtonNoSpinnerClicked) {
        showOverlaySpinner();
    }
});

$(document).ajaxStart(function(){
    showOverlaySpinner(true);
}).ajaxStop(function(){
    closeOverlaySpinner(true);
});
