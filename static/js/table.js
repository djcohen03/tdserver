
$('table thead th').on('click', event => {
    var target = $(event.target);

    // Get the index of the clicked tablehead cell:
    var cells = target.closest('tr').find('th');
    var index = cells.map((index, cell) => $(cell).text() == target.text() ? index : null).filter((_, item) => item != null);


    var table = $('table');

});
