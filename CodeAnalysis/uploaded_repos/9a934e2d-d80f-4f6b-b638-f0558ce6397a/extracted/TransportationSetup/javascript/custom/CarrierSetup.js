var oTable = null;
var resetUpdateNew = false;
var orgComm = "";
var orgResponseCode = 0;
var iModifiedRowCnt = 0;
var bOpenRow = false;
var allResonCodes = "";
var username = "";
var dataList=new Array();
var dealerList=new Array();

$(document).ready(function() {
	//$("#input_vin").val("12234");
	allResonCodes = $("#allReasonCodes").val();
	username = $("#username").val();
	
	$("#contentTable").hide();
	//resetValues();
	$("#carrierTable").hide();
	
	 $('#searchCarrierCode').keyup(function(){
	        $(this).val($(this).val().toUpperCase());
	    });
	 $('#carrierCd').keyup(function(){
	        $(this).val($(this).val().toUpperCase());
	    });
	 
	
});


function toUpperCaseCarrier(){

	$('#carrierName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#firstName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#lastName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#titleName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#email').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingAddr1').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#shippingAddr1').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingAddr2').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#shippingAddr2').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingAddr3').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#shippingAddr3').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingCity').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#shippingCity').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	
}
function generateExcelReport(frm)
{

	
	$("#action").val('E');
	
	//document.forms[0].target="_blank";
	document.forms[0].submit();
	
}
function trimText(txt){
	txt.value = txt.value.trim();
}

function checkEmail(){
	
	var str=$("#email").val();
	
	var i=0,j=-1;
	var str1;
	var flag=false;
	while(1){
		if($("#email").val()==""){
			//alert(" Email Id  can't be empty"); 
			$("#email").focus();
			return true;
		}else{
			j=str.indexOf(";",j);
			if(j==-1) break;
			str1=str.substring(i,j);
	
			if (!(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(str1))){
				alert(str1 + " is not an Invalid E-mail Address!"); 
				$("#email").focus();
				flag=true;
				break;
			}
			i=j+1;
			j=j+1;
			continue;
		}
	}
	str1=str.substring(i);
	if(str1!=''&& !flag)
		if (!(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(str1))){
				alert(str1 + " is an Invalid E-mail Address!");
				$("#email").focus();
				return false;
		}
	return true;
	
}

function validateOnSubmit(action){
	if(action=='A' || action=='U'){
		if(($('#carrierName').val()).length==0){
			alert("Carrier name should be entered");
			return false;
		}else if (($('#carrierCd').val()).length==0){
			alert("Carrier code should be entered");
			return false;
		}else if ($("select[name='carrierType'] option:selected").index()==0){
			alert("Carrier type should be selected");
			return false;
		}else if ($("select[name='currencyCd'] option:selected").index()==0){
			alert("Currency should be selected");
			return false;
		}else if ($("select[name='currencyCd'] option:selected").index()==0){
			alert("Currency should be selected");
			return false;
		
		}else if (($('#mailingCity').val()).length==0){
			alert("Mailing address city is empty");
			return false;	
		}else if($('#mailingCountryCd option:selected').val()== 'US' || $('#mailingCountryCd option:selected').val()== 'CA' || $('#mailingCountryCd option:selected').val()== 'MX' )
			if($("select[name='mailingStateCd'] option:selected").index()==0){
				alert("Mailing address state is empty");
				return false;
			}else  {
				if(action=='A'){
					
					if(!checkEmail()==false){
						
						if(confirm("Do you want to add a new Carrier?")){
							return true;
						}else{
							return false;
						}
					
			}
				}else if(action=='U'){
					
					if(!checkEmail()==false){
						
						if(confirm("Do you want to update the Carrier?")){
							return true;
						}else{
							return false;
						}
			}
				}
			}
			
		else {
			if(action=='A'){
				if(confirm("Do you want to add a new Carrier?")){
					return true;
				}else{
					return false;
				}
			}else if(action=='U'){
				if(confirm("Do you want to update the Carrier?")){
					return true;
				}else{
					return false;
				}
			}
		}
		
		
	}else if(action=='R'){
	var status=confirm("Do you want delete this Carrier?");
	 	if(status==false){
	 		return false;
	 	}else{
	 		return true;
	 	}
	}else {
	
		return true;
	}
}

function resetAddUpdateDelete(){
	
	$("#searchCarrierCode").val('');
	 $("#searchCarrierName").val('');
	 $("#searchStatusCd").val('');
	 $("#searchTypeCd").val('');
	 $("#searchCurrencyCd").val('');
}

