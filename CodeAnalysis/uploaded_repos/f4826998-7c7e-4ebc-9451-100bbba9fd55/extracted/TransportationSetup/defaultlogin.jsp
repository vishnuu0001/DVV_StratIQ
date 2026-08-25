<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<%@taglib uri="/WEB-INF/struts-bean.tld" prefix="bean"%>
<%@taglib uri="/WEB-INF/struts-html.tld" prefix="html"%>
<HTML>
<HEAD>
<TITLE>Default Login</TITLE>
<style type="text/css">
<!--
.note {  font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #3399FF}
-->
</style>

</HEAD>
<SCRIPT LANGUAGE="JAVASCRIPT">

	function init()  {
		if(window.document.forms["localloginActionForm"].userid.value == "")		{
			window.document.forms["localloginActionForm"].userid.focus();
		}
		/*
		else		{
			window.document.forms["localloginActionForm"].password.focus();
		}*/
	}

	function validate(thisForm)   {
		if(thisForm.userid.value=="")       {
			alert("Please enter a valid user id");
			window.document.forms["localloginaction"].userid.focus();
			return false;
		}
		
		/*
		else		{
			if(this.Form.password.value=="")          {
				alert("Please enter a valid password");
				window.document.forms["localloginActionForm"].password.focus();
				return false;
			}
			return true;
		}*/
	}

	function updatePasswordSelected(checkbox) {
		if(window.document.forms["localloginActionForm"].userid.value == "mazda" || window.document.forms["LoginAction"].userid.value == "") {
			alert("This ID can not change Password.");
		} 
		else { 
			var defaultUrl = "/emazda/internet/commonlogin/defaultlogin.jsp";
			var updateUrl = "/emazda/internet/commonlogin/updatelogin.jsp";
			if	(checkbox.checked)	{
				window.location = updateUrl;
			}
			else		{
				window.location = defaultUrl;
			}
		}
	}

</SCRIPT>

<BODY onLoad="init()" bgcolor="white">
<html:form action="/localloginaction"  method="post">
    <div align="center">
    <h3>
  <font color="#000066">Local Test Environment</font></h3>
  </div>

  <table width="95%" border="0" align="center">
    <tr>
      <td width="95%"></td>
      <td width="05%"></td>
    </tr>
  </table>

  <table align="center" width="229">
    <tr>
      <td align="right">
        <div align="right"><font size="3" color=darkblue> </font><font color="#000066">Userid:</font></div>
      </td>
      <td align="left">
        <div align="center">
          <html:text property="userid" maxlength="8" size="8"></html:text>
        </div>
      </td>
    </tr>
    

    <tr>
      <td></td>
    </tr>
  </table>
  <table align="center" width="43%" border="0" cellspacing="0" cellpadding="0">
    <tr> 
      <td colspan="2">
        <div align="center">Please select your application target audience:</div>
      </td>
    </tr>
    <tr> 
      <td> 
        <div align="right">US <html:radio property="fromCntryCd" value="US" ></html:radio>
        </div>
      </td>
      <td> 
        <div align="left">Mexico 
          <html:radio property="fromCntryCd" value="MX"></html:radio>
        </div>
      </td>
      <%--td width="52%"> 
        <div align="left">None
          <html:radio property="fromCntryCd" value=""></html:radio>
        </div>
      </td--%>
	  
    </tr>
	<tr> 
      <td width="48%"> 
        <div align="right">Language</div>
      </td>
      <td width="52%"> 
        <div align="left"> 
          <html:select property="language">
	          <html:option value="en">English</html:option>
	          <html:option value="es">Espanol</html:option>
	          <%--html:option value="">None</html:option--%>
          </html:select>
        </div>
      </td>
	<tr>
      <td align="center" colspan="2" height="42">
        <html:submit value="Submit"></html:submit>
      </td>
    </tr>
  </table>
</html:form>

<table align="center" width="79%" border="0" cellspacing="0" cellpadding="0" height="39">
  <tr> 
    <td class="note">
      <div align="center"><b>Note</b>: In production environment, users will come 
        into mazdausa domain from different urls. By selecting the target audience 
        the http session will be properly setup to simulate the production environment.</div>
    </td>
  </tr>
</table>

</BODY>

</HTML>
