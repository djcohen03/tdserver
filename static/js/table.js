$(function() {

    var bindTableDownload = (table, link) => {
        // Binds a download-table action on the given link for the given table

        var csvcontent = 'data:text/csv;charset=utf-8,';

        // Loop through table headers:
        table.find('thead > tr').each((i, header) => {
            // Loop through table header cells:
            $(header).find('th').each((i, cell) => {
                // Append cell contents:
                csvcontent += $(cell).text().trim() + ',';

                // Add extra spacing for colspans:
                var colspan = $(cell).attr('colspan');
                if (colspan) {
                    var count = parseInt(colspan) - 1;
                    csvcontent += ','.repeat(count);
                }
            });
            csvcontent += '\r\n';
        });

        // Get Table Content:
        table.find('tbody > tr').each((i, row) => {
            $(row).find('td').each((i, cell) => {
                // Append cell contents:
                csvcontent += $(cell).text().trim() + ',';

            });
            csvcontent += '\r\n';
        });

        // Chrome, Firefox: Create and Click hidden download link:
        link.attr({
            href: encodeURI(csvcontent),
            download: 'data.csv',
        });
    }

    var table = $('table');
    var button = $('.download');
    bindTableDownload(table, button);
});
