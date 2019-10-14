$(function() {
    $('.date-picker').on('change', function() {
        window.location = $(this).val();
    })
})
