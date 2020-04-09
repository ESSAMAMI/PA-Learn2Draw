// Call the dataTables jQuery plugin
//$(document).ready(function() {
//  $('#dataTable').DataTable();
//});

// Call the dataTables jQuery plugin
$(document).ready(function () {
$('#dataTable').DataTable({
"order": [[ 4, "desc" ]]
});
$('#users-table').DataTable( {
"pagingType": "full_numbers",
"order": [[ 2, "desc" ]]
} );
$('#drawings-table').DataTable( {
"pagingType": "full_numbers",
"order": [[ 4, "desc" ]]
} );
$('#categories-table').DataTable( {
"pagingType": "full_numbers",
"order": [[ 0, "asc" ]]
} );
$('#notations-table').DataTable( {
"pagingType": "full_numbers",
"order": [[ 5, "desc" ]]
} );
$('.dataTables_length').addClass('bs-select');
});

/*$(document).ready(function() {
$('#users-table').DataTable( {
//"pagingType": "full_numbers",
"order": [[ 4, "desc" ]]
} );
$('.dataTables_length').addClass('bs-select');
} );*/

/*
MB EDITOR EST PAYANT

$('#dtBasicExample').mdbEditor({
headerLength: 6,
evenTextColor: '#000',
oddTextColor: '#000',
bgEvenColor: '',
bgOddColor: '',
thText: '',
thBg: '',
modalEditor: false,
bubbleEditor: false,
contentEditor: false,
rowEditor: false
});

$('#dtBasicExample').mdbEditor({
mdbEditor: true
});
$('.dataTables_length').addClass('bs-select');
*/