function searchReset(){
	
	 $("#searchCarrierCode").val('');
	 $("#searchCarrierName").val('');
	 $("#searchStatusCd").val('');
	 $("#searchTypeCd").val('');
	 $("#searchCurrencyCd").val('');
	 $("#carrierTable").hide();
	 $("#contentTable").hide();
	 $("#message1").html("");
	 $("#message").html("");
	 AddNewReset();
	
}
function AddNewReset(){
	console.log('AddNewReset method>>>>');
	globalShipingState='-1';
	 $("#carrierCd").val('');
	 $("#carrierType").val('');
	 $("#currencyCd").val('');
	 $("#statusId").val('');
	 $("#statusDate").val('');
	 $("#carrierName").val('');
	 document.getElementById("carrierCd").disabled = false;
	 $("#carrierCd").val('');
	 $("#carrierName").val('');
	 $("#carrierCd").val('');
	 $("#carrierCd").val('');
	 $("#carrierType").val('');
	 $("#currencyCd").val('');
	 $("#statusId").val('');
	 $("#statusDate").val($("#statusDate1").val());
	 $("#statusDateSpan").html($("#statusDate1").val());
	 
	 $("#email").val("");
	 
	 if(resetUpdateNew==false){
		 $("#message1").hide();
		 $("#message1").html("");
	 }
	 
	 $("#message").html("");
	 $("#message2").html("");
	 
	  $("#receivingErrorData1").val('');
	 $("#receivingDeliveryDate1").val('');
	  
	  $("#firstName").val('');
	  $("#lastName").val('');
	   $("#titleName").val('');
	    $("#phoneAcNo").val('');
	 $("#phoneExcNo").val('');
	  $("#phoneNo").val('');
	  $("#phoneExtensnNo").val('');
	  $("#faxAcNo").val('');
	  $("#faxExcNo").val('');
	  $("#faxNo").val('');
	   $("#cellAcNo").val('');
	 $("#cellExcNo").val('');
	 $("#cellNo").val('');
	 $("#message").html("");
	 
	 
	$("#mailingAddr1").val('');
	$("#mailingAddr2").val('');
	$("#mailingAddr3").val('');
	$("#mailingCity").val('');
	$("#mailingStateCd").val('');
	$("#mailingZipCd").val('');
	$("#mailingCountryCd").val('US');
	
	$("#shippingCountryCd").val('');
	$("#shippingZipCd").val('');
	$("#shippingStateCd").val('');
	$("#shippingCity").val('');
	$("#shippingAddr3").val('');
	$("#shippingAddr2").val('');
	$("#shippingAddr1").val('');
	$(".addNewHide").hide();
	globalMailingState="-1";
	globalShipingState="-1";
	pouplateStateDropDown ('mailingCountryCd','mailingStateCd','');
	$("#mailingStateCd").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
	$("#mailingCity").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
	$("#sameAsMailingAddresss").prop("checked","");
	$("#mailingStateCd").val('');
	sameAsMailling();
	
	 $("#receivingErrorData1").prop('checked', true);
	 $("#receivingDeliveryDate1").prop('checked', true);
	 $("#statusId1").prop('checked', true);
	
}


function clearSameAsMailing(){
	
	$('#sameAsMailingAddresss').attr('checked', false);
	
	  $("#shippingAddr1").prop('readonly', false);
	  $("#shippingAddr2").prop('readonly', false);
	  $("#shippingAddr3").prop('readonly', false);
	  $("#shippingCity").prop('readonly', false);
	  $("#shippingZipCd").prop('readonly', false);
	  $('#shippingStateCd').attr("style", "");
	  $('#shippingCountryCd').attr("style", "");
}
function isValidNumber(id){
	if(isNaN($("#"+id).val())){
		alert('please enter valid number');
		$("#"+id).val('');
	}
}
function isAlphaNumericOnBlur(id ,fieldName) {
	
	var str = document.getElementById(id).value;
	  var code, i, len;

	  for (i = 0, len = str.length; i < len; i++) {
	    code = str.charCodeAt(i);
	    if (!(code > 47 && code < 58) &&
	        !(code > 64 && code < 91) && 
	        !(code > 96 && code < 123) ) { 
	    	 alert("Please enter valid "+fieldName);
	    	 $("#"+id).val('');
	    	 $("#"+id).focus();
	    	 return false;
	    }else{
	    	
	    }
	  }
	  return true;
	}
function isAlphaNumericWithSpaceOnBlur(id ,fieldName) {
	
	var str = document.getElementById(id).value;
	  var code, i, len;

	  for (i = 0, len = str.length; i < len; i++) {
	    code = str.charCodeAt(i);
	    if (!(code > 47 && code < 58) &&
	        !(code > 64 && code < 91) && 
	        !(code > 96 && code < 123) && !(code==32)) { 
	    	 alert("Please enter valid "+fieldName);
	    	 $("#"+id).val('');
	    	 $("#"+id).focus();
	    	 return false;
	    }
	  }
	  return true;
	}


/**
 * needs to modify the populate method
 * Hari
 * 
 */
