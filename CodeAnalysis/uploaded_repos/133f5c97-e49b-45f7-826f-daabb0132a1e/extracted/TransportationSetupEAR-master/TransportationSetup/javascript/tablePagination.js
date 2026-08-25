// JavaScript Document

var asInitVals = new Array();

$(document).ready(function() {
	
	var oTable = $('#area_code').dataTable( {
		"oLanguage": {
			"sSearch": "Search all columns:"
		}
	} );



	$("tfoot input").keyup( function () {
		/* Filter on the column (the index) of this element */
		oTable.fnFilter( this.value, $("tfoot input").index(this) );
	} );



	/*
	 * Support functions to provide a little bit of 'user friendlyness' to the textboxes in
	 * the footer
	 */
	$("tfoot input").each( function (i) {
		asInitVals[i] = this.value;
	} );

	$("tfoot input").focus( function () {
		if ( this.className == "search_init" )
		{
			this.className = "";
			this.value = "";
		}
	} );

	$("tfoot input").blur( function (i) {
		if ( this.value == "" )
		{
			this.className = "search_init";
			this.value = asInitVals[$("tfoot input").index(this)];
		}
	} );
	
} );



function restoreRow ( oTable, nRow )
{
	var aData = oTable.fnGetData(nRow);
	var jqTds = $('>td', nRow);

	for ( var i=0, iLen=jqTds.length ; i<iLen ; i++ ) {
		oTable.fnUpdate( aData[i], nRow, i, false );
	}

	oTable.fnDraw();
}

function editRow ( oTable, nRow )
{
	var aData = oTable.fnGetData(nRow);
	var jqTds = $('>td', nRow);
	jqTds[0].innerHTML = '<input type="radio" checked=checked>';
	jqTds[1].innerHTML = '<input type="text" value="'+aData[1]+'">';
	jqTds[2].innerHTML = '<input type="text" value="'+aData[2]+'">';
	jqTds[3].innerHTML = '<input type="text" value="'+aData[3]+'">';
	jqTds[4].innerHTML = '<input type="text" value="'+aData[4]+'">';
	jqTds[5].innerHTML = '<input type="text" value="'+aData[5]+'">';
	/*jqTds[6].innerHTML = '<input type="text" value="'+aData[6]+'">';*/
	jqTds[7].innerHTML = '<input type="text" value="'+aData[7]+'">';
	jqTds[8].innerHTML = '<input type="text" value="'+aData[8]+'">';
	jqTds[9].innerHTML = '<input type="text" value="'+aData[9]+'">';
	jqTds[10].innerHTML = '<input type="text" value="'+aData[10]+'">';
	jqTds[11].innerHTML = '<input type="text" value="'+aData[11]+'">';
	jqTds[12].innerHTML = '<input type="text" value="'+aData[12]+'">';
	jqTds[13].innerHTML = '<input type="text" value="'+aData[13]+'">';
	jqTds[14].innerHTML = '<input type="text" value="'+aData[14]+'">';
	jqTds[15].innerHTML = '<input type="text" value="'+aData[15]+'">';
	jqTds[17].innerHTML = '<input type="text" value="'+aData[17]+'">';
	jqTds[18].innerHTML = '<input type="text" value="'+aData[18]+'">';
}

function saveRow ( oTable, nRow )
{
	var jqInputs = $('input', nRow);
	oTable.fnUpdate( '<a class="Change" href="">Change</a>', nRow, 0, false );
	oTable.fnUpdate( jqInputs[1].value, nRow, 1, false );
	oTable.fnUpdate( jqInputs[2].value, nRow, 2, false );
	oTable.fnUpdate( jqInputs[3].value, nRow, 3, false );
	oTable.fnUpdate( jqInputs[4].value, nRow, 4, false );
	oTable.fnUpdate( jqInputs[5].value, nRow, 5, false );
	oTable.fnUpdate( jqInputs[6].value, nRow, 6, false );
	oTable.fnUpdate( jqInputs[7].value, nRow, 7, false );
	oTable.fnUpdate( jqInputs[8].value, nRow, 8, false );
	oTable.fnUpdate( jqInputs[9].value, nRow, 9, false );
	oTable.fnUpdate( jqInputs[10].value, nRow, 10, false );
	oTable.fnUpdate( jqInputs[11].value, nRow, 11, false );
	oTable.fnUpdate( jqInputs[12].value, nRow, 12, false );
	oTable.fnUpdate( jqInputs[13].value, nRow, 13, false );
	oTable.fnUpdate( jqInputs[14].value, nRow, 14, false );
	oTable.fnUpdate( jqInputs[15].value, nRow, 15, false );
	oTable.fnUpdate( jqInputs[17].value, nRow, 17, false );
	oTable.fnUpdate( jqInputs[18].value, nRow, 18, false );
	oTable.fnDraw();
}


$(document).ready(function() {
	
	var oTable = $('#area_code_add').dataTable();
	var nEditing = null;

	$('#new').click( function (e) {
		e.preventDefault();

		var aiNew = oTable.fnAddData( [
			'<a class="Change" href="">Change</a>','', '', '', '', '','', '', '', '', '','', '', '', '', '','<input type="checkbox" name="checkbox2" id="checkbox2">', '', '',] );
		var nRow = oTable.fnGetNodes( aiNew[0] );
		editRow( oTable, nRow );
		nEditing = nRow;
	} );
	
	
	var oTable = $('#area_code').dataTable();
	var nEditing = null;

	$('#new').click( function (e) {
		e.preventDefault();

		var aiNew = oTable.fnAddData( [
			'<a class="Change" href="">Change</a>','', '', '', '', '','', '', '', '', '','', '', '', '', '','<input type="checkbox" name="checkbox2" id="checkbox2">', '', '',] );
		var nRow = oTable.fnGetNodes( aiNew[0] );
		editRow( oTable, nRow );
		nEditing = nRow;
	} );

	$('#area_code a.delete').live('click', function (e) {alert("This record is getting deleted");
		e.preventDefault();

		var nRow = $(this).parents('tr')[0];
		oTable.fnDeleteRow( nRow );
	} );

	$('#area_code .Change').live('click', function (e) {
		e.preventDefault();

		/* Get the row as a parent of the link that was clicked on */
		var nRow = $(this).parents('tr')[0];

		if ( nEditing !== null && nEditing != nRow ) {
			/* Currently editing - but not this row - restore the old before continuing to Change mode */
			restoreRow( oTable, nEditing );
			editRow( oTable, nRow );
			nEditing = nRow;
		}
		else if ( nEditing == nRow && this.innerHTML == "Save" ) {
			/* Editing this row and want to save it */
			saveRow( oTable, nEditing );
			nEditing = null;
		}
		else {
			/* No Change in progress - let's start one */
			editRow( oTable, nRow );
			nEditing = nRow;
		}
	} );
} );





 $(function() {
	var availableTags = [
	"EX",
	"CD",
	"FL",
	"GU",
	"MA",
	"US",
	"MF",
	"MW",
	"M1",
	"M9",
	"NE",
	"PA",
	"P9",
	"SE"
	];
	$( "#tags" ).autocomplete({
	source: availableTags
	});
});