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

     $('select[name=exportProject]').on('change', function() {

       var selected_project_id = $('select[name=exportProject]').find(':selected').val();

       $.get('/admin/export/create/' + selected_project_id, function(new_categories){

         var categorySelect = $('select[name=exportCategory]');
         categorySelect.empty();

         alert(typeof(new_categories));

         for(var i = 0, len = new_categories.length; i < len; i++)
         {
           alert(i);
           //categorySelect.append($('<option value="' + new_categories.key + '">' + new_categories.val + '</option>'));
         }

       });

     });

 });