function doSearch() {
			populate();
			 $("#message1").html("");
			 $("#message2").html("");
			 
		
}
function showAddNew(){
	$("#contentTable").hide();
	AddNewReset();
	$("#carrierTable").show();
	$("#savebtn").show();
	$("#updatebtn").hide();
	$("#deletebtn").hide();
	$("#resetAddNew").show();
	$("#resetUpdate").hide();
	$("#formAddNewBack").show();
	$("#formEditBack").hide();
	$("#message1").hide();
}
var globalShipingState='-1';
var globalMailingState='-1';
function sameAsMailling(){
	  if($('#sameAsMailingAddresss').prop("checked") == true){
		  $("#shippingCountryCd").val($("#mailingCountryCd").val());
		  
		  if($("#mailingStateCd").val().length>0){
			  globalShipingState=$("#mailingStateCd").val();
			  globalMailingState=$("#mailingStateCd").val();
		  }
		  pouplateStateDropDown('shippingCountryCd','shippingStateCd');
		  $("#shippingAddr1").val($("#mailingAddr1").val());
		  $("#shippingAddr2").val($("#mailingAddr2").val());
		  $("#shippingAddr3").val($("#mailingAddr3").val());
		  $("#shippingCity").val($("#mailingCity").val());
		 
		  $("#shippingZipCd").val($("#mailingZipCd").val());
		  
		  $("#shippingAddr1").prop('readonly', true);
		  $("#shippingAddr2").prop('readonly', true);
		  $("#shippingAddr3").prop('readonly', true);
		  $("#shippingCity").prop('readonly', true);
		  $('#shippingStateCd').attr("style", "pointer-events: none;");
		  $('#shippingCountryCd').attr("style", "pointer-events: none;");
		  $("#shippingZipCd").prop('readonly', true);
		  $("#shippingStateCd").val($("#mailingStateCd").val());
		  
	  }else{
		/*  $("#shippingAddr1").val("");
		  $("#shippingAddr2").val("");
		  $("#shippingAddr3").val("");
		  $("#shippingCity").val("");
		  $("#shippingStateCd").val("");
		  $("#shippingZipCd").val("");
		  $("#shippingCountryCd").val("");*/
		  
		  $("#shippingAddr1").prop('readonly', false);
		  $("#shippingAddr2").prop('readonly', false);
		  $("#shippingAddr3").prop('readonly', false);
		  $("#shippingCity").prop('readonly', false);
		  $("#shippingZipCd").prop('readonly', false);
		  $('#shippingStateCd').attr("style", "");
		  $('#shippingCountryCd').attr("style", "");
		  //pouplateStateDropDown('shippingCountryCd','shippingStateCd');
	  }
	
	  
}
var globalCarrierCd;
function populateCarrierOperation( action,carried){
	
var parameters = "action=" + action;
$("#action").val(action);
	
	
	parameters += "&carrierName=" + $("#carrierName").val();
	if(carried=='0'){ 
		parameters += "&carrierCd=" + $("#carrierCd").val();
		globalCarrierCd=$("#carrierCd").val();
	}else{
		parameters += "&carrierCd=" +carried;
		globalCarrierCd=carried;
		
	}
	
	parameters += "&carrierType=" + $("#carrierType").val();
	parameters += "&currencyCd=" + $("#currencyCd").val();
	
	//$("#statusDate").val($("#statusDate1").val());
	parameters += "&statusDate=" + $("#statusDate").val();
	
	if(action=='A' || action=='U'){
	var status='I';
	if($("#statusId1").prop('checked')==true){
		status='A';
	}
	parameters += "&status=" +status;// $("#statusId1").val();
	
	
	var receivingErrorDataVAl='N';
		if($("#receivingErrorData1").prop('checked')==true){
			receivingErrorDataVAl='Y';
		}
		var receivingDeliveryDate='N';
		if($("#receivingDeliveryDate1").prop('checked')==true){
			receivingDeliveryDate='Y';
		}
	parameters += "&receivingErrorData=" +receivingErrorDataVAl; //$("#receivingErrorData1").val();
	parameters += "&receivingDeliveryDate=" +receivingDeliveryDate; //$("#receivingDeliveryDate1").val();
	}
	parameters += "&firstName=" + $("#firstName").val();
	parameters += "&lastName=" + $("#lastName").val();
	
	
	parameters += "&email=" + $("#email").val();
	parameters += "&titleName=" + $("#titleName").val();
	parameters += "&phoneAcNo=" + $("#phoneAcNo").val();
	parameters += "&phoneExcNo=" + $("#phoneExcNo").val();
	parameters += "&phoneNo=" + $("#phoneNo").val();
	parameters += "&phoneExtensnNo=" + $("#phoneExtensnNo").val();
	parameters += "&faxAcNo=" + $("#faxAcNo").val();
	parameters += "&faxExcNo=" + $("#faxExcNo").val();
	parameters += "&faxNo=" + $("#faxNo").val();
	
	parameters += "&cellAcNo=" + $("#cellAcNo").val();
	parameters += "&cellExcNo=" + $("#cellExcNo").val();
	parameters += "&cellNo=" + $("#cellNo").val();
	
	
	parameters += "&mailingAddr1=" + $("#mailingAddr1").val();
	parameters += "&mailingAddr2=" + $("#mailingAddr2").val();
	parameters += "&mailingAddr3=" + $("#mailingAddr3").val();
	parameters += "&mailingCity=" + $("#mailingCity").val();
	parameters += "&mailingStateCd=" + $("#mailingStateCd").val();
	parameters += "&mailingZipCd=" + $("#mailingZipCd").val();
	parameters += "&mailingCountryCd=" + $("#mailingCountryCd").val();
	
	parameters += "&shippingCountryCd=" + $("#shippingCountryCd").val();
	parameters += "&shippingZipCd=" + $("#shippingZipCd").val();
	parameters += "&shippingStateCd=" + $("#shippingStateCd").val();
	parameters += "&shippingCity=" + $("#shippingCity").val();
	parameters += "&shippingAddr3=" + $("#shippingAddr3").val();
	parameters += "&shippingAddr2=" + $("#shippingAddr2").val();
	parameters += "&shippingAddr1=" + $("#shippingAddr1").val();
	
	if(validateOnSubmit(action)){
		performOpertaions(parameters, action);
	}
	
	
	
}
function statusDateChange(checkedValue){
	
	if(checkedValue!=responseglobal.status){
		$("#statusDate").val($("#statusDate1").val());
		$("#statusDateSpan").html($("#statusDate1").val());
		
	}else{
		$("#statusDate").val(responseglobal.statusDt);
		$("#statusDateSpan").html(responseglobal.statusDt);
	}
}

