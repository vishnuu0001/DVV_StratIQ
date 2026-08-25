<!doctype html>
<%@ taglib uri="/WEB-INF/struts-tiles.tld" prefix="tiles" %> 
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<html>
	<HEAD><title><tiles:getAsString name="title" ignore="true" /></title>
	<META http-equiv=Content-Type content="text/html; charset=utf-8">
	<meta http-equiv="x-ua-compatible" content="IE=edge" />	
		<!-- VALUE OF BELOW SCRIPT COMMING FRO SERVER SITE. PLEASE DON"T REMOVE THIS -->
		${defaultScriptValues}
		
		<!--TABLE SCRIPT -->
		<script type="text/javascript" src="javascript/json2.js"></script>
		<script type="text/javascript" src="javascript/jquery-1.9.0.min.js"></script>
		
		<script type="text/javascript">
		$(document).ready(function() {
//  $("#selectedCountryCd").html("Country Code: "+sCountryCode);
			   var currentUrl = window.location.pathname;
			   var locationUrlArr = currentUrl.split("/");
			   var url = locationUrlArr[locationUrlArr.length-1];
			   if(url=="UploadMscCSV.do")
			   		url="R2Conversion.do";
				if(url=="UploadBulkMscCSV.do")
					url="R2BulkConversion.do";
			   		
			   var open_tab_id="menu_group_0";
			    //CODE FOR SUB-MENU ACTIVATION
				$('.menuitem').each(function(){
					var href = $(this).attr("href");
					var hrefarr =href.split("/");
					var actionpart = hrefarr[hrefarr.length-1];
					$(this).removeAttr('class');
					if(actionpart.toUpperCase()==url.toUpperCase()){
						$(this).addClass("menuitem active");
						open_tab_id= $(this).attr("sub-menu-id");
					}
					else{
						$(this).addClass("menuitem");
					}
					
					
				});
				
				//if(sUserCountryCode!='US'){
					//$("#Country").hide();
				//	$("#country_menu").hide();
				//}else{
				//	$('.menuitem-country').each(function(){
					//	$(this).removeAttr('class');
						//if($(this).attr("country-code")==sCountryCode){
						//	$(this).addClass("menuitem-country active");
						//}else{
						//	$(this).addClass("menuitem-country");
						//}
					//});
			//	}
				//CODE FOR SUB-MENU ACTIVATION
				
				//CODE FOR MENU SHOW?HIDE
				var all_manu_tabs = $(".submenu");
				$.each(all_manu_tabs,function(){
					if($(this).attr("id")==open_tab_id)
						$(this).show();
					else
						$(this).hide();
				});
				
				$("div.menuTitle").click(function(e){
				   var selected_manu = this;
				   $.each(all_manu_tabs,function(){
						if($(this).attr("id")==$(selected_manu).attr("sub-menu-id"))
							$(this).show(500);
						else
							$(this).hide(500);
					});
					
				});
				//END-CODE FOR MENU SHOW?HIDE
			   
			    $('a.menuitem').click(function(e){
			    	if(bOpenRow || unSavedData){
			    		var bConfirm= confirm("You have some unsaved data. Do you want to leave this page?");
			    		if(bConfirm){
			    			return true;
			    		}else{
			    			return false;
			    		}
			    	}
			    	return true;
			    });
			    
				$('a.menuitem-country').click(function(e){
					var counrty_code = $(this).attr("country-code");
					var bConfirm=true;
					if(bOpenRow || unSavedData){
			    		bConfirm= confirm("You have some unsave data.Do you want to leave this page?");
			    	}
			    	
					if(bConfirm){
						window.location.href="country.do?countryCd="+counrty_code+"&returnUrl="+url;
					}
					return false;
				});
				
				var modelYearOptions = $("#modelYear>option");
				$.each(modelYearOptions,function(){
					if(Number(this.value)==Number(iDefaultModelYear))
						this.selected=true;
					else
						this.selected=false;
				});
				
			    $('a.car-line').click(carLineClickHandler);
			    
			 
			   
	});				
	
	function fnPopulateCarlines(modelYear,carlineDropdownId,selectedCarlineCd){
		$("#"+carlineDropdownId+" option[value!='']").remove();
		$.each(oModelYearCarlineList,function(){
			if(Number(this[0])==Number(modelYear)){
				var option = $('<option></option>').attr({
					value:this[1]
				}).text(this[1]);
				$("#"+carlineDropdownId).append(option);
			}
		});
		
		if(selectedCarlineCd!=""){
			$.each($("#"+carlineDropdownId+">option"),function(){
				if(selectedCarlineCd==this.value)
					this.selected=true;
				else
					this.selected=false;
			});
		}
	}
	
	function fnPopulateCarlinesBasedOnYear(modelYear,carlineDropdownId,selectedCarlineCd){
		$("#"+carlineDropdownId+" option[value!='']").remove();

		$.each(oModelYearCarlineList,function(){
			if(Number(this[0])==Number(modelYear)){
				var option = $('<option></option>').attr({
					value:this[1]
				}).text(this[1]);
				$("#"+carlineDropdownId).append(option);
			}
			$("#"+carlineDropdownId).multipleSelect({placeholder: "SELECT CARLINE"});
			//$("#CRLN_CD_TD").prop("disabled", false);
		});
		
		if(selectedCarlineCd!=""){
			$.each($("#"+carlineDropdownId+">option"),function(){
				if(selectedCarlineCd==this.value)
					this.selected=true;
				else
					this.selected=false;
			});
		}
	}
	function fnPopulateModels(modelYear,carlineCd,modelDropdownId,selectedModelCd){
		$("#"+modelDropdownId+" option[value!='']").remove();
		if(carlineCd==null||carlineCd==""){
			return;
		}
		var parameters = "MDL_YR_DT="+modelYear+"&CRLN_CD="+carlineCd+"&CNTRY_CD="+sCountryCode+"&SAVE_IN_SESSION=true";
		var dt = new Date();
		var inMilliSeconds = dt.getTime();
		$.ajax({						          
			  type: "POST",
			  url: "FetchModel.do?timeStamp="+inMilliSeconds,
			  data: parameters,
			  datatype: 'json',
			  async: false,
			  success: function(response){
				 if(typeof response.responseCode == "undefined"){
					fnSessionOut();
					return;
				}
			
				 var iModelCount = 0;
				 $.each(response.modelList,function(){
						 var option = $('<option></option>').attr({
								value:this.MDL_CD
						}).text(this.MDL_CD);
						
						if(iModelCount==0)
							option.attr("selected",true);
							
						$("#"+modelDropdownId).append(option);
						iModelCount++;
				  });
				  
				 if(selectedModelCd!=""){
					$.each($("#"+modelDropdownId+" >option"),function(){
						if(this.value==selectedModelCd)
							this.selected = true;
						else
							this.selected = false;
					});
				 }
			   },
			  error: function(xhr, ajaxOptions, thrownError){
					alert("Error code:"+xhr.status);
			  }
		  });
	}	
	</script>
		
		<script type="text/javascript" src="javascript/jquery.dataTables.js"></script>
		<script src="javascript/jquery-ui.min.js" type = "text/javascript"></script>
		<link href="css/style.css?v=1.1" type=text/css rel="stylesheet"/>
		<link href="css/jquery-ui.css?v=1.1" rel = "Stylesheet" type="text/css" />


</HEAD>
		<BODY>
			<div class="container-fluid">
	<div class="row-fluid headerWrapper">
		<div class="span12 pull-left">
			<tiles:insert attribute="header"/>
		</div>
	</div>	
	
	<div class="row-fluid">
		<div class="span2">
			<tiles:insert attribute="menu"/>
		</div>
		
		<div class="span10" style="margin: 5px; padding-left: 30px;">
			<tiles:insert attribute="body"/>
		</div> 
	</div>
	
	<div class="row-fluid">
		<div class="span12 footer">
			<tiles:insert attribute="footer"/> 
		</div>
		
	</div>
		
			
		
   </div>
		</BODY>
</html>
