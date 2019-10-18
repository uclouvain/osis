let linkButtonNoSpinnerClicked = false;

function bindNoSpinner(elem){
    if (elem) {
        linkButtonNoSpinnerClicked = elem.hasClass("no_spinner");
    } else {
        $('a, button').on('click submit', function (e) {
            linkButtonNoSpinnerClicked = $(this).hasClass("no_spinner");
        });
    }
}

function closeOverlaySpinner(){
    $("#loader").hide();
    document.getElementById("overlay").style.display = "none";
    document.getElementById("overlay_fadein").style.display = "none";
}

$( document ).ready(function() {
    closeOverlaySpinner();
    bindNoSpinner();
    document.addEventListener("formAjaxSubmit:onSubmit", function( e ){
        bindNoSpinner(e.detail);
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