function pouplateStateDropDown (countryCd,stateCd,action){
	

	var parameters = "action=C" ;
	console.log(globalMailingState+'countrtyty'+stateCd+'ty:::::'+$("#"+countryCd).val());
	parameters += "&countryCd=" + $("#"+countryCd).val();
	
	if($('#mailingCountryCd option:selected').val()== 'US' || $('#mailingCountryCd option:selected').val()== 'CA' || $('#mailingCountryCd option:selected').val()== 'MX' )
		{
			if(countryCd=='mailingCountryCd'){
				$("#mailingStateCd").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
				$("#mailingCity").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
			}
		}else{
			if(countryCd=='mailingCountryCd'){
				$("#mailingStateCd").attr('style','font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
				$("#mailingCity").attr('style','font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
			}
		}
	
	var dt = new Date();
	 var inMilliSeconds = dt.getTime();
	$.ajax({
        type: "POST",
        url: "carrierSetup.do?timeStamp=" + inMilliSeconds,
        data: parameters,
        datatype: 'json',
        async: true,
        beforeSend: function(x) {
                  $("#message").html("Loading.....");
         },
        success: function(response){
        	 $("#message").html("");
        	$("#"+stateCd+" option[value!='']").remove();
        	$.each(response.stateList, function() {
				var objModel = this;
				var option = $('<option></option>').attr( {
					value : objModel.value
				}).text(objModel.label);
				$("#"+stateCd).append(option);
			});
        	
        	
        	console.log(globalMailingState+'country:::::'+$("#"+countryCd).val());
        	if(globalMailingState!='-1' && stateCd=='mailingStateCd'){
        		$("#"+stateCd+"").val(globalMailingState);
        		console.log(globalMailingState+'if:a:::::::'+$("#"+countryCd).val());
        	}
        	if(globalShipingState!='-1' && stateCd=='shippingStateCd'){
        		$("#"+stateCd+"").val(globalShipingState);
        		console.log(globalMailingState+'if1:a:::::::');
        		
        	}
        	
        },
        error: function(xhr, ajaxOptions, thrownError){
        		alert("error code:"+xhr.status);
         }
         
    });
}
var responseglobal;
function performOpertaions(parameters, action){
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
   
	$.ajax({
          type: "POST",
          url: "carrierSetup.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
			$("#message1").html("");
			}
                    $("#message").html("Loading.....");
                    
           },
          success: function(response){
        	  /* Logic for Session out redirection */
        	  $("#message").html("");
        	  if(action=='I'){
        		  AddNewReset();
        			$("#contentTable").hide();
        			//resetValues();
        			$("#carrierTable").show();
        			$("#savebtn").hide();
        			$("#updatebtn").show();
        			$("#deletebtn").show();
        			$("#resetAddNew").hide();
        			$("#resetUpdate").show();
        			$("#formAddNewBack").hide();
        			$("#formEditBack").show();
        		}
        		  if(action=='A' ){
        			 
        			  if(response.responseCd=='00'){
        				  	
        				  	$("#message1").show();
        				  	$("#contentTable").hide();
        				  	$("#carrierTable").show();
        				  	$("#message1").html("Carrier details successfully added");
        				  	resetUpdateNew=true;
        				  	populateCarrierOperation( 'I',$("#carrierCd").val()); 
        				  	resetAddUpdateDelete();
  				  		
        			  }else {
        				  	$("#message1").show();
							$("#carrierTable").show();
    				  		$("#contentTable").hide();
    				  		$("#message1").show();
    				  		$("#message1").html(response.responseMessage);
    				  		resetAddUpdateDelete();
    				  		 
        			  }
        			 // populateCarrierOperation('I',globalCarrierCd);
        		  }else if(action=='U'){
        			  
        			  if(response.responseCd=='00'){
        				  		
        				  		$("#message1").show();
        				  		$("#contentTable").hide();
        				  		$("#carrierTable").show();
        				  		populateCarrierOperation( 'I',$("#carrierCd").val()); 
        				  		$("#message1").html("Carrier details successfully updated");
        				  		resetUpdateNew=true;
        				  		resetAddUpdateDelete();
        				 
						}else {
							$("#message1").show();
							$("#carrierTable").show();
    				  		$("#contentTable").hide();
    				  		$("#message1").html(response.responseMessage);
    				  		resetAddUpdateDelete();
								
						}
        			  
        			 // populateCarrierOperation('I',globalCarrierCd);
        		  }else if(action=='I'){
        			  AddNewReset();
        			  responseglobal=response;
        			  resetValueForEdit();
        				
        		  }else if(action=='R'){

        			orgResponseCode="";
              	    orgResponseCode = response.responseMessage;

        			  if(response.responseCd=='00'){
        				  $("#message1").show();
        				  $("#contentTable").hide();
 				  		  $("#carrierTable").hide();
 				  		  $("#message1").html("Carrier details successfully deleted");
				  		  resetAddUpdateDelete();
					}else {
						
						$("#message1").hide();
						$("#message2").show();
      				    $("#contentTable").hide();
				  		$("#carrierTable").hide();
				  		$("#message2").html(orgResponseCode);
				  		resetAddUpdateDelete();
						
					}
        			 
        			  
        		  }
        	  if(typeof response.responseCd == "undefined") {
					fnSessionOut();
					return;
        	  }
        	
        	
          	
          	
		    
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}




function resetValueForEdit(){
//	AddNewReset();
	response=responseglobal;
	 $('#sameAsMailingAddresss').prop("checked","false");
	 $("#carrierCd").val(response.carrierCd);
	 $("#carrierType").val(response.carrierType);
	 $("#currencyCd").val(response.paymentType);
	 $("#statusId").val(response.status);
	 $("#statusDate").val(response.statusDt);
	 $("#carrierName").val(response.carrierName);
	 $("#carrierCd").val(response.carrierName);
	 
	 document.getElementById("carrierCd").disabled = true;
	 $("#carrierName").val(response.carrierName);
//	 $("#carrierCd").val(response.carrierName);
	 $("#carrierCd").val(response.carrierCd);
//	 $("#carrierType").val(response.carrierCd);
	 $("#currencyCd").val(response.currency);
	 $("#email").val("");
	 if(response.status=='I'){
		 $("#statusId2").prop('checked', true);
	 }
	 if(response.status=='A'){
		 $("#statusId1").prop('checked', true);
	 }
	 
	 if(response.deliveryDataYes=='Y'){
		 $("#receivingDeliveryDate1").prop('checked', true);
	 }
	 if(response.deliveryDataYes=='N'){
		 $("#receivingDeliveryDate2").prop('checked', true);
	 }
	console.log('response.deliveryDataYes::::'+response.deliveryDataYes);
	 if(response.returnErrorDataYes=='Y'){
		 $("#receivingErrorData1").prop('checked', true);
	 }
	 if(response.returnErrorDataYes=='N'){
		 $("#receivingErrorData2").prop('checked', true);
	 }
	 $(".addNewHide").show();
	 
	 $("#statusId").val(response.status);
	 $("#statusDate").val(response.statusDt);
	 $("#statusDateSpan").html(response.statusDt);
	 
	  $("#receivingErrorData1").val(response.carrierName);
	 $("#receivingDeliveryDate1").val(response.carrierName);
	  $("#firstName").val(response.contractFirstName);
	  $("#lastName").val(response.contractLastName);
	   $("#titleName").val(response.contractTitleTx);
	    $("#phoneAcNo").val(response.phoneAcNo);
	 $("#phoneExcNo").val(response.phoneExcNo);
	  $("#phoneNo").val(response.phoneNo);
	  $("#phoneExtensnNo").val(response.extnsnNo);
	  $("#faxAcNo").val(response.faxAcNo);
	  $("#faxExcNo").val(response.faxExcNo);
	  $("#faxNo").val(response.faxphnNo);
	   $("#cellAcNo").val(response.clPhoneAcNo);
	 $("#cellExcNo").val(response.clPhoneExcNo);
	 $("#cellNo").val(response.clPhoneNo);
	 $("#email").val(response.contactEmail);
	 
	$("#mailingAddr1").val(response.mailingStreet1Address);
	$("#mailingAddr2").val(response.mailingStreet2Address);
	$("#mailingAddr3").val(response.mailingStreet3Address);
	$("#mailingCity").val(response.mailingCityName);
	
	$("#mailingZipCd").val(response.mailingZipCd);
	$("#mailingCountryCd").val(response.mailingCountryCd);
	
	$("#mailingStateCd").val(response.mailingStateCd);
	
	$("#shippingCountryCd").val(response.shippingCountryCd);
	$("#shippingZipCd").val(response.shippingZipCd);
	$("#shippingStateCd").val(response.shippingStateCd);
	$("#shippingCity").val(response.shippingCityName);
	$("#shippingAddr3").val(response.shippingStreet3Address);
	$("#shippingAddr2").val(response.shippingStreet2Address);
	$("#shippingAddr1").val(response.shippingStreet1Address);
	$("#lastUpdatedBy").html(response.userId);
	$("#lastUpdatedAt").html(response.lastUpdateTimeStamp);
	 console.log(response.mailingStateCd+'from field1::::::::'+response.shippingStateCd);
	globalMailingState=response.mailingStateCd;
	globalShipingState =response.shippingStateCd;
	  console.log(globalShipingState+'from field::::::::'+globalShipingState);
	pouplateStateDropDown ('mailingCountryCd','mailingStateCd','');
	pouplateStateDropDown ('shippingCountryCd','shippingStateCd','');
	if($("#mailingAddr1").val()==$("#shippingAddr1").val() &&
			$("#mailingAddr2").val()==$("#shippingAddr2").val() &&
			$("#mailingAddr3").val()==$("#shippingAddr3").val() &&
			$("#mailingCity").val()==$("#shippingCity").val() &&
			$("#mailingStateCd").val()==$("#shippingStateCd").val() &&
			$("#mailingZipCd").val()==$("#shippingZipCd").val() &&
			$("#mailingCountryCd").val()==$("#shippingCountryCd").val()
			){
		 $('#sameAsMailingAddresss').prop("checked","true");
		 sameAsMailling();
		
	}else{
		clearSameAsMailing();
	}
		
	if($('#mailingCountryCd option:selected').val()== 'US' || $('#mailingCountryCd option:selected').val()== 'CA' || $('#mailingCountryCd option:selected').val()== 'MX' )
	{
		
			$("#mailingStateCd").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
			$("#mailingCity").attr('style','background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
		
	}else{
		if(countryCd=='mailingCountryCd'){
			$("#mailingStateCd").attr('style','font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
			$("#mailingCity").attr('style','font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;');
		}
	}
}

var specialKeys = new Array();
specialKeys.push(8);  //Backspace
specialKeys.push(9);  //Tab
specialKeys.push(46); //Delete
specialKeys.push(36); //Home
specialKeys.push(35); //End
specialKeys.push(37); //Left
specialKeys.push(39); //Right
specialKeys.push(8);
function IsNumeric(e) {
    var keyCode = e.which ? e.which : e.keyCode;
    var ret = ((keyCode >= 48 && keyCode <= 57) || specialKeys.indexOf(keyCode) != -1);
   
    return ret;
}

var specialKeys1 = new Array();
specialKeys1.push(8);  //Backspace
specialKeys1.push(9);  //Tab
specialKeys1.push(46); //Delete
specialKeys1.push(36); //Home
specialKeys1.push(35); //End
specialKeys1.push(37); //Left
specialKeys1.push(39); //Right
specialKeys1.push(17); //ctrl
specialKeys1.push(86); //Right

function IsAlphaNumeric(e) {
    var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
    var ret = ((keyCode >= 48 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || keyCode == 32 || (keyCode >= 97 && keyCode <= 122) || (specialKeys1.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
   
    return ret;
}
/**
 * needs to modify the populate method
 * Hari
 * 
 */
function populate(){
	var action = "S";
	var parameters = "action=" + action;
	$("#action").val(action);
	
//	searchStatusCd  searchTypeCd searchCurrencyCd
	
	parameters += "&carrierCd=" + $("#searchCarrierCode").val();
	parameters += "&carrierName=" + $("#searchCarrierName").val();
	parameters += "&status=" + $("#searchStatusCd").val();
	parameters += "&carrierType=" + $("#searchTypeCd").val();
	parameters += "&currencyCd=" + $("#searchCurrencyCd").val();
	
	
	fetch_data(parameters, action);
}
/**
 * needs to modify the populate method
 * Hari
 * 
 */
function fetch_data(parameters, action){

	
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "carrierSetup.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
		
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	  $("#contentTable").show();
        		//resetValues();
        		$("#carrierTable").hide();
        		$("#savebtn").hide();
        		$("#updatebtn").hide();
        		$("#deletebtn").hide();
        	  /* Logic for Session out redirection */
        	 // alert(response.responseCd);
        	  if(typeof response.responseCd == "undefined") {
					fnSessionOut();
					return;
        	  }
        	
        	$('#message').html("");
        	orgResponseCode = response.responseCd;
//        	if(response.responseCode == 0){				
//				dataList = response.dataList;
//				dealerList=response.dealerList;
        		//if (response.dataList.length > 0) {
//        			$("#contentTable").show();
//        			$("#assignBtn").show();
//        			$("#downloadBtn").show();
        			createDataTable(response);
        			//datatableEventBinding();
        	    /*} else {
        	    	if (action == "FetchVMA") {
        	    		$('#message').html("Record not found.");
        	    	}
        	    }
        		
        		$('#input_dealer').focus();
        		
        		$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		*/
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
//			}
          	
          /*	if(action != "FetchVMA" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "FetchVMA" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	*/
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}

function populateCarrierValues1 (parameters, action){
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "carrierSetup.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	  $("#contentTable").show();
        		//resetValues();
        		$("#carrierTable").hide();
        		$("#savebtn").hide();
        		$("#updatebtn").hide();
        		$("#deletebtn").hide();
        	  /* Logic for Session out redirection */
        	 // alert(response.responseCd);
        	  if(typeof response.responseCd == "undefined") {
					fnSessionOut();
					return;
        	  }
        	
        	$('#message').html("");
        	orgResponseCode = response.responseCd;
//        	if(response.responseCode == 0){				
//				dataList = response.dataList;
//				dealerList=response.dealerList;
        		//if (response.dataList.length > 0) {
//        			$("#contentTable").show();
//        			$("#assignBtn").show();
//        			$("#downloadBtn").show();
        			createDataTable(response);
        			//datatableEventBinding();
        	    /*} else {
        	    	if (action == "FetchVMA") {
        	    		$('#message').html("Record not found.");
        	    	}
        	    }
        		
        		$('#input_dealer').focus();
        		
        		$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		*/
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
//			}
          	
          /*	if(action != "FetchVMA" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "FetchVMA" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	*/
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}

/**
 * needs to modify the populate method
 * Hari needs to revisit
 * 
 */
function createDataTable (response) {
	var displayStart = 0;
    var displayLength = 10;
    
    var dataArr = new Array();
    for(var icount=0; icount<response.searchList.length; icount++){
		var datarow = response.searchList[icount];
		
		var actionRadio = '';
		dataArr[icount] = new Array(
				"<a href='javascript:void(0);' onclick='return populateCarrierOperation(\"I\",\""+datarow.carrierCd+"\");' >"+datarow.carrierCd+"</a>",
				datarow.carrierAddress,
				datarow.carrierTypeDesc,
				datarow.statusDesc,
				datarow.currencyCd,
				datarow.carrierType,
				datarow.paymentType,
				datarow.status,
				datarow.street1Address	,	
				datarow.street2Address,
				datarow.street3Address,
				datarow.cityName,
				datarow.stateCd,
				datarow.carrierName,
				datarow.zipCd
				);
		
	}
    
    
//    if(response.dealerList.length>0){
//    	$('#assignBtn').show();
//    	$("#downloadBtn").show();
//    }else{
//    	$('#assignBtn').hide();
//    	$("#downloadBtn").hide();
//    }
		if(oTable!=null){
			displayStart = oTable.fnSettings()._iDisplayStart;
			displayLength = oTable.fnSettings()._iDisplayLength;
			//bSortingStatus = oTable.fnSettings().aaSorting;
			oTable.fnClearTable(this);
			oTable.fnDestroy();
			oTable=null;
		}

	oTable = $('#carrierGrid').dataTable({
  		"iDisplayStart": displayStart,
	 	"iDisplayLength": displayLength,
		"oLanguage": {"sSearch": "Filter records:"},
		"bAutoWidth": false,
		"bFilter": false,
		"bSort" : false,
		"sScrollY": "300px",
		"bScrollCollapse": true,
		"aaData": dataArr,
		"ordering": false,
		
		"aoColumns"   : [
		    { "sWidth": "10%" ,className: "left" },
			{ "sWidth": "25%" }, 
			{ "sWidth": "15%" }, 
			{ "sWidth": "15%" }, 
			{ "sWidth": "15%" }
			
		],
		 "columnDefs": [
		    		    { className: "left", "targets": [ 0 ] }
		    		  ]
		
	  });
	
	
	
	
}

function checkUncheckBox() {
	
	var chkLen = $("#vehManAssgmnt input[name=group1]:checked").length ;
	var len = $("#vehManAssgmnt input[name=group1]").length ;
	
	if(chkLen!=len) {
		$('#chkActionAll').prop("checked",false);
	} else {
		$('#chkActionAll').prop("checked",true);
	}
}



function fnSelectRecord(sender){
	$('#message').html("");
	
	$(document).unbind("keyup");
	$(document).keyup(function (e) {
		if (e.keyCode == 13) {
			//doSave();
		}
	});
	
	if(sender.checked){
		iModifiedRowCnt++;
		var nEditRow = $(sender).parents('tr')[0];
		fnEditRow(nEditRow, "EDIT");
		oTable.fnDraw(false);
		
		$("#reasonCode_" + iModifiedRowCnt).focus();
		
		bOpenRow=true;
		
	} else {
		fnRestoreTable(sender);
	}
}

function fnOpenEditModeAll(sender){
	if(sender.checked){
		$.each($("input[name=group1]"),function(){
			if(!this.checked){
				iModifiedRowCnt++;
				var nEditRow = $(this).parents('tr')[0];
				this.checked=true;
				fnEditRow(nEditRow, "EDIT");
			}
		});
		
		bOpenRow=true;
		$(document).unbind("keyup");
		$(document).keyup(function (e) {
			if (e.keyCode == 13) {
				//doSave();
			}
		});
	} else {
		$.each($("input[name=group1]"),function(){
			if(this.checked) {
				this.checked=false;
				fnRestoreTable(this);				
			}
		});
		
	}
}
/**
 * needs to modify the populate method
 * Hari
 * actionRadio,
				datarow.dlrCd,
				datarow.VIN_CD,
				datarow.MDL_YR_DT,
				datarow.carLine,
				datarow.MDL_CD,
				datarow.EXT_COLOR_CD,
				datarow.INT_COLOR_CD,
				datarow.currentStatus,
				datarow.currentLocation	
 */
function fnEditRow(oRow,action){
	var aData = oTable.fnGetData(oRow);
	var jqTds = $('>td', oRow);

	var reasonSelect = $('<select style="width:90px ;"></select>').attr({name:"dlrCode", id:"dlrCode_" + iModifiedRowCnt});
	reasonSelect.attr('record-cnt', iModifiedRowCnt);
	reasonSelect.append($('<option>--Select--</option>').attr({value:""}));
	var reasonData = allResonCodes.split("|", 30);
	   for(var icount=0; icount<dealerList.length; icount++){
			
		var optionText = 	dealerList[icount];
		var option = $('<option></option>').attr({
			value:dealerList[icount]
		}).text(optionText);
		
		reasonSelect.append(option);
		
	}
	$(jqTds[1]).html("");
	$(jqTds[1]).append(reasonSelect);  
	if (aData[2] != "") {
		jqTds[2].innerHTML = '<input type="text" name="vin" id="vin_'+iModifiedRowCnt+'" maxlength="17" size="17" value="'+aData[2]+'" record-cnt='+iModifiedRowCnt+' style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	} else {
		jqTds[2].innerHTML = '<input type="text" name="vin" id="vin_'+iModifiedRowCnt+'" maxlength="17" size="17" value="'+aData[2]+'" record-cnt='+iModifiedRowCnt+' style="width:98%; padding:0.1em 0 0.1em 0; height:15px;">';
	}
	
	if (aData[3] != "") {
		jqTds[3].innerHTML = '<input type="text" name="mdlYR" id="mdlYR_'+iModifiedRowCnt+'" maxlength="4" size="4" value="'+aData[3]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	} else {
		jqTds[3].innerHTML = '<input type="text" name="mdlYR" id="mdlYR_'+iModifiedRowCnt+'" maxlength="4" size="4" value="'+aData[3]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;">';
	}
	
	if (aData[4] != "") {
		jqTds[4].innerHTML = '<input type="text" name="carline" id="carline_'+iModifiedRowCnt+'" maxlength="3" size="3" value="'+aData[4]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	} else {
		jqTds[4].innerHTML = '<input type="text" name="carline" id="carline_'+iModifiedRowCnt+'" maxlength="3" size="3" value="'+aData[4]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;">';
	}
	
	
	
	jqTds[5].innerHTML = '<input type="text" name="model" id="model_'+iModifiedRowCnt+'" maxlength="10" size="10" value="'+aData[5]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	jqTds[6].innerHTML = '<input type="text" name="colorExt" id="colorExt_'+iModifiedRowCnt+'" maxlength="15" size="15" value="'+aData[11]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	jqTds[7].innerHTML = '<input type="text" name="colorInt" id="colorInt_'+iModifiedRowCnt+'" maxlength="15" size="15" value="'+aData[12]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	jqTds[8].innerHTML = '<input type="text" name="currentstatus" id="currentstatus_'+iModifiedRowCnt+'" maxlength="15" size="15" value="'+aData[8]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	jqTds[9].innerHTML = '<input type="text" name="currentloc" id="currentloc_'+iModifiedRowCnt+'" maxlength="5" size="5" value="'+aData[9]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">'
	 +'<input type="hidden" name="LAST_UPDT_TM" id="LAST_UPDT_TM_'+iModifiedRowCnt+'" maxlength="15" size="15" value="'+aData[10]+'" style="width:98%; padding:0.1em 0 0.1em 0; height:15px;" disabled="disabled">';
	
	$('#soldDealer_' + iModifiedRowCnt).change(function() {
		var id = $(this).attr("record-cnt");
		var soldDealer = $('#soldDealer_' + id).val();
		var shipLoc = $('#shipLoc_' + id).val();
		if (shipLoc == "") {
			$("#shipLoc_" + id).val(soldDealer);
		}
	});
}

function fnRestoreTable(sender){
	$('#message').html("");
	var nEditRow = $(sender).parents('tr')[0];
	var aData = oTable.fnGetData(nEditRow);
	var jqTds = $('>td', nEditRow);
	for ( var i=0, iLen=jqTds.length ; i<iLen ; i++ ) {
		oTable.fnUpdate( aData[i], nEditRow, i, false );
	}
	oTable.fnDraw(false);
	
	var selRowCnt = 0;
	var objModelRadioButtons = $("input[name=group1]");
	for(var icount=0; icount < objModelRadioButtons.length; icount++){
		var objModelRadio = objModelRadioButtons[icount];
		if(objModelRadio.checked){
			selRowCnt++;
		}
	}
	if (selRowCnt == 0) {
		bOpenRow=false;
		
		$(document).unbind("keyup");
		$(document).keyup(function (e) {
			if (e.keyCode == 13) {
				//doSearch();
			}
		});
	}
	
}
/**
 * needs to modify the populate method
 * Hari
 * 
 */
function doSave(){
	var selected_item_count = 0;
	var bReturn = true;
	var allConcatRecords = "";
	var action = "Bulk_Assign";
	
	$.each($("select[name=dlrCode]"),function(){
		if (bReturn) {
			var record_cnt = $(this).attr("record-cnt");

	        var dlrCode = $("#dlrCode_" + record_cnt).val();

	        if (dlrCode == "") {
	    		alert("Please select the  Dealer.");
	    		$("#dlrCode_" + record_cnt).focus();
	    		bReturn = false;
	    		return false;
	    	}
	        
	       
			
	        var vin = $("#vin_" + record_cnt).val();
	        var mdlYR = $("#mdlYR_" + record_cnt).val();
	        var model = $("#model_" + record_cnt).val();
	   
	        
	        var colorExt =  $("#colorExt_" + record_cnt).val();
	        var colorInt = $("#colorInt_" + record_cnt).val();
	        
	       
	
			var last_updt_tm = $("#LAST_UPDT_TM_" + record_cnt).val();
	        
			if(last_updt_tm == "") {
				last_updt_tm = "0001-01-01 00:00:00.000000";
			}
			
			allConcatRecords += fnRightPadding(dlrCode, 5, " ") + " ";
			allConcatRecords += fnRightPadding(vin, 17, " ") + " ";
			allConcatRecords += fnRightPadding(mdlYR, 4, " ") + " ";
			allConcatRecords += fnRightPadding(model, 12, " ") + " ";
			allConcatRecords += fnRightPadding(colorExt, 3, " ") + " ";
			allConcatRecords += fnRightPadding(colorInt, 3, " ") + " ";
			allConcatRecords += fnRightPadding(last_updt_tm, 26, " ") + " ";
			allConcatRecords += fnRightPadding(username, 8, " ") + " ";
		}
		selected_item_count++;
	});
	
	if (bReturn) {
		if(selected_item_count == 0){
			alert("Please select a record to assign.");
			bReturn = false;
			return false;
		} else {
		
			var parameters = "allConcatData=" + allConcatRecords;
			parameters += "&ACTION=" + action;
			parameters += "&RGN_CD=" + $("#input_region").val();
			parameters += "&PORT_CD=" + $("#input_port").val();
			parameters += "&CRLN_CD=" + $("#input_carline").val();
			parameters += "&MDL_YR_DT=" + $("#input_model_year").val();
			parameters += "&MDL_CD=" + $("#input_model").val();
			parameters += "&EMSSN_CD=" + $("#input_emssn").val();
			parameters += "&EXT_CLR=" + $("#input_ext_clr").val();
			parameters += "&INT_CLR=" + $("#input_int_clr").val();
			parameters += "&VIN_CD=" + $("#input_vin").val();
			parameters += "&SOLD_DLR=" + $("#input_sold_to_delaer").val();
			parameters += "&SHIP_LOC=" + $("#input_ship_to_loc").val();
			
			//alert("parameters: " + parameters);
			fetch_data(parameters, action);
		}
	}
}



function doDownload(){
	
	var bReturn = true;
	var allConcatRecords = "";
	var action = "EXCEL_DOWNLOAD";
	
	$("#action").val('EXCEL_DOWNLOAD')
	document.forms[0].submit();
	
} 


/**
 * needs to modify the populate method
 * Hari
 * 
 */
function fnMakeDatatableForExportPrint(){
	var objMainTable = $('<table  id="rptData" border="1" cellpadding="6" cellspacing="3"></table>');
	
	var thead= $("<thead></thead>");
	objMainTable.append(thead);
	
	var objTr= $("<tr></tr>");
	thead.append(objTr);
	
	var objTh =$('<th></th>').html('Reason Code');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Sold Dealer');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Ship Location');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Re-Price');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Order Ref/VIN');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Model Year');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Model');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Ext Color');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Int Color');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Status');
	objTr.append(objTh);
	
	objTh =$('<th></th>').html('Special Type');
	objTr.append(objTh);
	
	var tbody = $("<tbody></tbody>");
	objMainTable.append(tbody);
	
	if(dataList.length==0){
		objTr= $("<tr></tr>").addClass("odd");
		tbody.append(objTr);
		var objTd =$('<td style="width:100%;text-align:center;">Data not available</td>').attr('colspan',4);
		objTr.append(objTd);
		
	}
	
	var iRowCount=0;
	for(var imodelcount=0; imodelcount<dataList.length;imodelcount++){
		var datarow = dataList[imodelcount];
		var objCTr = $('<tr height="25px"></tr>"');
		if(iRowCount%2==0)
			objCTr.addClass("even");
		else
			objCTr.addClass("odd");
		tbody.append(objCTr);
		
		var objCTd = $('<td style="text-align:center;"></td>').html(datarow.RSN_CD);
		objCTr.append(objCTd);
		
		var objCTd = $('<td style="text-align:center;"></td>').html(datarow.SOLD_DLR);
		objCTr.append(objCTd);	
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.SHIP_LOCT);
		objCTr.append(objCTd);	
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.RE_PRICE);
		objCTr.append(objCTd);	
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.VIN_CD);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.MDL_YR_DT);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.MDL_CD);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.EXT_COLOR_CD);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.INT_COLOR_CD);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.STATUS);
		objCTr.append(objCTd);
		
		objCTd = $('<td style="text-align:center;"></td>').html(datarow.SPCL_TYPE_CD);
		objCTr.append(objCTd);
		
		iRowCount++;
	}
	return objMainTable;
}