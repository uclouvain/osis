$( document ).ready(function() {
    $("#loader").hide();
    document.getElementById("overlay").style.display = "none";
});

window.addEventListener('beforeunload', function (e) {
  $("#loader").show();
  document.getElementById("overlay").style.display = "block";
});