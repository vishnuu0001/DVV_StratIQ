<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
 <%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>  
<%@ taglib uri="/WEB-INF/struts-html.tld" prefix="html" %> 
<%@taglib uri="/WEB-INF/struts-bean.tld" prefix="bean"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<%@page import="com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant"%>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<script type="text/javascript" src="javascript/custom/CarrierSetup.js"></script>

<link href="<%=request.getContextPath()%>/css/bootstrap.css" type="text/css" rel="stylesheet">
<link href="<%=request.getContextPath()%>/css/mnao_portlets.css" rel="stylesheet" type="text/css">
<!--<script type="text/javascript" src="<%=request.getContextPath()%>/javascript/custom/bootstrap.min.js"></script>-->

<SCRIPT>window.history.forward(1)</SCRIPT>
<title>Carrier Setup</title>
<Style>


.tabledetWithOutBorder tr td:nth-child(2) {
    text-align: left;
} 

a {
    color: #0086d7;
    text-decoration: underline;
    cursor: pointer;
}
.success {
	margin-left:30%;
    font-size:20px;
    color:green;
  background-color: white;
}

 .InquiryBox td{
 	padding:5px;
 }
 .left {
    text-align: left;
}
.paginate_enabled_next{
	padding-left:3px;
}
</Style>
<div class="row-fluid">
	<div class="span12 pageTitle">
		Carrier Setup
	</div>
</div>
<%
String userStatus=(String)request.getSession().getAttribute(AppConstant.LTS_USER_PRIVILEGE);
 %>
 
