/* ***************************************************
 * Listens for a change of selected project and gets
 * all categories of it.
 *
 * @author Patrick Rickles (http://github.com/excites)
 * ***************************************************/

$(function() {
    'use strict';

    var category = $('select[name=category]');

    $('select[name=project]').on('change', function() {
        var project = $(this).val();

        category.find('option').each(function() {
            if ($(this).val() !== '') {
                $(this).remove();
            }
        });

        if (project) {
            $.get('/admin/export/' + project + '/categories/', function(categories) {
                if (categories) {
                    categories = $.parseJSON(categories);

                    for (var key in categories) {
                        if (categories.hasOwnProperty(key)) {
                            category.append($('<option value="' + key + '">' + categories[key] + '</option>'));
                        }
                    }
                }
            });
        }

        category.parent().removeClass('hidden');
    });
});
