<HTML>
<HEAD>
<TITLE>Default Login Frame</TITLE>
<style type="text/css">
<!--
.note {  font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #3399FF}
-->
</style>

</HEAD>
<SCRIPT LANGUAGE="JAVASCRIPT">

	function init()  {
		if(window.document.forms["LoginAction"].userid.value == "")		{
			window.document.forms["LoginAction"].userid.focus();
		}
		else		{
			window.document.forms["LoginAction"].password.focus();
		}
	}

	function validate(thisForm)   
     {
		if(thisForm.userid.value=="")       
         {
			alert("Please enter a valid user id");
			window.document.forms["LoginAction"].userid.focus();
			return false;
		}
	}


</SCRIPT>

<BODY onLoad="init()" bgcolor="white">
<FORM NAME="LoginAction" ACTION="${$_LOCAL_LOGIN_TARGET_URI_$}" METHOD="post" onSubmit="return validate(this)">
    <div align="center">
    <h3>
  <font color="#000066">Please Log-In</font></h3>
  </div>
  <table colspan="2" align="center" width="229">
    <tr>
      <td align="right">
        <div align="right"><font size="3" color=darkblue> </font><font color="#000066">Userid:</font></div>
      </td>
      <td align="left">
        <div align="center">
          <input type="text" size="8" maxlength="8" name="userid">
        </div>
      </td>
    </tr>
    <tr>
      <td align="center" colspan="2" height="42">
        <input type="submit" name="Submit" value="Login">
      </td>
    </tr>

    <tr>
      <td></td>
    </tr>
  </table>
  <input type="hidden" name="id" value="SEC001">
  <table align="center" width="43%" border="0" cellspacing="0" cellpadding="0">
    <tr> 
      <td colspan="2">
        <div align="center">Please select your application target audience:</div>
      </td>
    </tr>
    <tr> 
      <td width="48%"> 
        <div align="right">US 
          <input type="radio" name="fromCntryCd" value="US" checked>
        </div>
      </td>
      <td width="52%"> 
        <div align="left">Mexico 
          <input type="radio" name="fromCntryCd" value="MX">
        </div>
      </td>
      <td width="52%"> 
        <div align="left">Canada 
          <input type="radio" name="fromCntryCd" value="CA">
        </div>
      </td>
      <td width="52%"> 
        <div align="left">None
          <input type="radio" name="fromCntryCd" value="">
        </div>
      </td>
	  
    </tr>
	<tr> 
      <td width="48%"> 
        <div align="right">Language 
          
        </div>
      </td>
      <td width="52%"> 
        <div align="left"> 
          <select name="language">
		  <option value="en">English</option>
		  <option value="es">Espanol</option>
		  <option value="fr">French</option>
		  <option value="">None</option>		  
		  </select>
        </div>
      </td>
    </tr>
  </table>
</form>
<font face="Verdana, Arial" size="3" color="red">

</font> 
<table align="center" width="79%" border="0" cellspacing="0" cellpadding="0" height="39">
  <tr> 
    <td class="note">
      <div align="center"><b>Note</b>: In production environment, users will come 
        into mazdausa domain from different urls. By selecting the target audience 
        the http session will be properly setup to simulate the production environment.</div>
    </td>
  </tr>
</table>
<p>&nbsp;</p>
</BODY>
</HTML>
