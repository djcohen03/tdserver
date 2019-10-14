$(function() {
    $('#choose-fetch').selectize().on('change', () => {
        window.location = $('#choose-fetch').val();
    });

})
