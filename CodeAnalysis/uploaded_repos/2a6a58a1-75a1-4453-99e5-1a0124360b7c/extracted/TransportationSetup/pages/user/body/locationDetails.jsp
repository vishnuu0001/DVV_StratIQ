<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>
<%@ taglib prefix = "fmt" uri = "http://java.sun.com/jsp/jstl/fmt" %>
<%@ taglib uri="/WEB-INF/struts-html.tld" prefix="html" %> 
<%@taglib uri="/WEB-INF/struts-bean.tld" prefix="bean"%>
<%@taglib uri="/WEB-INF/struts-logic.tld" prefix="logic"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">

<%@page import="com.mazdausa.corporate.vehicles.distribution.application.constants.AppConstant"%>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">

<link href="<%=request.getContextPath()%>/css/bootstrap.css" type="text/css" rel="stylesheet">
<link href="<%=request.getContextPath()%>/css/mnao_portlets.css" rel="stylesheet" type="text/css">
<!--<script type="text/javascript" src="<%=request.getContextPath()%>/javascript/custom/bootstrap.min.js"></script>-->
<script language="javascript" type="text/javascript" src="<%=request.getContextPath()%>/javascript/custom/location.js"></script>

<SCRIPT>window.history.forward(1)</SCRIPT>
<title>Location Details</title>

<style type="text/css">
#contentTable{display:none;}
#assignBtn{display:none;}
#downloadBtn{display:none;}
#locationTable{display:none;}
#locationMailingInformation{display:none;}

</style>

<style>

a {
    color: #0086d7;
    text-decoration: underline;
    cursor: pointer;
}

.tabledetWithOutBorder tr td:nth-child(2) {
    text-align: left;
} 

.success {
	margin-left:30%;
    font-size:20px;
    color:green;
  background-color: white;
}
.InquiryBoxCustomize {
    margin: 0px 2px 0px 0%;
    background-color: #f3f3f3;
    border: 1px solid #dadada;
    padding: 10px;
}

.InquiryBoxCustomizeLocation {
     margin: -382px 2px 30px 217px;
    background-color: #f3f3f3;
    border: 1px solid #dadada;
    padding: 10px;
    float: left;
}

.InquiryBoxCustomizeMailingInfo{
	background-color: #f3f3f3;
    border: 1px solid #dadada;
    padding: 10px;
    float: left;
    margin: -45px 0px 55px 217px;
}

.searchTableCustomize {
    width: 1103px;
}
.dataTables_length{ 
	width:100%; float:left; margin-bottom:5px; padding-left:15px; font-size:11px;
	}

.dataTables_paginate a {
    margin: 0 20px 0 0px;
}


</style>



</head>

<body>
<%
String userStatus=(String)request.getSession().getAttribute(AppConstant.LTS_USER_PRIVILEGE);
 %>

<html:form  action="/locationSearch"  styleId="locForm">  
<div>
	<div class="pageTitle">
		Location Setup
	</div>
</div>

<br>
<br>


<div class="InquiryBoxCustomize" style="width:100%">
	
	<table  border="0">
      <tr>
        <td style="width:8%;"><label class="labelCustomize">Name</label></td>
						<td style="width:8%; vertical-align:middle;">
							<input type="text"  name="locationName" id="locationName" maxlength="30" onblur="trimText(this);">
		</td>
        <td style="width:2%;"></td>
						<td style="width:8%;"><label class="labelCustomize">Code</label></td>
						<td style="width:8%; vertical-align:middle;">
						<input type="text"  onblur="isAlphaNumericOnBlur(this.id,' Code')" name="locationCode" maxlength="5" id="locationCode" onkeyup="toUpperCaseLocation()" onblur="trimText(this);">
		</td>
        <td style="width:2%;"></td>
        
						<td style="width:8%;"><label class="labelCustomize">Country</label></td>
						<td style="width:8%; vertical-align:middle;">
					
						<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_country" property="countryCode" onchange="selectCountry();">
	                      	<html:option value="">ALL</html:option>
	                      	<logic:notEmpty name="locationIndexForm" property="countryList"> 	
							<html:optionsCollection name="locationIndexForm" property="countryList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
		</td>
		
		</tr>
       	 <tr>
						<td  colspan="8">&nbsp;</td>
		</tr>	
		<tr>
						<logic:notEmpty name="locationIndexForm" property="regionCodeList">
						<td ><label class="labelCustomize">Region</label></td>
						<td style="vertical-align:middle;">
