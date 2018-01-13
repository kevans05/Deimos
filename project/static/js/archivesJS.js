$(document).ready(function()
    {
    $("#archiveInfo").tablesorter({
        // pass the headers argument and assing a object
        headers: {
            // assign the secound column (we start counting zero)
            4: {
                // disable it by setting the property sorter to false
                sorter: false
            }
        }
    });
});
$(document).ready(function(){
  $("#search").on("keyup", function() {
    var value = $(this).val().toLowerCase();
    $("#archiveInfo tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});