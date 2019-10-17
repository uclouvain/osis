$( document ).ready(function() {
    closeOverlaySpinner();
    $('a, button').on('click', function (e) {
        if ($(this).hasClass("no_spinner")) closeOverlaySpinner();
    });
});

$( document ).on( 'keyup', function ( e ) {
    if ( e.key === 'Escape' ) { // ESC
        closeOverlaySpinner();
    }
});

window.addEventListener('beforeunload', function (e) {
    $("#loader").show();
    document.getElementById("overlay_fadein").style.display = "block";
});

function closeOverlaySpinner(){
    $("#loader").hide();
    document.getElementById("overlay").style.display = "none";
    document.getElementById("overlay_fadein").style.display = "none";
}
