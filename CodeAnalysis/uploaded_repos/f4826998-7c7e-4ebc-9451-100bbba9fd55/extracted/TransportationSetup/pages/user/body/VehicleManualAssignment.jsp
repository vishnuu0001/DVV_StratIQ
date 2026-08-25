<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
 <%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c"%>  
<%@ taglib uri="/WEB-INF/struts-html.tld" prefix="html" %> 
<%@taglib uri="/WEB-INF/struts-bean.tld" prefix="bean"%>
<%@taglib uri="/WEB-INF/struts-logic.tld" prefix="logic"%>

<bean:write name="VehicleManualAssignmentForm" property="script" filter="false" />
<script src="javascript/custom/vehicleManualAssignment.js?timestamp=123" type="text/javascript"></script>

<div class="row-fluid">
	<div class="span12 pageTitle">
		Vehicle Manual Assignment
	</div>
</div>

<html:form action="/VehicleManualAssignmentOperation">
	<html:hidden property="ACTION" name="VehicleManualAssignmentForm"></html:hidden>
	<input type="hidden" id="allReasonCodes" name="allReasonCodes" value="${allReasonCodes}"/>
	<input type="hidden" id="username" name="username" value="${username}"/>
	
	<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>

	
	<div class="row-fluid">
		<div class="span12 InquiryBox">
			<table style="width: 100%; padding-left:20px; margin: 6px;">
				<tr>
					<td style="width:12%;">Order Ref/VIN*:</td>
					<td style="width:8%; vertical-align:middle;"><input type="text" style="width:150px;" name="VIN_CD" id="input_vin" maxlength="17" size="17" value=""/></td>
					<td style="width:4%;">&nbsp;&nbsp;<b>OR</b>&nbsp;</td>
					<td style="width:12%;">Model Year*:</td>
					<td style="width:8%; vertical-align:middle;">
						
						<select style="width: 98px; height: 21px;" id="input_model_year" name="MDL_YR_DT">
							<option selected="selected" value="">--Model Year--</option>
							<c:forEach var="item" items="${modelYearList}">
								<option value="${item}">${item}</option>
							</c:forEach>
						</select>
					</td>
					
					<td style="width:4%;"></td>
					<td style="width:8%;">Carline*:</td>
					<td style="width:8%; vertical-align:middle;">
						<select style="width: 98px; height: 21px;" name="CRLN_CD" id="input_carline">
							<option selected="selected" value="">--Carline--</option>
							<c:forEach var="carline" items="${carlineList}">
								<option value="${carline.CRLN_CD}">
									<c:out value="${carline.CRLN_CD}" />
								</option>
							</c:forEach>
						</select>
						
					</td>
					<td style="width:6%;"></td>
					<td style="width:6%;">Model*:</td>
					<td style="width:8%; vertical-align:middle;">
						<select style="width: 98px; height: 21px;" name="MDL_CD" id="input_model">
							<option selected="selected" value="">--Model Code--</option>
						</select>
					</td>
					
				</tr>
				<tr>
				<td style="height: 10px;" colspan="15"></td>
			</tr>
				<tr>
					<td>Ext Clr:</td>
					<td style="vertical-align:middle;">
						<input type="text" style="width:100px;" name="EXT_CLR" id="input_ext_clr" maxlength="3" size="3" value=""/>
					</td>
					<td></td>
					<td>Int Clr:</td>
					<td style="vertical-align:middle;">
						<input type="text" style="width:100px;" name="INT_CLR"  id="input_int_clr" maxlength="3" size="3" value=""/>
					</td>
					<td></td>
					<td> <input type="button" value="Search" id="Search" class="submitButton" onClick="return doSearch();" /></td>
					<td>
						<td></td>
					</td>
					<td></td>
					<td></td>
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
		<div class="span12 error" id="message">
		</div>
	</div>
	
	<div class="row-fluid"><div class="span12" style="min-height: 10px;"></div></div>
	<div class="span12" style="margin-left: 0px" id="contentTable">
		<table id="vehManAssgmnt" class="tabledetWithOutBorder" border="0" cellpadding="6" cellspacing="3">
			<thead>
				<tr>
					<th>
						<input type="checkbox" name="chkAction"
										id="chkActionAll" onclick="fnOpenEditModeAll(this)"
										style="border: none; width: 15px;">
					</th>
					<th>LOCTN CD/DLR CD</th>
					<th>Order Ref/VIN</th>
					<th>Model Year</th>
					<th>Car Line</th>
					<th>Model</th>
					<th>Ext Color</th>
					<th>Int Color</th>
					<th>Current Status</th>
					<th>Current Location</th>
					<th></th>
					
				</tr>
		     </thead>
		 </table>
	</div>
		
	<div class="row-fluid">
		<div class="span12 control-box" style="padding-left:40px;">
			<ul>
				<li><input type="button" id="assignBtn" class="submitButton" value="ASSIGN" onclick="return doSave();"></li>
				<!-- For Excel Downloader, Added a button 'DOWNLOAD' , Starts-->
				<li><input type="button" id="downloadBtn" class="submitButton" value=DOWNLOAD onclick="return doDownload();"> <input type="hidden" name="action" id="action"/>  </li>
				<!-- Ends -->
			</ul>
		</div>
	</div>
	
</html:form>
