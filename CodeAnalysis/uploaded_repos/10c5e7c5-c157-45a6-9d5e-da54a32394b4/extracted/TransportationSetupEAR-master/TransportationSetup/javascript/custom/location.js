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
	
	$("#contentTable").hide();
	$("#assignBtn").hide();
	$("#downloadBtn").hide();
	$("#locationTable").hide();
	$("#locationMailingInformation").hide();
	
	
});


function toUpperCaseLocation(){
	
	$('#locationCode').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });	
	
	$('#locationsetupName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#locationsetupfirstName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#locationsetupCode').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	
	$('#locationsetuplastName').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });

	$('#locationsetupTitle').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet1').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet2').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet3').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet4').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingStreet5').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingCity1').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#mailingCity2').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
	$('#locationsetupEmail').keyup(function(){
        $(this).val($(this).val().toUpperCase());
    });
	
}

function checkEmail(){
	
	var str=$("#locationsetupEmail").val();
	
	var i=0,j=-1;
	var str1;
	var flag=false;
	while(1){
		if($("#locationsetupEmail").val()==""){
			//alert(" Email Id  can't be empty"); 
			$("#locationsetupEmail").focus();
			return true;
		}else{
			j=str.indexOf(";",j);
			if(j==-1) break;
			str1=str.substring(i,j);
	
			if (!(/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(str1))){
				alert(str1 + " is not an Invalid E-mail Address!"); 
				$("#locationsetupEmail").focus();
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
				$("#locationsetupEmail").focus();
				return false;
		}
	return true;
	
}


function setValue2(){
	resetUpdateNew=true;
//	$("#message1").hide();
//	$("#message1").html("");
	$('#locationCode').val($('#locationsetupCode').val());
	doSearch();
	
} 

function numericCheck(){
	
	 	var check = true;
	 	var phoneNo=$("#locationsetupPhone1").val();
	   check = IsNumeric(phoneNo);
	  if(check==false){
	  	alert("Bus area code should be numeric");
	  	$("#locationsetupPhone1").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#locationsetupPhone2").val());
	  if(check==false){
	  	alert("Bus exchange code should be numeric");
	  	$("#locationsetupPhone2").focus();
	  	return false;
	  }
	  check = IsNumeric($("#locationsetupPhone3").val());
	  if(check==false){
	  	alert("Bus phone number should be numeric");
	  	$("#locationsetupPhone3").focus();
	  	return false;
	  }
	  check = IsNumeric($("#locationsetupPhone4").val());
	  if(check==false){
	  	alert("Bus Ext number should be numeric");
	  	$("#locationsetupPhone4").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#locationsetupfaxAreaCode1").val());
	  if(check==false){
	  	alert("Fax area code should be numeric");
	  	$("#locationsetupfaxAreaCode1").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#locationsetupfaxAreaCode2").val());
	  if(check==false){
	  	alert("Fax exchange code should be numeric");
	  	$("#locationsetupfaxAreaCode2").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#locationsetupfaxAreaCode3").val());
	  if(check==false){
	  	alert("Fax phone number should be numeric");
	  	$("#locationsetupfaxAreaCode3").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#locationsetupcellAreaCode1").val());
	  if(check==false){
	  	alert("Cell area code should be numeric");
	  	$("#locationsetupcellAreaCode1").focus();
	  	return false;
	  }
	  check = IsNumeric($("#locationsetupcellAreaCode2").val());
	  if(check==false){
	  	alert("Cell exchange code should be numeric");
	  	$("#locationsetupcellAreaCode2").focus();
	  	return false;
	  }
	  check = IsNumeric($("#locationsetupcellAreaCode3").val());
	  if(check==false){
	  	alert("Cell phone number should be numeric");
	  	$("#locationsetupcellAreaCode3").focus();
	  	return false;
	  }
	  
	  check = IsNumeric($("#mailingZipCd1").val());
	  if(check==false){
	  	alert("Zip code should be numeric");
	  	$("#mailingZipCd1").focus();
	  	return false;
	  }
	  check = IsNumeric($("#mailingZipCd2").val());
	  if(check==false){
	  	alert("Zip code should be numeric");
	  	$("#mailingZipCd2").focus();
	  	return false;
	  }
	  check = IsNumeric($("#location_zipCode").val());
	  if(check==false){
	  	alert("Zip code should be numeric");
	  	$("#location_zipCode").focus();
	  	return false;
	  }
	  
	  return true;
}

/**checks is the given input is a Integer**/
function IsNumeric(sTextObject)
{
   var ValidChars = "0123456789";
   var IsNumber=true;
   var char;
   var i;

   if(sTextObject.length ==0){    
     return IsNumber;  
    }
   for (i = 0; i < sTextObject.length && IsNumber == true; i++) 
   { 
      char = sTextObject.charAt(i); 
      if (ValidChars.indexOf(char) == -1) 
         {
            IsNumber = false;
         }
   }
   if(!IsNumber)
   {
      /* sTextObject.select();*/
   }
   return IsNumber;
}


function doLeftFilterReset(){
	
	$("#locationName").val('');
	$("#locationCode").val('');
	$("#input_country").val('');
	$("#input_region").val('');
	$("#input_State").val('');
	$("#location_zipCode").val('');
	$("#input_City").val('');
	$("#input_statusCode").val('');
	$("#input_Type").val('');
	
}

var globalmailing_State2="-1";
function sameAsMailing(){
	
if($("#sameasmailing").prop("checked") == true){
	var mailingStreetVal=$('#mailingStreet').val();
	var mailingStreet2=$('#mailingStreet2').val();
	var mailingStreet4=$('#mailingStreet4').val();
	var mailingCity1=$('#mailingCity1').val();
	var mailingZipCd1=$('#mailingZipCd1').val();
	var mailingCountry1=$('#mailingCountry1').val();
	var mailing_State1=$('#mailing_State1').val();
	
	($('#mailingStreet1').val(mailingStreetVal));
	($('#mailingStreet3').val(mailingStreet2));
	($('#mailingStreet5').val(mailingStreet4));
	($('#mailingCity2').val(mailingCity1));
	($('#mailingZipCd2').val(mailingZipCd1));
	($('#mailingCountry2').val(mailingCountry1));
	($('#mailing_State2').val(mailing_State1)); 
	globalmailing_State2=mailing_State1;
	document.getElementById("mailingStreet1").disabled = true;
	document.getElementById("mailingStreet3").disabled = true;

	document.getElementById("mailingStreet5").disabled = true;

	document.getElementById("mailingCity2").disabled = true;

	document.getElementById("mailingZipCd2").disabled = true;

	document.getElementById("mailingCountry2").disabled = true;

	document.getElementById("mailing_State2").disabled = true;
	selectShippingCountry();
	}
	else{
		
		document.getElementById("mailingStreet1").disabled = false;
		document.getElementById("mailingStreet3").disabled = false;

		document.getElementById("mailingStreet5").disabled = false;

		document.getElementById("mailingCity2").disabled = false;

		document.getElementById("mailingZipCd2").disabled = false;

		document.getElementById("mailingCountry2").disabled = false;

		document.getElementById("mailing_State2").disabled = false; 

	}


}

function clearSameAsMailing(){
	
	$('#sameasmailing').attr('checked', false);
	document.getElementById("mailingStreet1").disabled = false;
	document.getElementById("mailingStreet3").disabled = false;

	document.getElementById("mailingStreet5").disabled = false;

	document.getElementById("mailingCity2").disabled = false;

	document.getElementById("mailingZipCd2").disabled = false;

	document.getElementById("mailingCountry2").disabled = false;

	document.getElementById("mailing_State2").disabled = false; // Unchecks it
	
}


/*function generateLocationExcelReport(frm)
{

	var action = "EXCEL_DOWNLOAD";
	
	$("#action").val('EXCEL_DOWNLOAD');
	$("#ACTION").val('EXCEL_DOWNLOAD');
	
	
	document.forms[0].target="_blank";
	document.forms[0].submit();
	
}
*/

function selectMailingCountryForReset(){

	var parameters=null;
	var action = "SELECTMAILINGCOUNTRY";
	var addReset = "addreset";
	parameters = "ACTION=" + action;
	var state="";
	parameters += '&mailingCountry1='+ 'US';
	fetch_MailingCountryDetails(parameters, action,addReset,state);
	
	
}



function selectMailingCountry(){

	var parameters=null;
	var action = "SELECTMAILINGCOUNTRY";
	parameters = "ACTION=" + action;
	var countryDrop = "countryDrop";
	var state="";
	parameters += '&mailingCountry1='+ $("#mailingCountry1").val();
	fetch_MailingCountryDetails(parameters, action,countryDrop,state);
	
	
}

function selectMailingCountryforUpdateRst(state){

	var parameters=null;
	var action = "SELECTMAILINGCOUNTRY";
	parameters = "ACTION=" + action;
	var updateReset = "updatereset";
	parameters += '&mailingCountry1='+ $("#mailingCountry1").val();
	fetch_MailingCountryDetails(parameters, action,updateReset,state);
	
	
}



function fetch_MailingCountryDetails(parameters, action,resetValue,state){
	
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  $("#message").html("");
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	   
				dataList = response.stateNameList;
				$("#mailing_State1 option[value!='']").remove(); 
				if(resetValue=="addreset"){$("#mailing_State1 option[value!='']").remove(); }
				//var state=$("#mailing_State1").val();
				$.each(dataList, function() {
					var objModel = this;
					var option = $('<option></option>').attr( {
						value : objModel.value
					}).text(objModel.label);
					$("#mailing_State1").append(option);
					
				}); 
				
				
				if(resetValue=="updatereset"){$("#mailing_State1").val(state); }
				if(dataList == "undefined" ||dataList==0){
					document.getElementById("mailing_State1").style.backgroundColor = "";
					$("#mailing_State1 option[value!='']").remove();
				}else{
					document.getElementById("mailing_State1").style.backgroundColor = "#FAFFA8";
					
				};
				
				
				
				$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "SELECTMAILINGCOUNTRY" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "SELECTMAILINGCOUNTRY" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}



function selectShippingCountry(){
	
	var parameters=null;
	var action = "SELECTSHIPPINGCOUNTRY";
	parameters = "ACTION=" + action;
	var addReseet = "addreset";
	var state="";
	parameters += '&mailingCountry2='+ $("#mailingCountry2").val();
	
	
	fetch_ShippingCountryDetails(parameters, action,addReseet,state);
	var shippingCountry=$("#mailingCountry2 option:selected").text();
	
}

function selectShippingCountryUpdateRst(state){
	
	var parameters=null;
	var action = "SELECTSHIPPINGCOUNTRY";
	parameters = "ACTION=" + action;
	var updateReset = "updatereset";
	parameters += '&mailingCountry2='+ $("#mailingCountry2").val();
	fetch_ShippingCountryDetails(parameters, action,updateReset,state);
	
	
}

function fetch_ShippingCountryDetails(parameters, action,resetValue,state){
	
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
		  
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  $("#message").html("");
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	   
				dataList = response.stateNameList;
				//var state=$("#mailing_State1").val();
				$("#mailing_State2 option[value!='']").remove(); 
				
				$.each(dataList, function() {
					var objModel = this;
					var option = $('<option></option>').attr( {
						value : objModel.value
					}).text(objModel.label);
					$("#mailing_State2").append(option);
				}); 
				
				if(globalmailing_State2!="-1"){
					$("#mailing_State2").val(globalmailing_State2);
				}
				
				if(resetValue=="updatereset"){$("#mailing_State2").val(state); }
				$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "SELECTSHIPPINGCOUNTRY" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "SELECTSHIPPINGCOUNTRY" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}


function selectCountry(){
	
	var parameters=null;
	var action = "SELECTCOUNTRY";
	parameters = "ACTION=" + action;
	
	parameters += '&input_country='+ $("#input_country").val();
	fetch_CountryDetails(parameters, action);
	
	
}

function fetch_CountryDetails(parameters, action){

	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
			
        	  $("#message").html("");
              $("#message").html("Loading.....");
           },
          success: function(response){
        	   
        	    $("#message").html("");
				dataList = response.regionCodeList;
				$("#input_region option[value!='']").remove(); 
				
				$.each(dataList, function() {
					var objModel = this;
					var option = $('<option></option>').attr( {
						value : objModel.value
					}).text(objModel.label);
					$("#input_region").append(option);
				}); 
				
				
				$("#input_State option[value!='']").remove(); 
				dataList = response.stateNameList;
				$.each(dataList, function() {
					var objModel = this;
					var option = $('<option></option>').attr( {
						value : objModel.value
					}).text(objModel.label);
					$("#input_State").append(option);
				}); 
				
				
				
				$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "SELECTCOUNTRY" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "SELECTCOUNTRY" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}

function actionCheck(){
	
	var actionCheck=$("#Save").val();
	var parameters=null;
	//var selectedText=null;
	selectedCountry=$("#mailingCountry1 option:selected").text();
	shippingCountry=$("#mailingCountry2 option:selected").text();
	if(actionCheck=='SAVE'){
		
		
		var action = "SAVE";
		parameters = "ACTION=" + action;
		
		parameters += '&locationsetupName='+ $("#locationsetupName").val(); 
		parameters += '&locationsetupfirstName='+ $("#locationsetupfirstName").val();
		parameters += '&locationsetupCode='+ $("#locationsetupCode").val();
		parameters += '&locationsetuplastName='+ $("#locationsetuplastName").val();
		parameters += '&input_locationsetup_Statuscode='+ $("#input_locationsetup_Statuscode").val();
		parameters += '&locationsetupTitle='+ $("#locationsetupTitle").val();
		parameters += '&locationsetupEmail='+ $("#locationsetupEmail").val();
		parameters += '&locationsetupPhone1='+ $("#locationsetupPhone1").val();
		parameters += '&locationsetupPhone2='+ $("#locationsetupPhone2").val();
		parameters += '&locationsetupPhone3='+ $("#locationsetupPhone3").val();
		parameters += '&locationsetupPhone4='+ $("#locationsetupPhone4").val();
		parameters += '&input_locationsetup_Type1='+ $("#input_locationsetup_Type1").val();
		parameters += '&locationsetupfaxAreaCode1='+ $("#locationsetupfaxAreaCode1").val();
		parameters += '&locationsetupfaxAreaCode2='+ $("#locationsetupfaxAreaCode2").val();
		parameters += '&locationsetupfaxAreaCode3='+ $("#locationsetupfaxAreaCode3").val();
		parameters += '&input_locationsetup_Type2='+ $("#input_locationsetup_Type2").val();
		parameters += '&locationsetupcellAreaCode1='+ $("#locationsetupcellAreaCode1").val();
		parameters += '&locationsetupcellAreaCode2='+ $("#locationsetupcellAreaCode2").val();
		parameters += '&locationsetupcellAreaCode3='+ $("#locationsetupcellAreaCode3").val();
		parameters += '&input_locationsetup_Type3='+ $("#input_locationsetup_Type3").val();
		parameters += '&input_locationsetupRegion='+ $("#input_locationsetupRegion").val();
		
		parameters += '&mailingStreet='+ $("#mailingStreet").val(); 
		parameters += '&mailingStreet1='+ $("#mailingStreet1").val();
		parameters += '&mailingStreet2='+ $("#mailingStreet2").val();
		parameters += '&mailingStreet3='+ $("#mailingStreet3").val();
		parameters += '&mailingStreet4='+ $("#mailingStreet4").val();
		parameters += '&mailingStreet5='+ $("#mailingStreet5").val();
		parameters += '&mailingCity1='+ $("#mailingCity1").val();
		parameters += '&mailingCity2='+ $("#mailingCity2").val();
		parameters += '&mailing_State1='+ $("#mailing_State1").val();
		parameters += '&mailing_State2='+ $("#mailing_State2").val();
		parameters += '&mailingZipCd1='+ $("#mailingZipCd1").val();
		parameters += '&mailingZipCd2='+ $("#mailingZipCd2").val();
		parameters += '&mailingCountry1='+ $("#mailingCountry1").val();
		parameters += '&mailingCountry2='+ $("#mailingCountry2").val();
		parameters += '&locStatusDate='+ $("#locStatusDate").val();
		parameters += '&currentDate='+ $("#currentDate").val();
		parameters += '&districtCode='+ $("#districtCode").val();
		parameters += '&selectedCountry='+selectedCountry;
		parameters += '&shippingCountry='+shippingCountry;
		
		
		if((!checkLocationNameCode()==false) && (!locationTypeSelect()==false) 
				&& (!locationTypeComboValidation()==false)&& (!checkMailingCityZipCode()==false) &&
				(!validateMailingCountry()==false) && (!checkMailingState()==false) && (!checkEmail()==false) && (!numericCheck()==false) ){

			
			var selectedValue1 = $("#input_locationsetup_Type1").val();
			var selectedValue2 = $("#input_locationsetup_Type2").val();
			var selectedValue3 = $("#input_locationsetup_Type3").val();
			
		/*	if((selectedValue1=="DD") || (selectedValue1=="DP") || (selectedValue1=="OT") || (selectedValue1=="PT") || (selectedValue1=="GD") || (selectedValue1=="VS") || (selectedValue1=='DL') || (selectedValue1=='F0') ||
					(selectedValue1=="RH") || (selectedValue1=="RI") || (selectedValue1=="TC") || selectedValue1 == null || trimStringSpaces(selectedValue1) == ""){
				
				if((selectedValue2=="DD") || (selectedValue2=="DP") || (selectedValue2=="OT") || (selectedValue2=="PT") || (selectedValue2=="GD") || (selectedValue2=="VS") || (selectedValue2=='DL') || (selectedValue2=='F0') ||
						(selectedValue2=="RH") || (selectedValue2=="RI") || (selectedValue2=="TC") || selectedValue2 == null || trimStringSpaces(selectedValue2) == ""){
				

					if((selectedValue3=="DD") || (selectedValue3=="DP") || (selectedValue3=="OT") || (selectedValue3=="PT") || (selectedValue3=="GD") || (selectedValue3=="VS") || (selectedValue3=='DL') || (selectedValue3=='F0') ||
								(selectedValue3=="RH") || (selectedValue3=="RI") || (selectedValue3=="TC") || selectedValue3 == null || trimStringSpaces(selectedValue3) == ""){ */
			if((selectedValue1=="CA") || (selectedValue1=="DP") || (selectedValue1=="OT") || (selectedValue1=="PT") || (selectedValue1=="GD") || (selectedValue1=="VS") || (selectedValue1=="RH") || (selectedValue1=="RI") || (selectedValue1=="TC") || selectedValue1 == null || trimStringSpaces(selectedValue1) == ""){
 			   if((selectedValue2=="CA") || (selectedValue2=="DP") || (selectedValue2=="OT") || (selectedValue2=="PT") || (selectedValue2=="GD") || (selectedValue2=="VS") || (selectedValue2=="RH") || (selectedValue2=="RI") || (selectedValue2=="TC") || selectedValue2 == null || trimStringSpaces(selectedValue2) == ""){
				  if((selectedValue3=="CA") || (selectedValue3=="DP") || (selectedValue3=="OT") || (selectedValue3=="PT") || (selectedValue3=="GD") || (selectedValue3=="VS") || (selectedValue3=="RH") || (selectedValue3=="RI") || (selectedValue3=="TC") || selectedValue3 == null || trimStringSpaces(selectedValue3) == ""){		
						if(confirm("Do you want to add a new Location?")){
							
							fetch_Save(parameters, action);	
						}
					}else{
						
						alert("Location Type 3 selected is not allowed to be inserted"); 
						return false;
					}
				}else{
					
					alert("Location Type 2 selected is not allowed to be inserted"); 
					return false;
				}
			}else{
				
				alert("Location Type 1 selected is not allowed to be inserted"); 
				return false;
			}
		
		}
		
	}else{
		var action = "UPDATE";
		parameters = "ACTION=" + action;
		
		parameters += '&locationsetupName='+ $("#locationsetupName").val(); 
		parameters += '&locationsetupfirstName='+ $("#locationsetupfirstName").val();
		parameters += '&locationsetupCode='+ $("#locationsetupCode").val();
		parameters += '&locationsetuplastName='+ $("#locationsetuplastName").val();
		parameters += '&input_locationsetup_Statuscode='+ $("#input_locationsetup_Statuscode").val();
		parameters += '&locationsetupTitle='+ $("#locationsetupTitle").val();
		parameters += '&locationsetupEmail='+ $("#locationsetupEmail").val();
		parameters += '&locationsetupPhone1='+ $("#locationsetupPhone1").val();
		parameters += '&locationsetupPhone2='+ $("#locationsetupPhone2").val();
		parameters += '&locationsetupPhone3='+ $("#locationsetupPhone3").val();
		parameters += '&locationsetupPhone4='+ $("#locationsetupPhone4").val();
		parameters += '&input_locationsetup_Type1='+ $("#input_locationsetup_Type1").val();
		parameters += '&locationsetupfaxAreaCode1='+ $("#locationsetupfaxAreaCode1").val();
		parameters += '&locationsetupfaxAreaCode2='+ $("#locationsetupfaxAreaCode2").val();
		parameters += '&locationsetupfaxAreaCode3='+ $("#locationsetupfaxAreaCode3").val();
		parameters += '&input_locationsetup_Type2='+ $("#input_locationsetup_Type2").val();
		parameters += '&locationsetupcellAreaCode1='+ $("#locationsetupcellAreaCode1").val();
		parameters += '&locationsetupcellAreaCode2='+ $("#locationsetupcellAreaCode2").val();
		parameters += '&locationsetupcellAreaCode3='+ $("#locationsetupcellAreaCode3").val();
		parameters += '&input_locationsetup_Type3='+ $("#input_locationsetup_Type3").val();
		parameters += '&input_locationsetupRegion='+ $("#input_locationsetupRegion").val();
		
		parameters += '&mailingStreet='+ $("#mailingStreet").val(); 
		parameters += '&mailingStreet1='+ $("#mailingStreet1").val();
		parameters += '&mailingStreet2='+ $("#mailingStreet2").val();
		parameters += '&mailingStreet3='+ $("#mailingStreet3").val();
		parameters += '&mailingStreet4='+ $("#mailingStreet4").val();
		parameters += '&mailingStreet5='+ $("#mailingStreet5").val();
		parameters += '&mailingCity1='+ $("#mailingCity1").val();
		parameters += '&mailingCity2='+ $("#mailingCity2").val();
		parameters += '&mailing_State1='+ $("#mailing_State1").val();
		parameters += '&mailing_State2='+ $("#mailing_State2").val();
		parameters += '&mailingZipCd1='+ $("#mailingZipCd1").val();
		parameters += '&mailingZipCd2='+ $("#mailingZipCd2").val();
		parameters += '&mailingCountry1='+ $("#mailingCountry1").val();
		parameters += '&mailingCountry2='+ $("#mailingCountry2").val();
		parameters += '&locStatusDate='+ $("#locStatusDate").val();
		
		parameters += '&districtCode='+ $("#districtCode").val();
		parameters += '&selectedCountry='+selectedCountry;
		parameters += '&shippingCountry='+shippingCountry;
		
		if((!checkLocationNameCode()==false) && (!locationTypeSelect()==false) 
				&& (!locationTypeComboValidation()==false)&& (!checkMailingCityZipCode()==false) &&
				(!validateMailingCountry()==false) && (!checkMailingState()==false) && (!checkEmail()==false) && (!numericCheck()==false)){
			
			var selectedValue1 = $("#old_input_locationsetup_Type1").val();
			var selectedValue2 = $("#old_input_locationsetup_Type2").val();
			var selectedValue3 = $("#old_input_locationsetup_Type3").val();
			
			var newValue1 = $("#input_locationsetup_Type1").val();
			var newValue2 = $("#input_locationsetup_Type2").val();
			var newValue3 = $("#input_locationsetup_Type3").val();
			
			
			
			if(checkLocationType(selectedValue1,'1') && checkLocationType(selectedValue2,'2') && checkLocationType(selectedValue3,'3') ){
				if(checkLocationType(newValue1,'1') && checkLocationType(newValue2,'2') && checkLocationType(newValue3,'3') ){
					if(confirm("Do you want to update a new Location?")){
					
							fetch_Update(parameters, action);
						
							
					}
				}else{
					return false;
				}
				
			}else{
				return false;
			}
			
			
			
			
			/*if((selectedValue1=="DD") || (selectedValue1=="DP") || (selectedValue1=="OT") || (selectedValue1=="PT") || (selectedValue1=="GD") || (selectedValue1=="VS") || (selectedValue1=='DL') || (selectedValue1=='F0') ||
					(selectedValue1=="RH") || (selectedValue1=="RI") || (selectedValue1=="TC") || selectedValue1 == null || trimStringSpaces(selectedValue1) == ""){
				
				if((selectedValue2=="DD") || (selectedValue2=="DP") || (selectedValue2=="OT") || (selectedValue2=="PT") || (selectedValue2=="GD") || (selectedValue2=="VS") || (selectedValue2=='DL') || (selectedValue2=='F0') ||
						(selectedValue2=="RH") || (selectedValue2=="RI") || (selectedValue2=="TC") || selectedValue2 == null || trimStringSpaces(selectedValue2) == ""){
				

					if((selectedValue3=="DD") || (selectedValue3=="DP") || (selectedValue3=="OT") || (selectedValue3=="PT") || (selectedValue3=="GD") || (selectedValue3=="VS") || (selectedValue3=='DL') || (selectedValue3=='F0') ||
								(selectedValue3=="RH") || (selectedValue3=="RI") || (selectedValue3=="TC") || selectedValue3 == null || trimStringSpaces(selectedValue3) == ""){
						
						if(confirm("Do you want to update a new Location?")){
							fetch_Update(parameters, action);	
						}
							
					}else{
						
						alert("Location Type 3 selected is not allowed to be Updated"); 
						return false;
					}
				}else{
					
					alert("Location Type 2 selected is not allowed to be Updated"); 
					return false;
				}
			}else{
				
				alert("Location Type 1 selected is not allowed to be Updated"); 
				return false;
			}*/
			
		}
		
	}
		
}

function checkLocationType(locationType,locationType1)
{
	/*if((locationType=="DD") || (locationType=="DP") || (locationType=="OT") || (locationType=="PT") || (locationType=="GD") || (locationType=="VS") || (locationType=='DL') || (locationType=='F0') ||
			(locationType=="RH") || (locationType=="RI") || (locationType=="TC") || locationType == null || trimStringSpaces(locationType) == ""){*/
	if((locationType=="CA") || (locationType=="DP") || (locationType=="OT") || (locationType=="PT") || (locationType=="GD") || (locationType=="VS") || (locationType=="RH") || (locationType=="RI") || (locationType=="TC") || locationType == null || trimStringSpaces(locationType) == ""){
	return true;
	}else {
		alert("Location Type "+locationType1+" selected is not allowed to be updated"); 
		return false;
	}
}
function checkLocationTypeDelete(locationType,locationType1)
{
	/*if((locationType=="DD") || (locationType=="DP") || (locationType=="OT") || (locationType=="PT") || (locationType=="GD") || (locationType=="VS") || (locationType=='DL') || (locationType=='F0') ||
			(locationType=="RH") || (locationType=="RI") || (locationType=="TC") || locationType == null || trimStringSpaces(locationType) == ""){*/
	if((locationType=="CA") || (locationType=="DP") || (locationType=="OT") || (locationType=="PT") || (locationType=="GD") || (locationType=="VS") || (locationType=="RH") || (locationType=="RI") || (locationType=="TC") || locationType == null || trimStringSpaces(locationType) == ""){
	return true;
	}else {
		alert("Location Type "+locationType1+" selected is not allowed to be deleted"); 
		return false;
	}
}


var existingLocStatusFlag;
var existingLocStatusDate;
function statusDateChange(checkedValue){
	
	if(checkedValue!=existingLocStatusFlag){
		$("#locStatusDate").val($("#currentDate").val());
	}else{
		$("#locStatusDate").val(existingLocStatusDate);
	}
}

function validateMailingCountry(){
	
	if($("#mailingCountry1")[0]. selectedIndex <= 0){
		alert("Select mailing country");
		return false;
	}	
	return true;
}


function checkMailingState(){
	
	var countryCode = $("#mailingCountry1").val();
	
	/*if(countryCode == 'US - UNITED STATES OF AMERICA' || countryCode == 'MX' || countryCode == 'CA'){
		
		var stateCode = $("#mailing_State1").val();	
		if(stateCode<=0)
		{
			$("#mailing_State1").focus();
			alert("Select mailing address state");
			return false;	
		}
	}*/
	var color = $('#mailing_State1').css("background-color");
	if($("#mailing_State1").val().length<=0 && color== "rgb(250, 255, 168)"){
		alert("Select mailing address state");
		$("#mailing_State1").focus();
		return false;
	}
	
	return true;
}

function checkLocationNameCode(){
	
	if($("#locationsetupName").val().length<=0){
		alert("Location name is empty");
		$("#locationsetupName").focus();
		return false;
	}
	if($("#locationsetupCode").val().length<=0){
		alert("Location code is empty");
		$("#locationsetupCode").focus();
		return false;
	}
	return true;
}



function locationTypeSelect(){
	
	if (($("#input_locationsetup_Type1")[0]. selectedIndex <= 0) && ($("#input_locationsetup_Type2")[0]. selectedIndex <= 0) && ($("#input_locationsetup_Type3")[0]. selectedIndex <= 0)) {
		alert("Select at least one location type");
		$("#input_locationsetup_Type1").focus();
		return false;
}	
	return true;
}

function checkMailingCityZipCode(){
	
	if($("#mailingCity1").val().length<=0){
		alert("Mailing address city is empty");
		$("#mailingCity1").focus();
		return false;
	}
	return true;
}

function locationTypeComboValidation(){
	
	if(($("#input_locationsetup_Type1")[0]. selectedIndex > 0) && ($("#input_locationsetup_Type2")[0]. selectedIndex > 0)||
	  ($("#input_locationsetup_Type1")[0]. selectedIndex > 0) &&($("#input_locationsetup_Type3")[0]. selectedIndex > 0)||
	  ($("#input_locationsetup_Type2")[0]. selectedIndex > 0) &&($("#input_locationsetup_Type3")[0]. selectedIndex > 0))
	  {
		
		var selectedValue1 = $("#input_locationsetup_Type1").val();
		var selectedValue2 = $("#input_locationsetup_Type2").val();
		var selectedValue3 = $("#input_locationsetup_Type3").val();
		
		
		if(selectedValue1==selectedValue2 || selectedValue1==selectedValue3 || selectedValue2==selectedValue3){
			alert("Please select different location type");
			return false;
		}	
		return true;
	}
	return true;
}



function fetch_Save(parameters, action){
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
    $('#actionCode').val("SAVE");
    var formData = $('#locForm').serialize();
    selectedCountry=$("#mailingCountry1 option:selected").text();
	shippingCountry=$("#mailingCountry2 option:selected").text();
	formData += '&selectedCountry='+selectedCountry;
	formData += '&shippingCountry='+shippingCountry;
	formData += '&mailingStreet1='+ $("#mailingStreet1").val();
	formData += '&mailingStreet3='+ $("#mailingStreet3").val();
	formData += '&mailingStreet5='+ $("#mailingStreet5").val();
	formData += '&mailingCity2='+ $("#mailingCity2").val();
	formData += '&mailingZipCd2='+ $("#mailingZipCd2").val();
	formData += '&mailing_State2='+ $("#mailing_State2").val();
	formData += '&mailingCountry2='+ $("#mailingCountry2").val();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data:formData,
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  $("#message").html("");
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	  orgResponseCode="";
        	    orgResponseCode = response.responseText;
        	    
        	    $("#message1").html("");
        	    $("#message").html("");
				$("#locationTable").hide();
				$("#message1").show();
				$("#locationMailingInformation").hide();
				if(orgResponseCode.match("already")){
					
					 $("#message1").show();
					 $("#locationTable").show();
					 $("#locationMailingInformation").show();
					 $("#message1").html(" Location code already exists - Please inquire first");
					 $(window).scrollTop($('#message1').offset().top);
					 resetOnAddUpdate();
				}else{
					$("#message1").show();
					$("#locationTable").show();
				    $("#locationMailingInformation").show();
					$("#message1").html("Location details "+orgResponseCode);
					$(window).scrollTop($('#message1').offset().top);
					resetOnAddUpdate();
					senderGlobal=0;
					setValue2();
				}
        		$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "SAVE" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "SAVE" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}


function fetch_Update(parameters, action){

	var dt = new Date();
    var inMilliSeconds = dt.getTime();
    $('#actionCode').val("UPDATE");
    var formData = $('#locForm').serialize();
    selectedCountry=$("#mailingCountry1 option:selected").text();
	shippingCountry=$("#mailingCountry2 option:selected").text();
	formData += '&selectedCountry='+selectedCountry;
	formData += '&shippingCountry='+shippingCountry;
	formData += '&mailingStreet1='+ $("#mailingStreet1").val();
	formData += '&mailingStreet3='+ $("#mailingStreet3").val();
	formData += '&mailingStreet5='+ $("#mailingStreet5").val();
	formData += '&mailingCity2='+ $("#mailingCity2").val();
	formData += '&mailingZipCd2='+ $("#mailingZipCd2").val();
	formData += '&mailing_State2='+ $("#mailing_State2").val();
	formData += '&mailingCountry2='+ $("#mailingCountry2").val();
	
	 
  
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
        data:formData,
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  $("#message").html("");
                    $("#message").html("Loading.....");
           },
          success: function(response){
        	  orgResponseCode="";
        	    orgResponseCode = response.responseText;	
        	    //$("#locationTable").hide();
        	    $("#locationTable").show();
        	    $("#message1").html("");
        	    $("#message").html("");
				$("#message1").show();
				//$("#locationMailingInformation").hide();
				$("#locationMailingInformation").show();
				if(orgResponseCode.match("already")){
					 $("#message1").show();
					 $("#locationTable").show();
					 $("#locationMailingInformation").show();
					 $("#message").html(" Location code already exists - Please inquire first");
					 $(window).scrollTop($('#message').offset().top);
					 resetOnAddUpdate();
				}else{
				$("#message1").show();
				$("#locationTable").show();
				$("#locationMailingInformation").show();
				$("#message1").html("Location details "+orgResponseCode);
				 $(window).scrollTop($('#message1').offset().top);
				resetOnAddUpdate();
				}
				
				$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "UPDATE" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "UPDATE" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}


function deleteLocationDetails(){
	
	var action = "DELETE";
	var parameters = "ACTION=" + action;
	parameters += '&locationsetupCode='+ $("#locationsetupCode").val();
	
	if((!checkLocationNameCode()==false) && (!locationTypeSelect()==false) 
			&& (!locationTypeComboValidation()==false)&& (!checkMailingCityZipCode()==false) &&
			(!validateMailingCountry()==false) && (!checkMailingState()==false)){
		var selectedValue1 = $("#old_input_locationsetup_Type1").val();
		var selectedValue2 = $("#old_input_locationsetup_Type2").val();
		var selectedValue3 = $("#old_input_locationsetup_Type3").val();
		
		var newValue1 = $("#input_locationsetup_Type1").val();
		var newValue2 = $("#input_locationsetup_Type2").val();
		var newValue3 = $("#input_locationsetup_Type3").val();
		
		if(checkLocationTypeDelete(selectedValue1,'1') && checkLocationTypeDelete(selectedValue2,'2') && checkLocationTypeDelete(selectedValue3,'3') ){
			if(checkLocationTypeDelete(newValue1,'1') && checkLocationTypeDelete(newValue2,'2') && checkLocationTypeDelete(newValue3,'3') ){
				if(confirm("Do you want to delete a new Location?")){
					fetch_Delete(parameters, action);	
				}
			}else{
				return false;
			}
			
		}else{
			return false;
		}
		
		
	
	}
	
}


function fetch_Delete(parameters, action){
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  
                    $("#message").html("Loading.....");
                    $("#message").hide();
           },
          success: function(response){
        	   	
        	    $('#message').html("");
        	    orgResponseCode="";
        	    orgResponseCode = response.responseText;			
        	    
        	    $("#locationTable").hide();
				$("#locationMailingInformation").hide();
				$("#message1").show();
				$("#message1").html("Location code details "+orgResponseCode);
				resetOnAddUpdate();
				
        		$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "DELETE" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "DELETE" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}

function doReset(){
	
	$("#message1").hide();
	$("#locationsetupName").val('');
	$("#locationsetupfirstName").val('');
	$("#locationsetupCode").val('');
	$("#locationsetuplastName").val('');
	$("#locationsetupTitle").val('');
	$("#locationsetupEmail").val('');
	$("#locationsetupPhone1").val('');
	$("#locationsetupPhone2").val('');
	$("#locationsetupPhone3").val('');
	$("#locationsetupPhone4").val('');
	$("#input_locationsetup_Type1").val('');
	$("#locationsetupfaxAreaCode1").val('');
	$("#locationsetupfaxAreaCode2").val('');
	$("#locationsetupfaxAreaCode3").val('');
	$("#input_locationsetup_Type2").val('');
	$("#locationsetupcellAreaCode1").val('');
	$("#locationsetupcellAreaCode2").val('');
	$("#locationsetupcellAreaCode3").val('');
	$("#input_locationsetup_Type3").val('');
	$("#input_locationsetupRegion").val('');
	$("#mailingStreet").val('');
	$("#mailingStreet1").val('');
	$("#mailingStreet2").val('');
	$("#mailingStreet3").val('');
	$("#mailingStreet4").val('');
	$("#mailingStreet5").val('');
	$("#mailingCity1").val('');
	$("#mailingCity2").val('');
	$("#mailing_State1").val('');
	$("#mailing_State2").val('');
	$("#mailingZipCd1").val('');
	$("#mailingZipCd2").val('');
	$("#mailingCountry2").val('');

	
	
}

function dobackbuttonClick(){
	
		$("#locationTable").hide();
		$("#locationMailingInformation").hide();	
		$("#contentTable").show();
		$("#message1").hide();
		$("#message1").html("");
		//fnSelectRecord(0,false);
}

function donewbackbuttonClick(){
	
	document.getElementById("ResetUpdate").disabled = false;
	$('#sameasmailing').attr('checked', false);
	 $("#Back").hide();
	 $('#newBack').show();
	 $("#todaysDate").show();
	 $("#locStatusDate").hide();
	 $("#Delete").hide();
	 $("#contentTable").hide();
	 $("#message").hide();
	 $("#message1").hide();
	 $("#locationTable").show();
	 $("#locationMailingInformation").show();
	 $("#locationsetupName").val(''); 
	 $("#locationsetupCode").val('');
	 //$("#input_locationsetup_Statuscode").val('');
	 $("#input_locationsetup_Type1").val('');
	 $("#input_locationsetup_Type2").val('');
	 $("#input_locationsetup_Type3").val('');
	 $("#input_locationsetupRegion").val('');
	 $("#locationsetupPhone1").val('');
	 $("#locationsetupPhone2").val('');
	 $("#locationsetupPhone3").val('');
	 $("#mailingStreet").val('');
	 $("#mailingCity1").val(''); 
	 $("#mailing_State1").val('');  
	 $("#mailingZipCd1").val(''); 
	 $("#mailingCountry1").val('');
	 $("#Save").val('SAVE');
	 $("#lastUpdatedBy").hide();
	 $("#lastUpdatedTime").hide();
	 $("#updatedlastUpdatedTime").hide();
	 $("#updatedlastUpdatedBy").hide();
	 
	 $("#locationsetupfirstName").val(''); 
	 $("#locationsetuplastName").val('');  
	 $("#locationsetupEmail").val('');
	 $("#locationsetupPhone1").val('');
	 $("#locationsetupPhone2").val('');
	 $("#locationsetupPhone3").val('');
	 $("#locationsetupPhone4").val('');
	 $("#locationsetupfaxAreaCode1").val('');
	 $("#locationsetupfaxAreaCode2").val('');
	 $("#locationsetupfaxAreaCode3").val('');
	 $("#locationsetupcellAreaCode1").val('');
	 $("#locationsetupcellAreaCode2").val('');
	 $("#locationsetupcellAreaCode3").val(''); 
	 
	
	 $("#mailingStreet").val(''); 
	 $("#mailingStreet2").val(''); 
	 $("#mailingStreet4").val(''); 
	 $("#mailingStreet1").val(''); 
	 $("#mailingStreet3").val(''); 
	 $("#mailingStreet5").val(''); 
	 $("#mailingCity2").val(''); 
	 $("#locationsetupTitle").val(''); 
	 $("#mailingZipCd1").val('');
	 $("#mailingZipCd2").val('');
	 $("#mailingCountry2").val('');
	 $("#mailing_State1").val('');
	// $("#mailingCountry1").val('');
	 $("#mailing_State2").val('');				
	 $("#input_locationsetup_Statuscode option[value='A']").attr("selected", "selected");
	 $("#mailingCountry1 option[value='US']").attr("selected", "selected");
	
	$("#locationTable").hide();
	$("#locationMailingInformation").hide();	
	$("#contentTable").hide();	
	
	//selectShippingCountry();
}


function doSearch(){
if(resetUpdateNew==false){
$("#message1").hide();
$("#contentTable").hide();
$("#assignBtn").hide();
$("#downloadBtn").hide();
$("#locationTable").hide();
$("#locationMailingInformation").hide();
}

if(!numericCheck()==false){
populate();	
}
}


function populate(){
	
	var action = "SEARCH";
	var parameters = "ACTION=" + action;
	
	parameters += '&locationName='+ $("#locationName").val(); 
	parameters += '&locationCode='+ $("#locationCode").val();
	parameters += '&input_country='+ $("#input_country").val();
	parameters += '&input_region='+ $("#input_region").val();
	parameters += '&input_State='+ $("#input_State").val();
	parameters += '&location_zipCode='+ $("#location_zipCode").val();
	parameters += '&input_City='+ $("#input_City").val();
	parameters += '&input_statusCode='+ $("#input_statusCode").val();
	parameters += '&input_Type='+ $("#input_Type").val();
	
	
	fetch_data(parameters, action);
}


function fetch_data(parameters, action){
	
	var dt = new Date();
    var inMilliSeconds = dt.getTime();
	$.ajax({
          type: "POST",
          url: "locationSearch.do?timeStamp=" + inMilliSeconds,
          data: parameters,
          datatype: 'json',
          async: true,
          beforeSend: function(x) {
			if(resetUpdateNew==false){
				$("#message1").hide();
			}
        	  $("#message").html("");
                    $("#message").html("Loading.....");
                    $("#message").show();
           },
          success: function(response){
 
				dataList = response.searchList;
				$("#contentTable").show();
				createDataTable(response);
        		return false;
        		
        		$("#chkActionAll").attr("checked",false);
        		bOpenRow=false;
        		
        		$(document).unbind("keyup");
        		$(document).keyup(function (e) {
        			if (e.keyCode == 13) {
        				//doSearch();
        			}
        		});
          	
          	if(action != "SEARCH" || response.responseCode == 100){
	        	  alert(response.response);
	      	}
          	if(action == "SEARCH" && response.responseCode ==1){
	        	  alert(response.response);
	      	}
          	
          	if(response.responseCode == -1){
          		//$('#message').html(response.response);
          	}
		    return true;
          },
          error: function(xhr, ajaxOptions, thrownError){
          		alert("error code:"+xhr.status);
           }
           
      });
}


function getaddressField(datarow){
	
	var locName;
	var shipAddr;
	var shipAddr2;
	var shipAddr3;
	var shipCity;
	var shiStateCd;
	var shiStateCd;
	var shipZipCD;
	var phoneAcNo;
	var phoneExcNo
	var phoneNo;
	if(datarow.addressTypeNm=='SHIPPING'){
		
		if(datarow.locationName.length>0){
			locName=datarow.locationName+','+'<br>';
		}else{
			locName='';
		}if(datarow.shippingstreetaddress1.length>0){
			shipAddr=datarow.shippingstreetaddress1+''+',';
		}else{
			shipAddr='';
		}if(datarow.shippingstreetaddress2.length>0){
			shipAddr2=datarow.shippingstreetaddress2+', ';	
		}else{
			shipAddr2='';
		}if(datarow.shippingstreetaddress3.length>0){
		shipAddr3=datarow.shippingstreetaddress3+','+'<br> ';
		}else{
			shipAddr3='';
		}if(datarow.shippingcityname.length>0){
			shipCity=datarow.shippingcityname+',';
		}else{
			shipCity='';
		}if(datarow.shippingstatecode.length>0){
			shiStateCd=datarow.shippingstatecode+' ';
		}else{
			shiStateCd='';
		}if(datarow.shippingzipcode.length>0){
			shipZipCD=datarow.shippingzipcode+'<br> '+' ';
		}else{
			shipZipCD='';
		}if(datarow.phoneAcNo.length>0){
			phoneAcNo='('+datarow.phoneAcNo+')'+' ';
		}else{
			phoneAcNo='';
		}if(datarow.phoneExcNo.length>0){
			phoneExcNo=datarow.phoneExcNo;
		}else{
			phoneExcNo='';
		}if(datarow.phoneNo.length>0){
			phoneNo='-'+datarow.phoneNo;
		}else{
			phoneNo='';
		}
		
		return locName+shipAddr+shipAddr2+shipAddr3+shipCity+shiStateCd+shipZipCD+phoneAcNo+phoneExcNo+phoneNo;
		
	}else{
		
		if(datarow.locationName.length>0){
			locName=datarow.locationName+','+'<br>';
		}else{
			locName='';
		}if(datarow.streetAddress1.length>0){
			shipAddr=datarow.streetAddress1+''+',';
		}else{
			shipAddr='';
		}if(datarow.streetAddress2.length>0){
			shipAddr2=datarow.streetAddress2+', ';	
		}else{
			shipAddr2='';
		}if(datarow.streetAddress3.length>0){
		shipAddr3=datarow.streetAddress3+','+'<br> ';
		}else{
			shipAddr3='';
		}if(datarow.cityName.length>0){
			shipCity=datarow.cityName+',';
		}else{
			shipCity='';
		}if(datarow.stateCode.length>0){
			shiStateCd=datarow.stateCode+' ';
		}else{
			shiStateCd='';
		}if(datarow.zipCode.length>0){
			shipZipCD=datarow.zipCode+'<br> '+' ';
		}else{
			shipZipCD='';
		}if(datarow.phoneAcNo.length>0){
			phoneAcNo='('+datarow.phoneAcNo+')'+' ';
		}else{
			phoneAcNo='';
		}if(datarow.phoneExcNo.length>0){
			phoneExcNo=datarow.phoneExcNo;
		}else{
			phoneExcNo='';
		}if(datarow.phoneNo.length>0){
			phoneNo='-'+datarow.phoneNo;
		}else{
			phoneNo='';
		}
		
		return locName+shipAddr+shipAddr2+shipAddr3+shipCity+shiStateCd+shipZipCD+phoneAcNo+phoneExcNo+phoneNo;
	}
	
	
	
}

function getLocationTypeField(datarow){
	
	var locTypeName='';
	var dataavaliable=false;
	if(datarow.cdtvalueTx.length>0){
		dataavaliable=true;
		locTypeName=datarow.cdtvalueTx;
	}if(datarow.cdtvalueTx2.length>0){
		
		if(dataavaliable==true){
			locTypeName+=',';
		}
		dataavaliable=true;
		locTypeName+=datarow.cdtvalueTx2;
	}if(datarow.cdtvalueTx3.length>0){
		if(dataavaliable==true){
			locTypeName+=',';
		}
		locTypeName+=datarow.cdtvalueTx3;
	}
	
	return locTypeName;
}

function createDataTable (response) {

	//fnSelectRecord(0,false);
	var displayStart = 0;
    var displayLength = 10;
    $("#message").hide();
    var dataArr = new Array();
   
    for(var icount=0; icount<response.searchList.length; icount++){
		var datarow = response.searchList[icount];
		
		var actionRadio = '';
  		
  		//actionRadio = '<input class="change" type="checkbox"  onclick="fnSelectRecord(this);checkUncheckBox();" name="group1" action-cd="EDIT" />';
  		
	
		
		//actionRadio = '<input class="change" type="checkbox"  onclick="fnSelectRecord('+icount+','+true+');checkUncheckBox();" name="group1" action-cd="EDIT" />';
			var locTypeValue=getLocationTypeField(datarow);
  			var addressfeld=getaddressField(datarow);
		dataArr[icount] = new Array(
				//actionRadio,
				'<a href="javascript:void(0);" onclick="fnSelectRecord('+icount+','+true+')" title="'+datarow.currentLocationCode+'" >'+datarow.currentLocationCode+'</a>',
				addressfeld,
				datarow.addressTypeNm,
				datarow.statusDesc,
				locTypeValue,
				datarow.regionCd,
				datarow.locationName,
				datarow.streetAddress1,
				datarow.cityName,
				datarow.stateCode,
				datarow.zipCode,
				datarow.countryCd,
				datarow.phoneAcNo,
				datarow.phoneExcNo,
				datarow.phoneNo,
				datarow.currentLocationCode,
				datarow.lastUpdateTime,
				datarow.lastUserIdCd,
				datarow.statusDate,
				datarow.statusCdSearch,
				datarow.cdtvalueCd,
				datarow.firstName,
				datarow.lastName,
				datarow.contactTitle,
				datarow.shippingstreetaddress1,
				datarow.shippingstreetaddress2,
				datarow.shippingstreetaddress3,
				datarow.shippingcityname,
				datarow.shippingstatecode,
				datarow.shippingzipcode,
				datarow.shippingcountrycode,
				datarow.streetAddress2,
				datarow.streetAddress3,
				datarow.faxAcNo,
				datarow.faxExcNo,
				datarow.faxNo,
				datarow.districtCode,
				datarow.phoneExtnsnNo,
				datarow.emailId,
				datarow.cellNo1,
				datarow.cellNo2,
				datarow.cellNo3,
				datarow.cdtvalueTx2,
				datarow.cdtvalueCd2,
				datarow.cdtvalueTx3,
				datarow.cdtvalueCd3
				);
		
	}
    
    if(oTable!=null){
			displayStart = oTable.fnSettings()._iDisplayStart;
			displayLength = oTable.fnSettings()._iDisplayLength;
			//bSortingStatus = oTable.fnSettings().aaSorting;
			oTable.fnClearTable(this);
			oTable.fnDestroy();
			oTable=null;
		}
	

	oTable = $('#vehManAssgmnt').dataTable({
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
		    //{ "sWidth": "" },
		    { "sWidth": "10%" },
			{ "sWidth": "25%" }, 
			{ "sWidth": "15%" }, 
			{ "sWidth": "15%" }, 
			{ "sWidth": "15%" }, 
			{ "sWidth": "15%" }
		]
		
	  });	
	
	if(resetUpdateNew==true){
		fnSelectRecord(senderGlobal,true);
		$('#locationCode').val('');
		resetUpdateNew=false;
	} 
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

var senderGlobal='-1';
/*
function setValue(){
		var aData = oTable.fnGetData(senderGlobal);
		 
		 $('#ResetNew').hide();
		 $('#ResetUpdate').show();
		 $('#newBack').hide();
		 $("#Back").show();
		 $('#todaysDate').hide();
		 $("#contentTable").hide();
		 $("#locationTable").show();
		 $("#locationMailingInformation").show();
		 $("#Save").val('UPDATE');
		 $("#message1").hide();
		 $("#message").hide();
		 $("#Delete").show();
		 $("#locationsetupName").val(aData[7]); 
		 $("#locationsetupCode").val(aData[16]);
		 $("#input_locationsetup_Statuscode").val(aData[20]);
		 $("#input_locationsetup_Type1").val(aData[21]);
		 $("#input_locationsetupRegion").val(aData[6]);
		 $("#locationsetupPhone1").val(aData[13]);
		 $("#locationsetupPhone2").val(aData[14]);
		 $("#locationsetupPhone3").val(aData[15]);
		 
		 $("#mailingStreet2").val(aData[32]);
		 $("#mailingStreet4").val(aData[33]);
		 
		 
		 $("#locationsetupfaxAreaCode1").val(aData[34]);
		 $("#locationsetupfaxAreaCode2").val(aData[35]);
		 $("#locationsetupfaxAreaCode3").val(aData[36]);
		 
		 $("#mailingStreet").val(aData[8]);
		 $("#mailingCity1").val(aData[9]); 
		 $("#mailing_State1").val(aData[10]); 
		 $("#mailingZipCd1").val(aData[11]); 
		 $("#mailingCountry1").val(aData[12]);
		 $("#updatedlastUpdatedTime").show();
		 $("#updatedlastUpdatedBy").show();
		 $("#locStatusDate").show();
		 $("#lastUpdatedBy").show();
		 $("#lastUpdatedTime").show();
		 $("#locStatusDate").val(aData[19]);
		 $("#lastUpdatedBy").val(aData[18]);
		 $("#lastUpdatedTime").val(aData[17]);
		 $("#locationsetupfirstName").val(aData[22]);
		 $("#locationsetuplastName").val(aData[23]);
		 $("#locationsetupTitle").val(aData[24]);
		 $("#mailingStreet1").val(aData[25]); 
		 
		 $("#mailingStreet3").val(aData[26]);
		 $("#mailingStreet5").val(aData[27]);
		 
		 $("#mailingCity2").val(aData[28]);
		 $("#mailing_State2").val(aData[29]);
		 $("#mailingZipCd2").val(aData[30]);
		 $("#mailingCountry2").val(aData[31]);		
		 document.getElementById("locStatusDate").disabled = true;
		 document.getElementById("lastUpdatedBy").disabled = true;
		 document.getElementById("lastUpdatedTime").disabled = true;
}*/


function setValue(){
		var aData = oTable.fnGetData(senderGlobal);
		
		
		
		$("#input_locationsetup_Type1").val(aData[20]);
		$("#old_input_locationsetup_Type1").val(aData[20]);
		$("#input_locationsetup_Type2").val(aData[43]);
		$("#old_input_locationsetup_Type2").val(aData[43]);
		 $("#input_locationsetup_Type3").val(aData[45]);
		 $("#old_input_locationsetup_Type3").val(aData[45]);
		
		 $('#ResetNew').hide();
		 $('#ResetUpdate').show();
		 $('#newBack').hide();
		 $("#Back").show();
		 $('#todaysDate').hide();
		 $("#contentTable").hide();
		 $("#locationTable").show();
		 $("#locationMailingInformation").show();
		 $("#Save").val('UPDATE');
		
		 if(resetUpdateNew==false){
			$("#message1").hide();
		}
		 
		 $("#message").hide();
		 $("#Delete").show();
		 $("#locationsetupName").val(aData[6]); 
		 $("#locationsetupCode").val(aData[15]);
		 $("#locationLatestCode").val(aData[15]);
		 $("#locDate").val(aData[18]);
		 $("#latestUpdatedBy").val(aData[17]);
		 $("#input_locationsetup_Statuscode").val(aData[19]);
		 $("#input_locationsetupRegion").val(aData[5]);
		 $("#locationsetupPhone1").val(aData[12]);
		 $("#locationsetupPhone2").val(aData[13]);
		 $("#locationsetupPhone3").val(aData[14]);
		 $("#locationsetupPhone4").val(aData[37]);
		 $("#mailingStreet2").val(aData[31]);
		 $("#mailingStreet4").val(aData[32]);

		 $("#locationsetupfaxAreaCode1").val(aData[33]);
		 $("#locationsetupfaxAreaCode2").val(aData[34]);
		 $("#locationsetupfaxAreaCode3").val(aData[35]);
		 $("#districtCode").val(aData[36]);
		 $("#locationsetupEmail").val(aData[38]);
		 $("#locationsetupcellAreaCode1").val(aData[39]);
		 $("#locationsetupcellAreaCode2").val(aData[40]);
		 $("#locationsetupcellAreaCode3").val(aData[41]);
		 $("#mailingStreet").val(aData[7]);
		 $("#mailingCity1").val(aData[8]); 
		 //globalmailing_State2=aData[9];
		 $("#mailing_State1").val(aData[9]); 
		 $("#mailingZipCd1").val(aData[10]); 
		 $("#mailingCountry1").val(aData[11]);
		 $("#updatedlastUpdatedTime").show();
		 $("#updatedlastUpdatedBy").show();
		 $("#locStatusDate").show();
		 $("#lastUpdatedBy").show();
		 $("#lastUpdatedTime").show();
		 $("#locStatusDate").val(aData[18]);
		 existingLocStatusFlag=aData[19];
		 existingLocStatusDate=aData[18];
		 $("#lastUpdatedBy").val(aData[17]);
		 $("#lastUpdatedTime").val(aData[16]);
		 $("#locationsetupfirstName").val(aData[21]);
		 $("#locationsetuplastName").val(aData[22]);
		 $("#locationsetupTitle").val(aData[23]);
		 $("#mailingStreet1").val(aData[24]); 
		 
		 $("#mailingStreet3").val(aData[25]);
		 $("#mailingStreet5").val(aData[26]);
		 
		 $("#mailingCity2").val(aData[27]);
		 $("#mailing_State2").val(aData[28]);
		// addedjuly1
		 $("#shipstateName").val(aData[28]);
		 $("#mailingZipCd2").val(aData[29]);
		 $("#mailingCountry2").val(aData[30]);		
		 
		 document.getElementById("locationsetupCode").disabled = true;
		 document.getElementById("locStatusDate").disabled = true;
		 document.getElementById("lastUpdatedBy").disabled = true;
		 document.getElementById("lastUpdatedTime").disabled = true;
		 selectMailingCountryforUpdateRst(aData[9]);
		 selectShippingCountryUpdateRst(aData[28]);
		 sameAsMailing();
		 
		 //clearSameAsMailing();
		 clearsameAsMailingUpdate(aData);
}

function clearsameAsMailingUpdate(aData){

	
	if((aData[7]==aData[24] ) && (aData[31]==aData[25]) && (aData[32]==aData[26]) && (aData[8]==aData[27]) && (aData[10]==aData[29]) && (aData[11]==aData[30]) && (aData[9]==aData[28])){
		
		$("#sameasmailing").prop("checked", true);
		document.getElementById("mailingStreet1").disabled = true;
		document.getElementById("mailingStreet3").disabled = true;

		document.getElementById("mailingStreet5").disabled = true;

		document.getElementById("mailingCity2").disabled = true;

		document.getElementById("mailingZipCd2").disabled = true;

		document.getElementById("mailingCountry2").disabled = true;

		document.getElementById("mailing_State2").disabled = true; // Checks it
		
	}else{
		
		$("#sameasmailing").prop("checked", false);
		document.getElementById("mailingStreet1").disabled = false;
		document.getElementById("mailingStreet3").disabled = false;

		document.getElementById("mailingStreet5").disabled = false;

		document.getElementById("mailingCity2").disabled = false;

		document.getElementById("mailingZipCd2").disabled = false;

		document.getElementById("mailingCountry2").disabled = false;

		document.getElementById("mailing_State2").disabled = false; // Unchecks it
	}
	
}
function fnSelectRecord(sender,editmode){
	
	
	if(editmode==true){
		//fnSelectRecord(0,false);
		senderGlobal=sender;
		clearSameAsMailing();
		setValue(); 
		
		 
	}else{
		document.getElementById("ResetUpdate").disabled = false;
		document.getElementById("locationsetupCode").disabled = false;
		 $('#ResetUpdate').hide();
		 $('#ResetNew').show();
		$('#sameasmailing').attr('checked', false);
		 $("#Back").hide();
		 $('#newBack').show();
		 $("#todaysDate").show();
		 $("#locStatusDate").hide();
		 $("#Delete").hide();
		 $("#contentTable").hide();
		 $("#message").hide();
		 $("#message1").hide();
		 $("#locationTable").show();
		 $("#locationMailingInformation").show();
		 $("#locationsetupName").val(''); 
		 $("#locationsetupCode").val('');
		 $("#input_locationsetup_Statuscode").val('A');
		 $("#input_locationsetup_Type1").val('');
		 $("#input_locationsetup_Type2").val('');
		 $("#input_locationsetup_Type3").val('');
		 $("#input_locationsetupRegion").val('');
		 $("#locationsetupPhone1").val('');
		 $("#locationsetupPhone2").val('');
		 $("#locationsetupPhone3").val('');
		 $("#mailingStreet").val('');
		 $("#mailingCity1").val(''); 
		 $("#mailing_State1").val('');  
		 $("#mailingZipCd1").val(''); 
		 $("#mailingCountry1").val('');
		 $("#Save").val('SAVE');
		 $("#lastUpdatedBy").hide();
		 $("#lastUpdatedTime").hide();
		 $("#updatedlastUpdatedTime").hide();
		 $("#updatedlastUpdatedBy").hide();
		 
		 $("#locationsetupfirstName").val(''); 
		 $("#locationsetuplastName").val('');  
		 $("#locationsetupEmail").val('');
		 $("#locationsetupPhone1").val('');
		 $("#locationsetupPhone2").val('');
		 $("#locationsetupPhone3").val('');
		 $("#locationsetupPhone4").val('');
		 $("#locationsetupfaxAreaCode1").val('');
		 $("#locationsetupfaxAreaCode2").val('');
		 $("#locationsetupfaxAreaCode3").val('');
		 $("#locationsetupcellAreaCode1").val('');
		 $("#locationsetupcellAreaCode2").val('');
		 $("#locationsetupcellAreaCode3").val(''); 
		 
		
		 $("#mailingStreet").val(''); 
		 $("#mailingStreet2").val(''); 
		 $("#mailingStreet4").val(''); 
		 $("#mailingStreet1").val(''); 
		 $("#mailingStreet3").val(''); 
		 $("#mailingStreet5").val(''); 
		 $("#mailingCity2").val(''); 
		 $("#locationsetupTitle").val(''); 
		 $("#mailingZipCd1").val('');
		 $("#mailingZipCd2").val('');
		 $("#mailingCountry2").val('');
		 $("#mailing_State1").val('');
		 $("#mailingCountry1").val('US');
		 $("#mailing_State2").val('');				
		 $("#input_locationsetup_Statuscode option[value='A']").attr("selected", "selected");
		 $("#mailingCountry1 option[value='US']").attr("selected", "selected");
		 document.getElementById("mailing_State1").style.backgroundColor = "#FAFFA8";
		 selectMailingCountryForReset();
		 clearSameAsMailing();
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


function trimText(txt){
	txt.value = txt.value.trim();
}


function trimStringSpaces(stringValue) {

	while(stringValue.indexOf(" ") == 0) {
		stringValue = stringValue.substring(1);
	}
	
	while(stringValue.lastIndexOf(" ") != -1 && stringValue.lastIndexOf(" ") == stringValue.length - 1) {
		stringValue = stringValue.substring(0, stringValue.lastIndexOf(" "));
	}
	
	return stringValue;
}



function resetAll(){

	var action = "E";
	
	var parameters = "ACTION=" + action;
	$("#locationName").val('');
	$("#locationCode").val('');
	$("#input_country").val('');
	$("#input_region").val('');
	$("#input_State").val('');
	$("#location_zipCode").val('');
	$("#input_City").val('');
	$("#input_statusCode").val('');
	$("#input_Type").val('');
	document.getElementById("ResetUpdate").disabled = false;
	$('#sameasmailing').attr('checked', false);
	 $("#Back").hide();
	 $('#newBack').hide();
	 $("#todaysDate").hide();
	 $("#locStatusDate").hide();
	 $("#Delete").hide();
	 $("#contentTable").hide();
	 $("#message").hide();
	 $("#message1").hide();
	 $("#locationTable").hide();
	 $("#locationMailingInformation").hide();
	 $("#locationsetupName").val(''); 
	 $("#locationsetupCode").val('');
	 //$("#input_locationsetup_Statuscode").val('');
	 $("#input_locationsetup_Type1").val('');
	 $("#input_locationsetup_Type2").val('');
	 $("#input_locationsetup_Type3").val('');
	 $("#input_locationsetupRegion").val('');
	 $("#locationsetupPhone1").val('');
	 $("#locationsetupPhone2").val('');
	 $("#locationsetupPhone3").val('');
	 $("#mailingStreet").val('');
	 $("#mailingCity1").val(''); 
	 $("#mailing_State1").val('');  
	 $("#mailingZipCd1").val(''); 
	 $("#mailingCountry1").val('');
	 $("#Save").val('SAVE');
	 $("#lastUpdatedBy").hide();
	 $("#lastUpdatedTime").hide();
	 $("#updatedlastUpdatedTime").hide();
	 $("#updatedlastUpdatedBy").hide();
	 
	 $("#locationsetupfirstName").val(''); 
	 $("#locationsetuplastName").val('');  
	 $("#locationsetupEmail").val('');
	 $("#locationsetupPhone1").val('');
	 $("#locationsetupPhone2").val('');
	 $("#locationsetupPhone3").val('');
	 $("#locationsetupPhone4").val('');
	 $("#locationsetupfaxAreaCode1").val('');
	 $("#locationsetupfaxAreaCode2").val('');
	 $("#locationsetupfaxAreaCode3").val('');
	 $("#locationsetupcellAreaCode1").val('');
	 $("#locationsetupcellAreaCode2").val('');
	 $("#locationsetupcellAreaCode3").val(''); 
	 
	
	 $("#mailingStreet").val(''); 
	 $("#mailingStreet2").val(''); 
	 $("#mailingStreet4").val(''); 
	 $("#mailingStreet1").val(''); 
	 $("#mailingStreet3").val(''); 
	 $("#mailingStreet5").val(''); 
	 $("#mailingCity2").val(''); 
	 $("#locationsetupTitle").val(''); 
	 $("#mailingZipCd1").val('');
	 $("#mailingZipCd2").val('');
	 $("#mailingCountry2").val('');
	 $("#mailing_State1").val('');
	 $("#mailingCountry1").val('');
	 $("#mailing_State2").val('');
	$('#actionCode').val('');
	 $("#locationLatestCode").val('');
	 $("#locDate").val('');
	 $("#latestUpdatedBy").val('');
	 $("#input_locationsetup_Statuscode option[value='A']").attr("selected", "selected");
	 $("#mailingCountry1 option[value='US']").attr("selected", "selected");
	 globalmailing_State2="-1";
	document.forms[0].action = "locationSearch.do?"+parameters;
	document.forms[0].target="_self"; 
		document.forms[0].submit();
    
}


function resetOnAddUpdate(){

	$("#locationName").val('');
	$("#locationCode").val('');
	$("#input_country").val('');
	$("#input_region").val('');
	$("#input_State").val('');
	$("#location_zipCode").val('');
	$("#input_City").val('');
	$("#input_statusCode").val('');
	$("#input_Type").val('');
}

function generateLocationExcelReport(frm)
{

	var action = "EXCEL_DOWNLOAD";
	
	var parameters = "ACTION=" + action;
	
	parameters += '&locationName='+ $("#locationName").val(); 
	parameters += '&locationCode='+ $("#locationCode").val();
	parameters += '&input_country='+ $("#input_country").val();
	parameters += '&input_region='+ $("#input_region").val();
	parameters += '&input_State='+ $("#input_State").val();
	parameters += '&location_zipCode='+ $("#location_zipCode").val();
	parameters += '&input_City='+ $("#input_City").val();
	parameters += '&input_statusCode='+ $("#input_statusCode").val();
	parameters += '&input_Type='+ $("#input_Type").val();
	
	$("#action").val('EXCEL_DOWNLOAD');
	$("#ACTION").val('EXCEL_DOWNLOAD');
	
	document.forms[0].action = "locationSearch.do?"+parameters;
	//document.forms[0].target="_blank";
	document.forms[0].submit();
	
}

var specialKeys = new Array();
specialKeys.push(8);
/*function IsNumeric(e) {
    var keyCode = e.which ? e.which : e.keyCode;
    var ret = ((keyCode >= 48 && keyCode <= 57) || specialKeys.indexOf(keyCode) != -1);
   
    return ret;
}*/

var specialKeys1 = new Array();
specialKeys1.push(8);  //Backspace
specialKeys1.push(9);  //Tab
specialKeys1.push(46); //Delete
specialKeys1.push(36); //Home
specialKeys1.push(35); //End
specialKeys1.push(37); //Left
specialKeys1.push(39); //Right


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


function IsAlphaNumeric(e) {
    var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
    var ret = ((keyCode >= 48 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || keyCode == 32 || (keyCode >= 97 && keyCode <= 122) || (specialKeys1.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
   alert("Please enter valid location code");
    
}

function IsAlphaNumericAddress(e) {
    var keyCode = e.keyCode == 0 ? e.charCode : e.keyCode;
    var ret = ((keyCode >= 44 && keyCode <= 57) || (keyCode >= 65 && keyCode <= 90) || keyCode == 32 || (keyCode >= 97 && keyCode <= 122) || (specialKeys1.indexOf(e.keyCode) != -1 && e.charCode != e.keyCode));
   
    return ret;
}