<!--							 input_Type input_statusCode input_City location_zipCode input_State -->
						<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_region" property="regionCode" onchange="selectState();">
	                      	<html:option value="">ALL</html:option> 	
							
							<logic:notEmpty name="locationIndexForm" property="regionCodeList">
							<html:optionsCollection name="locationIndexForm" property="regionCodeList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
       					
						</td>
						</logic:notEmpty>
      					
      					<td style=""></td>
      					<logic:notEmpty name="locationIndexForm" property="stateNameList">
						<td ><label class="labelCustomize">State</label></td>
						<td style=" vertical-align:middle;">
							
						<html:select name="locationIndexForm" styleClass="locationCombo"  styleId="input_State" property="stateName">
	                      	<html:option value="">ALL</html:option> 	
							<logic:notEmpty name="locationIndexForm" property="stateNameList">
							<html:optionsCollection name="locationIndexForm" property="stateNameList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
						
						</td>
						</logic:notEmpty>
						<td style=""></td>
						<td ><label class="labelCustomize">Zip Code</label></td>
						<td style="vertical-align:middle;">
							<input type="text" onblur="isAlphaNumericOnBlur(this.id,' Zip Code')" name="location_zipCode" id="location_zipCode" maxlength="9" onblur="trimText(this);">
						</td>
	  </tr>
	  <tr>
						<td  colspan="8">&nbsp;</td>
	  </tr>
	  
	 <tr>
					
						<td ><label class="labelCustomize">City</label></td>
						<td style="vertical-align:middle;">
							<input type="text"   name="input_City" id="input_City" maxlength="25" onblur="trimText(this);">
						</td>
						
						<td style=""></td>
						<td ><label class="labelCustomize">Status</label></td>
						<td style=" vertical-align:middle;">
						
						<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_statusCode" property="statusCode">
	                      	<html:option value="">ALL</html:option>
	                      <logic:notEmpty name="locationIndexForm" property="statusCodeList">
							<html:optionsCollection name="locationIndexForm" property="statusCodeList" label="label" value="value"/>
						</logic:notEmpty>
						</html:select>

						</td>
						
						<td style=""></td>
						<logic:notEmpty name="locationIndexForm" property="typeNameList">
						<td ><label class="labelCustomize">Type</label></td>
						<td style=" vertical-align:middle;">
							
						<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_Type" property="typeName">
	                      	<html:option value="">ALL</html:option> 	
						<logic:notEmpty name="locationIndexForm" property="typeNameList">
							<html:optionsCollection name="locationIndexForm" property="typeNameList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>	
						
						</td>
						</logic:notEmpty>
						
		</tr>
		<tr>
					<td>&nbsp;</td>
		</tr>
		<tr>
					<td style="padding-left:30px;" colspan="8" align="center">
						<input name="submitbutton" type="button" class="submitButton" value="Search" onClick="return doSearch();">
						
						<% if(userStatus.equalsIgnoreCase("ltsadmin")){ %>
						<input name="submitbutton" type="button" class="submitButton" value="ADD NEW" onClick="return fnSelectRecord(0,false);">
						<%} %>
						<input name="reset" type="button" class="submitButton" value="Reset" onClick="resetAll();">
					</td>
		</tr>
					
					<tr>
						<td  colspan="8">&nbsp;</td>
		</tr>
	</table>
</div>


<br>
<br>
<div class=""> 
		<div class="error "  style="text-transform: none" id="message">
		</div>
	</div>
	<div class="span12" style="width:102%; margin-left: 0%;display:none;" id="contentTable" >
	<div ><input type="hidden" name="action" id="action" />
	<input type="hidden" name="ACTION" id="ACTION" />
			<a href="#">
				<img src="<%=request.getContextPath()%>/images/excel.JPG" alt="" width="18" height="16" align="right" border="0" onclick="return generateLocationExcelReport('/locationIndexForm');">
			</a>
	</div>		
		<table id="vehManAssgmnt" style="width:100%" class="tabledetWithOutBorder" border="0" cellpadding="6" cellspacing="3"  >
			<thead>
				<tr style="width:100%" >
					<!-- <th style="width:10%">
						<input type="checkbox" name="chkAction"
										id="chkActionAll" onclick="fnOpenEditModeAll(this)"
										style="border: none; ">
					</th> -->
				
					<th style="width:10%">Location</th>
					<th style="width:35%">Address</th>
					<th style="width:13%">Address Type</th>
					<th style="width:12%">Status</th>
					<th style="width:10%">Type</th>
					<th style="width:10%">Region</th>
				</tr>
		     </thead>
		 </table>
	</div>

