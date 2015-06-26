/* ***********************************************
 * Module to select export filter properties. Is currently
 * only responsible for dynamically populating the category
 * values for the category select and is automatically loaded
 * when included in a page.
 *
 * @author Patrick Rickles (http://github.com/excites)
 * @version 0.1
 * ***********************************************/

 $(function() {
    'use strict';

    var categorySelect = $('select[name=exportCategory]');

    $('select[name=exportProject]').on('change', function () {
        var selectedProjectId = $(this).val();

        categorySelect.find('option').each(function () {
            if ($(this).val() !== '') {
                $(this).remove();
            }
        });

        $.get('/admin/export/create/' + selectedProjectId, function (categories) {
            var id;

            for (id in categories) {
                categorySelect.append($('<option value="' + id + '">' + categories[id] + '</option>'));
            }
        });
     });

 });
