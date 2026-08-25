
			<!--FOOTER SECTION -->
			<div id=footer>
				  Mazda North American Operations ©2013 Mazda North American Operations
				</div>
				<div id="pop-up-lighbox">
				  <div class="top-arrow"></div>
				  <div class="light_box_header">
				    <table width="100%">
				      <tbody><tr>
				        <td><span>
				          <h5>Select Model </h5>
				          </span></td>
				        <td><span class="pull-right"> <a href="javascript:void(0)" onclick="close_lighbox()" class="icon-remove-sign"></a></span></td>
				      </tr>
				    </tbody></table>
				  </div>
				 <div class="lightbox_content" id="carline_modelList_lightbox">
				    
				  </div>
  			</div>
  
			<!-- FOOTER (div id=footer) ENDS-->
<script type="text/javascript">
function close_lighbox(){
	$("#pop-up-lighbox").hide();
	$("#pop-up-lighbox1").hide();
}

function carLineClickHandler(e) {
	if(bOpenRow){
		var bConfirm= confirm("You have some unsaved data. Do you want to leave this page?");
		if(!bConfirm){
			return false;
		}
	}
    	
	var moveLeft = 118;
	var moveDown = 12;
	var carline_name = $(this).attr('carline-name');
	var carline_cd = $(this).attr('carline-cd');
	var year=getModelYear();
	if(Number(year)==0){
		alert("Please select model year.");
		return false;
	}
	
	if ($('div#pop-up-lighbox').is(':visible')){
			$('div#pop-up-lighbox').hide();
	}
	else{
		
		var parameters = '';//"MDL_YR_DT="+year+"&CRLN_CD="+carline_cd+"&CNTRY_CD="+sCountryCode+"&SAVE_IN_SESSION=true";
		var dt = new Date();
	    var inMilliSeconds = dt.getTime();
	    $.ajax({						          
	    	  type: "POST",
	          url: "FetchModel.do?timeStamp="+inMilliSeconds,
	          data: parameters,
	          datatype: 'json',
	          async: false,
	          beforeSend: function(x) {
	                   
	           },
	          success: function(response){
	        	 
	        	  var modelList = response.modelList;
	        	  var objModelTbl = $("<table></table>");
	        	  
	        	   if(modelList.length==0){
	        		   var objTr = $("<tr></tr>");
	        			objModelTbl.append(objTr);
	        			var objTd =$("<td></td>").text("No Model Found.");
	        			objTr.append(objTd);
	        	   }
	        	   
	        	  for(var iModel=0;iModel<modelList.length;iModel++  ){
	        			var objModel = modelList[iModel];
	        			var objTr = $("<tr></tr>");
	        			objModelTbl.append(objTr);
	        			var objTd =$("<td></td>");
	        			objTr.append(objTd);
	        			var fnName = "select_model('"+year+"','"+carline_cd+"','"+carline_name+"','"+objModel.MDL_CD+"')";
	        			var jsAnchor = document.createElement("a");
	        			jsAnchor.onclick = new Function(fnName);
	        			var objAnchor = $(jsAnchor).attr({
	        				href:"javascript:void(0)"
	        			}).html(objModel.MDL_CD);
	        			objTd.append(objAnchor);
	        			
	        			
	        		}
	        	  	$("#carline_modelList_lightbox").html("");
	        		$("#carline_modelList_lightbox").append(objModelTbl);
	        		
	        		
	           },
	          error: function(xhr, ajaxOptions, thrownError){
	          		 alert("Failed");
	          }
	      });
	    
		//bind_data(parameters,"FETCHMODEL");
		$('div#pop-up-lighbox').show().css('top', e.pageY + moveDown).css('left', e.pageX - moveLeft);
	}
}

function getModelYear(){
	var year=0;
	if($("#modelYear").val()!=undefined)
		year = $("#modelYear").val();
	/*
	var radiobuttons = document.getElementsByName("modelYear");
	for(var icount=0;icount<radiobuttons.length;icount++){
		var radioButton = radiobuttons[icount];
		if(radioButton.checked){
			year= radioButton.value;
			break;
		}
	}*/
	
	return year;
	
}
	
function doExportEcel(){
	
	//CODE FOR CHECKING BROWSER
    var check = function (r) {
        return r.test(ua);
    };
    var ua = navigator.userAgent.toLowerCase();
    var isOpera = check(/opera/);
    var isChrome = check(/chrome/);
    var isWebKit = check(/webkit/);
    var isSafari = !isChrome && check(/safari/);
    var isIE = !isOpera && (check(/msie/)||check(/.net/)||check(/trident/)||check(/rv:11.0/));
    //END-CODE FOR CHECKING BROWSER
    
	var objDataTable = makeDatatable();
    if(isIE){
		xlsIE(objDataTable);
    }else{
		var objExportDiv = $("<div><div>");
		objExportDiv.append(objDataTable);
		window.open('data:application/vnd.ms-excel,' + encodeURIComponent(objExportDiv.html()));
		objExportDiv.html("");
     }
	 return false;
}
	
function xlsIE(objDataTable){
		var ExcelApp = new ActiveXObject("Excel.Application");
		var wb=ExcelApp.WorkBooks.Add();
		var ExcelSheet = wb.Sheets("Sheet1");
		var	i = 0;
		var j = 0;
		var findNbsp = '&nbsp;';
		var regnbsp = new RegExp(findNbsp, 'g');
		$.each(objDataTable,function(){
			var tbl=this;
			$.each($.find("tr",tbl),function(){
				var row=this;
				$.each($.find("th",row),function(){
					//ExcelSheet.Cells(j+1,i+1).Font.Bold = true;
					var html =this.innerHTML.replace(/<(?:.|\n)*?>/gm, '');
					var finalText = html.replace(regnbsp, ' ');
					finalText = finalText.replace("/49", "/2049");
					ExcelSheet.Cells(j+1,i+1).Value = finalText;
					i++;
				 });
				 
				$.each($.find("td",row),function(){
					var html =this.innerHTML.replace(/<(?:.|\n)*?>/gm, '');
					var finalText = html.replace(regnbsp, ' ');
					finalText = finalText.replace("/49", "/2049");
					ExcelSheet.Cells(j+1,i+1).Value = finalText;
					i++;
				 });
				 
				i=0;
				j++;
			});
		});
		
		ExcelApp.Application.Visible = true; 
		
		
}
	
function printData(){
	var objDataTable = makeDatatable();
	var objExportDiv = $("<div><div>");
	objExportDiv.append(objDataTable);
	objExportDiv.printHTML();
	 return false;
}


</script>