<br>
<br>

<div class="row-fluid" id="locationTable" style="display:none;">
<div class="InquiryBoxCustomizeLocation" style="width:100%; margin-top: 0%;margin-left:0%">
<table width="100%" border="0" align="center" class="tableCls">
  <tbody><tr class="subHeader">
    <td width="50%" ><strong>Location Information</strong></td>
    <td colspan="50%"><strong>Contact</strong></td>
  </tr>
</tbody></table>

 <%java.text.DateFormat df = new java.text.SimpleDateFormat("yyyy-MM-dd"); %>

<table width="100%" border="0" align="center" cellspacing="0">		
		<tbody>
  <tr>
    <td width="20%"><label class="labelCustomize">Location Name</label> </td>
    <td width="30%"> 
    <input type="text"   name="locationsetupName" id="locationsetupName" maxlength="30" onkeyup="toUpperCaseLocation()" value="" onblur="trimText(this);" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;"> 
   </td>
  
    <td width="20%"><label class="labelCustomize">First Name</label> </td>
    <td width="30%"><input type="text" name="locationName" id="locationsetupfirstName" maxlength="15" onkeyup="toUpperCaseLocation()" onblur="isAlphaNumericWithSpaceOnBlur(this.id,' First Name')" value="" onblur="trimText(this);" class="mandLocTextStyle"> 
   </td>
  </tr>
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
  
  <tr>
    <td ><label class="labelCustomize">Location Code</label></td>
    <td >
	<input type="text" name="locationsetupCode" id="locationsetupCode" maxlength="5" onkeyup="toUpperCaseLocation()" onblur="isAlphaNumericOnBlur(this.id,' Location Code')" value=""  onblur="trimText(this);" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;"> 
   </td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Last Name</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text"  name="locationsetuplastName" id="locationsetuplastName" onkeyup="toUpperCaseLocation()" onblur="isAlphaNumericWithSpaceOnBlur(this.id,' Last Name')" maxlength="20" value="" onblur="trimText(this);" class="mandLocTextStyle">
	</td>

  </tr>
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
  <tr>
    <td><label class="labelCustomize">Status</label> </td>
    <td>

						<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_locationsetup_Statuscode" property="locstatusCode"  onchange="statusDateChange(this.value)"  style="font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
	                      	<html:option value="" >SELECT</html:option> 	
	                      	<logic:notEmpty name="locationIndexForm" property="statusCodeList">
							<html:optionsCollection name="locationIndexForm" property="statusCodeList" label="label" value="value"/>
							</logic:notEmpty>
					  </html:select>
</td>
    <td ><label class="labelCustomize">Title</label></td>
    <td >
	<input type="text"   name="locationsetupTitle" id="locationsetupTitle" maxlength="20" onkeyup="toUpperCaseLocation()" value="" onblur="trimText(this);" class="mandLocTextStyle"> 
   </td>
</tr>

<tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
					
  <tr>
    <td class="nonMandLocTextStyle"></td>
	<td class="nonMandLocTextStyle"></td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Email</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="locationsetupEmail" id="locationsetupEmail" maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle">
	</td>

  </tr>
  <tr>
						<td  colspan="8">&nbsp;</td>
 </tr>

  <tr>
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Status Date </label></td>
    <td class="nonMandLocTextStyle"><html:hidden name="locationIndexForm" property="currentDate" styleId="currentDate" value="<%= df.format(new java.util.Date())%>"></html:hidden><h7 id="todaysDate" "class="labelCustomize"><%= df.format(new java.util.Date())%></h7>
	<input type="text" name="locStatusDate" id="locStatusDate">
    </td>	
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Phone</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="locationsetupPhone1" id="locationsetupPhone1"  style="width:50px !important" size="3" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
	<input type="text" name="locationsetupPhone2" id="locationsetupPhone2"   style="width:50px !important" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
	<input type="text" name="locationsetupPhone3" id="locationsetupPhone3"   style="width:50px !important" maxlength="4" value="" onblur="trimText(this);" class="inputPhone">
	<input type="text" name="locationsetupPhone4" id="locationsetupPhone4"   style="width:50px !important" maxlength="5" value="" onblur="trimText(this);" class="inputPhone">
	<label class="labelCustomize">Bus</label>
	</td>

  </tr>
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
  <tr>
    <td ><label class="labelCustomize">Location Type&nbsp;1</label></td>
    <td> 				<html:select name="locationIndexForm" styleClass="mandLocTextStyle" styleId="input_locationsetup_Type1" property="loctypeName">
	                      	<html:option value="" >SELECT</html:option>
	                      	<logic:notEmpty name="locationIndexForm" property="typeNameList"> 	
							<html:optionsCollection name="locationIndexForm" property="typeNameList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>	
						<input type="hidden" name="old_input_locationsetup_Type1" id="old_input_locationsetup_Type1" />
</td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Fax</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="locationsetupfaxAreaCode1" id="locationsetupfaxAreaCode1"  style="width:50px !important" size="3" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
	<input type="text" name="locationsetupfaxAreaCode2" id="locationsetupfaxAreaCode2"   style="width:50px !important" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
	<input type="text" name="locationsetupfaxAreaCode3" id="locationsetupfaxAreaCode3"   style="width:50px !important" maxlength="4" value="" onblur="trimText(this);" class="inputPhone">
	</td>

  </tr>
  
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
					
					
  <tr>
    <td ><label class="labelCustomize">Location Type&nbsp;2</label></td>
    <td> 
    					<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_locationsetup_Type2" property="loctypeName2">
	                      	<html:option value="" >SELECT</html:option> 
	                      	<logic:notEmpty name="locationIndexForm" property="typeNameList">	
							<html:optionsCollection name="locationIndexForm" property="typeNameList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
						<input type="hidden" name="old_input_locationsetup_Type2" id="old_input_locationsetup_Type2" />
</td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Cell</label></td>
    <td class="nonMandLocTextStyle">
		<input type="text" name="locationsetupcellAreaCode1" id="locationsetupcellAreaCode1"   style="width:50px !important" size="3" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
		<input type="text" name="locationsetupcellAreaCode2" id="locationsetupcellAreaCode2"   style="width:50px !important" maxlength="3" value="" onblur="trimText(this);" class="inputPhone">
		<input type="text" name="locationsetupcellAreaCode3" id="locationsetupcellAreaCode3"   style="width:50px !important" maxlength="4" value="" onblur="trimText(this);" class="inputPhone">
	
	</td>

  </tr>
  
  <tr>
						<td  colspan="8">&nbsp;</td>
 </tr>

  
  <tr>
    <td ><label class="labelCustomize">Location Type&nbsp;3</label></td>
    <td> 
    					<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_locationsetup_Type3" property="loctypeName3">
	                      	<html:option value="" >SELECT</html:option> 	
	                      	<logic:notEmpty name="locationIndexForm" property="typeNameList">
							<html:optionsCollection name="locationIndexForm" property="typeNameList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
						<input type="hidden" name="old_input_locationsetup_Type3" id="old_input_locationsetup_Type3" />
</td>
    
    <td class="nonMandLocTextStyle" id="updatedlastUpdatedBy"><label class="labelCustomize">Last Updated By </label></td>
    <td class="nonMandLocTextStyle">
    	<input type="text" name="lastUpdatedBy" id="lastUpdatedBy">
    </td>	

  </tr>
  
  <tr>
						<td  colspan="8">&nbsp;</td>
 </tr>

<tr>
    <td ><label class="labelCustomize">Region</label></td>
    <td> 
    					<html:select name="locationIndexForm" styleClass="locationCombo" styleId="input_locationsetupRegion" property="locregionCode" onchange="selectState();">
	                      	<html:option value="" >SELECT</html:option> 	
							<logic:notEmpty name="locationIndexForm" property="regionCodeList">
							<html:optionsCollection name="locationIndexForm" property="regionCodeList" label="label" value="value"/>
							</logic:notEmpty>
						</html:select>
