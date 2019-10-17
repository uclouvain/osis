let linkButtonNoSpinnerClicked = false;

$( document ).ready(function() {
    closeOverlaySpinner();
    $('a, button').on('click submit', function (e) {
        linkButtonNoSpinnerClicked = $(this).hasClass("no_spinner");
    });
});

$( document ).on( 'keyup', function ( e ) {
    if ( e.key === 'Escape' ) { // ESC
        closeOverlaySpinner();
    }
});

window.addEventListener('beforeunload', function (e) {
    if (! linkButtonNoSpinnerClicked) {
        $("#loader").show();
        document.getElementById("overlay_fadein").style.display = "block";
    }
});

function closeOverlaySpinner(){
    $("#loader").hide();
    document.getElementById("overlay").style.display = "none";
    document.getElementById("overlay_fadein").style.display = "none";
}
