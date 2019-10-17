$( document ).ready(function() {
    closeOverlaySpinner();
});

$( document ).on( 'keyup', function ( e ) {
    if ( e.key === 'Escape' ) { // ESC
        closeOverlaySpinner();
    }
});

window.addEventListener('beforeunload', function (e) {
    $( document ).on( 'click', function ( e ) {
        alert(e.hasClass('no_spinner'));
        if (e.hasClass('no_spinner')){
            return null;
        }
    });
    $("#loader").show();
    document.getElementById("overlay_fadein").style.display = "block";
});

function closeOverlaySpinner(){
    $("#loader").hide();
    document.getElementById("overlay").style.display = "none";
    document.getElementById("overlay_fadein").style.display = "none";
}