</td>
 
 
<td class="nonMandLocTextStyle" id="updatedlastUpdatedTime"><label class="labelCustomize">Last Updated Time</label></td>
    <td class="nonMandLocTextStyle">
    	<input type="text" name="lastUpdatedTime" id="lastUpdatedTime">
    </td>	

  </tr>
  
<tr>
						<td  colspan="8">&nbsp;</td>
</tr>
					
					
  </tbody>
  </table>
</div>
</div>
<br>
<br>


<div class="row-fluid" id="locationMailingInformation">


<div class="InquiryBoxCustomizeMailingInfo" style="width:100%; margin-left: 0%;">

<table width="100%" border="0" align="center" class="tableCls">
  <tbody><tr class="subHeader">
    <td width="50%"><strong>Mailing Address</strong></td>
    <td colspan="50%"><strong>Shipping Address</strong></td>
  </tr>
</tbody>
</table>
<table width="100%" border="0" align="center" cellspacing="3" cellpadding="3">

<tbody>
<tr>
	<td width="20%"></td>
	<td width="30%"></td>
	<td width="20%"></td>
	<td width="30%">
	<input type="checkbox" name="sameasmailing" id="sameasmailing" onclick="sameAsMailing();"> 
	<strong>(Same as Mailing)</strong>
	</td>
</tr>

<tr>
						<td  colspan="8">&nbsp;</td>
</tr>

<tr>
    <td width="20%"><label class="labelCustomize">Street</label> </td>
    <td width="30%"> <input type="text" name="mailingStreet" id="mailingStreet"   maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle" onchange="clearSameAsMailing();"> 
   </td>
  
    <td width="20%"><label class="labelCustomize">Street</label> </td>
    <td width="30%"><input type="text" name="mailingStreet1" id="mailingStreet1"   maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle"> 
   </td>
</tr>
  
<tr>
						<td  colspan="8">&nbsp;</td>
</tr>

  <tr>
    <td ></td>
    <td >
	<input type="text" name="mailingStreet2" id="mailingStreet2" maxlength="30"   value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle" onchange="clearSameAsMailing();"> 
   </td>
 
    <td class="nonMandLocTextStyle"></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="mailingStreet3" id="mailingStreet3"   maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle">
	</td>

  </tr>
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
					
  <tr>
    <td> </td>
    <td>
 <input type="text" name="mailingStreet4" id="mailingStreet4"   maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle" onchange="clearSameAsMailing();">
</td>
    <td ></td>
    <td >
	<input type="text" name="mailingStreet5" id="mailingStreet5"   maxlength="30" value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle"> 
   </td>
</tr>

<tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
					
  <tr>
    <td><label class="labelCustomize">City</label></td>
	<td><input type="text" name="mailingCity1" id="mailingCity1" maxlength="25"   value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;" onchange="clearSameAsMailing();"></td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">City</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="mailingCity2" id="mailingCity2" maxlength="25"   value="" onkeyup="toUpperCaseLocation()" onblur="trimText(this);" class="mandLocTextStyle">
	</td>

  </tr>
  
<tr>
						<td  colspan="8">&nbsp;</td>
</tr>
				
					
  
<tr>
	<td  colspan="8">&nbsp;</td>
</tr>

<tr>
    <td ><label class="labelCustomize">Zip</label></td>
    <td> <input type="text" name="mailingZipCd1" id="mailingZipCd1"  onblur="isAlphaNumericOnBlur(this.id,' Zip Code')"  maxlength="9" value="" onblur="trimText(this);" class="mandLocTextStyle" onchange="clearSameAsMailing();"></td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">Zip</label></td>
    <td class="nonMandLocTextStyle">
	<input type="text" name="mailingZipCd2" id="mailingZipCd2" onblur="isAlphaNumericOnBlur(this.id,' Zip Code')" maxlength="9" value="" onblur="trimText(this);" class="mandLocTextStyle">
	</td>

  </tr>
  
  <tr>
						<td  colspan="8">&nbsp;</td></tr>
					<tr>
					
					