<html:form action="/carrierSetup" type="com.mazdausa.corporate.vehicles.distribution.application.form.CarrierSetupForm" >
	
	
	<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>

	<div class="row-fluid">
		<div class="span12 InquiryBox">
			<table style="width: 96%; padding-left:20px; margin: 6px;">
				<tr>
					<td style="width:12%;">Name:</td>
					<td style="width:8%; vertical-align:middle;">
						<input type="text" style="width:150px;" name="searchCarrierName" id="searchCarrierName" maxlength="40" size="17" value=""/>
					</td>
					<td style="width:12%;padding-left:5px;">Code:</td>
					<td style="width:8%; vertical-align:middle;">
						<input type="text" onkeypress="return IsAlphaNumeric(event);"  onblur="isAlphaNumericOnBlur(this.id,' Code' )"    style="width:150px;" onkeyup="toUpperCaseCarrier()" name="searchCarrierCode" id="searchCarrierCode" maxlength="5" size="17" value=""/>
					</td>
					<td style="width:12%;padding-left:5px;">Status:</td>
					<td style="width:8%; vertical-align:middle;">
						
						<select style="width: 98px; height: 21px;" id="searchStatusCd" name="searchStatusCd">
							<c:forEach var="statusList" items="${carrierSetupForm.statusList}">
								<option value="${statusList.value}">${statusList.label}</option>
							</c:forEach>
						</select>
					</td> 
					<td style="width:12%;padding-left:5px;">Type:</td>
					<td style="width:8%; vertical-align:middle;">
						
						<select style="width: 98px; height: 21px;" id="searchTypeCd" name="searchTypeCd">
							<c:forEach var="typeList" items="${carrierSetupForm.typeList}">
								<option value="${typeList.value}">${typeList.label}</option>
							</c:forEach>
						</select>
					</td>
					
					
				</tr>
				<tr>
				<td style="height: 10px;" colspan="15"></td>
			</tr>
				<tr>
					<td>Currency:</td>
					<td style="vertical-align:middle;">
						<select style="width: 98px; height: 21px;" id="searchCurrencyCd" name="searchCurrencyCd">
							<c:forEach var="currencyList" items="${carrierSetupForm.currencyList}">
								<option value="${currencyList.value}">${currencyList.label}</option>
							</c:forEach>
						</select>
					</td>
					<td colspan="4" style="padding-left:5px;">
					
						 <input type="button" value="Search" id="Search" class="submitButton" onClick="return doSearch();" /> &nbsp;&nbsp;
						 <% if(userStatus.equalsIgnoreCase("ltsadmin")){ %>
						 <input type="button" value="Add New" id="Search" class="submitButton" onClick="return showAddNew();" />&nbsp;&nbsp;
						 <%} %>
						 
						 <input type="button" value="Reset" id="Search" class="submitButton" onClick="return searchReset();" />	 
						  
					</td>
					
					<td></td>
					<td></td>
				</tr>
				<tr>
				<td style="height: 10px;" colspan="15"></td>
			</tr>
				
				<tr>
				<td style="height: 10px;" colspan="15"></td>
			</tr>
				
				
			</table>
		</div>		
	</div>
	
	
	<div class="row-fluid"> 
		<div class="span12 error" style="text-transform: none" id="message">
		</div>
		
	</div>
	
	<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>
	<div class="span12" style="margin-left: 0px; display:none;" id="contentTable">
		<div ><input type="hidden" name="action" id="action" />
					<a href="javascript:void(0);" onclick="generateExcelReport('/carrierSetupForm');">
						<img src="<%=request.getContextPath()%>/images/excel.JPG" alt="" width="18" height="16" align="right" border="0" >
					</a>
			</div>	
		<table id="carrierGrid" class="tabledetWithOutBorder" border="0" cellpadding="6" cellspacing="3" >
			<thead>
				<tr>
					<th>
						Carrier Code
					</th>
					<th>Address</th>
					<th>Carrier Type</th>
					<th>Status</th>
					<th>Currency</th>
					
				</tr>
		     </thead>
		 </table>
	</div>
	<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>
	
		
		<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>
	<div class="row-fluid" id="carrierTable" style="display:none;">
		<div class=" InquiryBox">
			<table width="100%" border="0" align="center" class="tableCls">
			  <tbody><tr class="subHeader">
			    <td width="50%" ><strong>Carrier Information</strong></td>
			    <td colspan="50%"><strong> </strong></td>
			  </tr>
			</tbody></table>
			
			
			<table width="100%" border="0" align="center" cellspacing="3" cellspacing="3">		
					<tbody>
			  <tr>
			    <td width="20%"><label class="labelCustomize">Carrier Name</label> </td>
			    <td width="30%"> 
			    <input type="text" name="carrierName" id="carrierName" maxlength="30" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;"> 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Carrier Code</label> </td>
			    <td width="30%"><input onkeypress="return IsAlphaNumeric(event);" onblur="isAlphaNumericOnBlur(this.id,' Carrier Code' )"    type="text" name="carrierCd" id="carrierCd" maxlength="5" value="" onblur="trimText(this);" class="mandLocTextStyle" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;"> 
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize">Carrier Type</label> </td>
			    <td width="30%"> 
			    <select name="carrierType" id="carrierType" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
					<!--<option value="">All</option>  -->			    
			   <c:forEach var="detailedTypeList" items="${carrierSetupForm.detailedTypeList}">
								<option value="${detailedTypeList.value}">${detailedTypeList.label}</option>
							</c:forEach>
			    </select>
			    
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Currency</label> </td>
			    
			    <td width="30%">
			     <select name="currencyCd" id="currencyCd" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
			    <!--<option value="">All</option>  -->
			    <c:forEach var="detailedCurrencyList" items="${carrierSetupForm.detailedCurrencyList}">
								<option value="${detailedCurrencyList.value}">${detailedCurrencyList.label}</option>
							</c:forEach>
			    </select>
			  
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize">Status </label> </td>
			    <td width="30%"> 
			    <input type="radio" name="status" id="statusId1" value="A" onclick="statusDateChange(this.value)" checked="checked"/> <label for="statusId1">Active</label>&nbsp; <input type="radio" value="I" onclick="statusDateChange(this.value)" name="status" id="statusId2" /><label for="statusId">Inactive</label> 
			     
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Status Date</label> </td>
			    <td width="30%"><%java.text.DateFormat df = new java.text.SimpleDateFormat("MM/dd/yyyy");
			    String statusdate =df.format(new java.util.Date());
			     %>
			    <span id="statusDateSpan"><%= statusdate%></span>
			    
			    <input type="hidden" name="statusDate" id="statusDate" maxlength="15" value="<%=statusdate%>" onblur="trimText(this);" class="mandLocTextStyle">
			    <input type="hidden" name="statusDate1" id="statusDate1" maxlength="15" value="<%=statusdate%>" onblur="trimText(this);" class="mandLocTextStyle"> 
			   
			   
			   
				
				
			   </td>
			  </tr>
			   <tr>
			    <td width="20%"><label class="labelCustomize">Receive Delivery Data </label> </td>
			    <td width="30%"> 
			    <input type="radio" name="receivingDeliveryDate" id="receivingDeliveryDate1"  checked="checked" value="Y"/> <label for="receivingDeliveryDate1">Yes</label>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <input type="radio" name="receivingDeliveryDate" id="receivingDeliveryDate2" value="N" /> <label for="receivingDeliveryDate2">No</label>
			     
			  
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Return Error Data</label> </td>
			    <td width="30%">
			    <input type="radio" name="receivingErrorData" id="receivingErrorData1" checked="checked"  value="Y"/> <label for="receivingErrorData1">Yes</label> <input type="radio" name="receivingErrorData" id="receivingErrorData2" value="N" /> <label for="receivingErrorData2">No</label>
			   </td>
			  </tr>
			  <tr class="addNewHide">
			    <td width="20%"><label class="labelCustomize">Last Updated By </label> </td>
			    <td width="30%"> 
			     <span id="lastUpdatedBy"> </span>
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Last Updated Time</label> </td>
			    <td width="30%">
			     <span id="lastUpdatedAt"> </span>
			   </td>
			  </tr>
			  </tbody>
			  </table>
			  
			  <table width="100%" border="0" align="center" class="tableCls">
			  <tbody><tr class="subHeader">
			    <td width="50%" ><strong>Contact Information</strong></td>
			    <td colspan="50%"><strong> </strong></td>
			  </tr>
			</tbody></table>
			<table width="100%" border="0" align="center" cellspacing="3" cellspacing="3">	
					<tbody>
			  <tr>
			    <td width="20%"><label class="labelCustomize">First Name</label> </td>
			    <td width="30%"> 
			    <input type="text" name="firstName" id="firstName" maxlength="15" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Last Name</label> </td>
			    <td width="30%"><input type="text" name="lastName" id="lastName" maxlength="20" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="mandLocTextStyle"> 
			   </td>
			  </tr>
			   
			  <tr>
			    <td width="20%"><label class="labelCustomize">Title </label> </td>
			    <td width="30%"> 
			    <input type="text" name="titleName" id="titleName" maxlength="20" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Email</label> </td>
			    <td width="30%"><input type="text" name="email" id="email" maxlength="30" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="mandLocTextStyle"> 
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize">Phone </label> </td>
			    <td width="30%"> 
			    <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="phoneAcNo" id="phoneAcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			     <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="phoneExcNo" id="phoneExcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			      <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="phoneNo" id="phoneNo" maxlength="4" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px!important;">
			       <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="phoneExtensnNo" id="phoneExtensnNo" maxlength="5" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px!important;"> 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Fax</label> </td>
			    <td width="30%"><input onkeypress="return IsNumeric(event);" ondrop="return false;"   type="text" name="faxAcNo" id="faxAcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			     <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="faxExcNo" id="faxExcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			      <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="faxNo" id="faxNo" maxlength="4" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			      
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize">Cell </label> </td>
			    <td width="30%"> 
			    <input type="text"  onkeypress="return IsNumeric(event);" ondrop="return false;"   name="cellAcNo" id="cellAcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			     <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"   name="cellExcNo" id="cellExcNo" maxlength="3" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px !important;">
			      <input type="text" onkeypress="return IsNumeric(event);" ondrop="return false;"    name="cellNo" id="cellNo" maxlength="4" value="" onblur="trimText(this),isValidNumber(this.id);" style="width:50px!important;">
			       
			   </td>
			  
			    <td width="20%"> </td>
			    <td width="30%">
			       
			   </td>
			  </tr>
			  </tbody>
			  </table>
			  
			   <table width="100%" border="0" align="center" class="tableCls">
			  <tbody><tr class="subHeader">
			    <td width="50%" ><strong>Mailing Address</strong></td>
			    <td colspan="50%"><strong>Shipping Address </strong></td>
			  </tr>
			</tbody></table>
			<table width="100%" border="0" align="center" cellspacing="3" cellspacing="3">		
			<tbody>
				 <tr>
			    <td width="20%"> </td>
			    <td width="30%"> 
			    
			   </td>
			  
			    <td width="20%"><input type="checkbox"  name="sameAsMailingAddresss" id="sameAsMailingAddresss"  onclick="sameAsMailling();"/><label class="labelCustomize">Same as Mailing Address</label> </td>
			    <td width="30%"> 
			   </td>
			  </tr>	
			  <tr>
			    <td width="20%"><label class="labelCustomize">Street</label> </td>
			    <td width="30%"> 
			    <input type="text" name="mailingAddr1" id="mailingAddr1" maxlength="30" value=""  onchange="clearSameAsMailing();" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			    <td width="20%"><label class="labelCustomize">Street</label> </td>
			    <td width="30%"><input type="text" name="shippingAddr1" id="shippingAddr1" maxlength="30" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="mandLocTextStyle sameAsMailingAddresscls"> 
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize"></label> </td>
			    <td width="30%"> 
			    <input type="text" name="mailingAddr2" id="mailingAddr2" maxlength="30" value=""  onchange="clearSameAsMailing();" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			 
			    <td width="20%"><label class="labelCustomize"></label> </td>
			    <td width="30%"><input type="text" name="shippingAddr2" id="shippingAddr2" maxlength="30" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="sameAsMailingAddresscls mandLocTextStyle"> 
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize"></label> </td>
			    <td width="30%"> 
			    <input type="text" name="mailingAddr3" id="mailingAddr3" maxlength="30" onchange="clearSameAsMailing();" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize"></label> </td>
			    <td width="30%"><input type="text" name="shippingAddr3" id="shippingAddr3" maxlength="30" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="mandLocTextStyle sameAsMailingAddresscls"> 
			   </td>
			  </tr>  
			   <tr>
			    <td width="20%"><label class="labelCustomize">City </label> </td>
			    <td width="30%"> 
			    <input type="text" name="mailingCity" id="mailingCity" maxlength="25" value="" onchange="clearSameAsMailing();" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" > 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">City</label> </td>
			    <td width="30%"><input type="text" name="shippingCity" id="shippingCity" maxlength="25" value="" onkeyup="toUpperCaseCarrier()" onblur="trimText(this);" class="mandLocTextStyle sameAsMailingAddresscls"> 
			   </td>
			  </tr>
			  
			  <tr>
			    <td width="20%"><label class="labelCustomize">Zip </label> </td>
			    <td width="30%"> 
			    <input type="text" onkeypress="return IsNumeric(event);" name="mailingZipCd" id="mailingZipCd" maxlength="9" value=""  onchange="clearSameAsMailing();" onblur="trimText(this),isValidNumber(this.id);" > 
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">Zip</label> </td>
			    <td width="30%"><input type="text" onkeypress="return IsNumeric(event);" name="shippingZipCd" id="shippingZipCd" maxlength="9" value="" onblur="trimText(this),isValidNumber(this.id);" class="mandLocTextStyle sameAsMailingAddresscls"> 
			   </td>
			  </tr>
			  
			   <tr>
			    <td width="20%"><label class="labelCustomize">Country </label> </td>
			    <td width="30%"> 
			     <select name="mailingCountryCd" id="mailingCountryCd" onchange="pouplateStateDropDown('mailingCountryCd','mailingStateCd'), clearSameAsMailing();">
			    <option value="">SELECT</option>
			    <c:forEach var="countryList" items="${carrierSetupForm.countryList}">
								<option value="${countryList.value}">${countryList.label}</option>
							</c:forEach>
			    </select>
			    
			   </td>
			 
			    <td width="20%"><label class="labelCustomize">Country</label> </td>
			    <td width="30%">
			     <select name="shippingCountryCd" id="shippingCountryCd" onchange="pouplateStateDropDown('shippingCountryCd','shippingStateCd')">
			    <option value="">SELECT</option>
			    <c:forEach var="countryList" items="${carrierSetupForm.countryList}">
								<option value="${countryList.value}">${countryList.label}</option>
							</c:forEach>
			    </select>
			    
			   </td>
			  </tr>
			  <tr>
			    <td width="20%"><label class="labelCustomize" >State </label> </td>
			    <td width="30%"> 
			     <select name="mailingStateCd" id="mailingStateCd" onchange="clearSameAsMailing();" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
			    <option value="">SELECT</option>
			    <c:forEach var="stateList" items="${carrierSetupForm.stateList}">
								<option value="${stateList.value}">${stateList.label}</option>
							</c:forEach>
			    </select>
			    
			  
			   </td>
			  
			    <td width="20%"><label class="labelCustomize">State</label> </td>
			    <td width="30%">
			     <select name="shippingStateCd" id="shippingStateCd">
			    <option value="">SELECT</option>
			    <c:forEach var="stateList" items="${carrierSetupForm.stateList}">
								<option value="${stateList.value}">${stateList.label}</option>
							</c:forEach>
			    </select>
			    
			   </td>
			  </tr> 
			   
			  
				<tr>
					 <td width="20%"> </td>
			    <td width="50%" align="center" colspan="2" style="padding-left:120px;"> 
			    
			    <% if(userStatus.equalsIgnoreCase("ltsadmin")){ %>
			   <input type="button" id="savebtn" value="SAVE" class="submitButton" onclick="populateCarrierOperation('A','0')"> 
			    <input type="button" value="UPDATE" id="updatebtn" class="submitButton" onclick="populateCarrierOperation('U','0')"> 
			    <input type="button" id="deletebtn" value="DELETE" class="submitButton" onclick="populateCarrierOperation('R','0')">
			    <%} %>
			    <input type="button" value="Back" id="formAddNewBack" class="submitButton" onClick="return searchReset();" /> 
			    <input type="button" value="Back" id="formEditBack" class="submitButton" onClick="return doSearch();" /> 
			    <input type="button" value="Reset" id="resetAddNew" class="submitButton" onClick="return AddNewReset();" /> 
			    <input type="button" value="Reset" id="resetUpdate" class="submitButton" onClick="return resetValueForEdit();" /> 
			     </td>
			    <td width="30%"> 
			   </td>
				</tr>
			  </tbody>
			  </table>
			  
			 
	
		  </div>
 </div> 
 <br>
 <br>
  <div class=""> 
		<div class="success " style="text-transform: none" id="message1">
		</div>
		<div class="error " style="text-transform: none" id="message2">
		</div>
	</div>
</html:form>
