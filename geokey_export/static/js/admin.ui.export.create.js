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

        if(selectedProjectId) {
            $.get('/admin/export/' + selectedProjectId + '/categories/', function (new_categories) {
                if(new_categories) {
                    var new_categories_p = $.parseJSON(new_categories);

                    for (var key in new_categories_p) {
                        if (new_categories_p.hasOwnProperty(key)) {
                            categorySelect.append($('<option value="' + key + '">' + new_categories_p[key] + '</option>'));
                        }
                    }
                }
            });
        }

        categorySelect.parent().removeClass('hidden');
     });
 });