<tr>
<td ><label class="labelCustomize">Country</label></td>
<td>
	<html:select name="locationIndexForm" styleClass="locationCombo" styleId="mailingCountry1" property="mailcountryCode" onchange="selectMailingCountry(),clearSameAsMailing();" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
    	<html:option value="" >SELECT</html:option> 	
    	<logic:notEmpty name="locationIndexForm" property="countryList">
		<html:optionsCollection name="locationIndexForm" property="countryList" label="label" value="value"/>
		</logic:notEmpty>
   </html:select>
</td>
 
<td class="nonMandLocTextStyle"><label class="labelCustomize">Country</label></td>
<td class="nonMandLocTextStyle">
	<html:select name="locationIndexForm" styleClass="locationCombo" styleId="mailingCountry2" property="shipcountryCode" onchange="selectShippingCountry(); ">
    	<html:option value="" >SELECT</html:option> 
    	<logic:notEmpty name="locationIndexForm" property="countryList">	
		<html:optionsCollection name="locationIndexForm" property="countryList" label="label" value="value"/>
		</logic:notEmpty>
	</html:select>
</td>
</tr>

<tr>
<td  colspan="8">&nbsp;</td>
</tr>

<tr>
    <td ><label class="labelCustomize">State</label></td>
    <td >
    <html:select name="locationIndexForm" styleClass="locationCombo"  styleId="mailing_State1" onchange="clearSameAsMailing();" property="mailstateName" style="background-color: #FAFFA8;font-family: Arial, Helvetica, sans-serif;font-size: 10px;width: 225px;">
	     <html:option value="" >SELECT</html:option> 	
		<html:optionsCollection name="locationIndexForm" property="stateNameList" label="label" value="value"/>
	</html:select>
    </td>
 
    <td class="nonMandLocTextStyle"><label class="labelCustomize">State</label></td>
    <td>
	<html:select name="locationIndexForm" styleClass="locationCombo"  styleId="mailing_State2" property="shipstateName">
	     <html:option value="" >SELECT</html:option> 	
		<html:optionsCollection name="locationIndexForm" property="stateNameList" label="label" value="value"/>
	</html:select>
	</td>

  </tr>

<tr>
	<td  colspan="8">&nbsp;</td>
</tr>

					
<tr>
<td>&nbsp;</td>
</tr>
<tr>
				<td colspan="8" align="center">
				<% if(userStatus.equalsIgnoreCase("ltsadmin")){ %>
				<input name="Save" type="button" class="submitButton" id="Save" value="Save" onclick="return actionCheck();">
<!--				<input name="Delete" type="button" class="submitButton" id="Delete" value="Delete" disabled="true">  -->
				<input name="Delete" type="button" class="submitButton" id="Delete" value="Delete" onclick=" return deleteLocationDetails();">
			<!--  input name="Reset" type="button" class="submitButton" id="ResetUpdate" value="Reset" onClick="return fnSelectRecord(0,false),selectMailingCountry(),selectShippingCountry();"-->

				<%} %>
							<input name="Reset" type="button" class="submitButton" id="ResetUpdate" value="Reset" onClick="return setValue2();">   
 				<input name="Reset" type="button" class="submitButton" id="ResetNew" value="Reset" onClick="return fnSelectRecord(0,false);">
 				<input name="Back" type="button" class="submitButton" id="Back" value="Back" onclick=" return dobackbuttonClick();">
				<input name="Back" type="button" class="submitButton" id="newBack" value="Back" onclick=" resetAll();">
				</td>
</tr>

<tr>
<td  colspan="8">&nbsp;</td>
</tr>
  
</tbody>
</table>

</div>
</div>	

	<!-- <div class=""> 
		<div class="error "  style="text-transform: none" id="message">
		</div>
	</div>
 -->
	<div class=""> 
		<div class="success " style="text-transform: none" id="message1">
		</div>
	</div>
	<html:hidden name="locationIndexForm" property="districtCode" styleId="districtCode"></html:hidden>
	<html:hidden name="locationIndexForm" property="locationLatestCode" styleId="locationLatestCode" />
	<html:hidden name="locationIndexForm" property="actionCode" styleId="actionCode" />
	<html:hidden name="locationIndexForm" property="locDate" styleId="locDate" />
	<html:hidden name="locationIndexForm" property="latestUpdatedBy" styleId="latestUpdatedBy" />
	
			
</html:form>
</body>
</html>
