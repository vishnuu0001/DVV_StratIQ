<%@ Page Language="vb" AutoEventWireup="false" CodeFile="Login.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Login" %>

<%@ Register TagPrefix="cc1" Namespace="WebApp.APlus.UI.CustomControls" %>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Login</title>
    <link type="text/css" href="Styles/LoginStyle.css" rel="stylesheet" />
    <script type="text/javascript" language="JavaScript" src="Scripts/CommonFunctions.js"></script>
    <script type="text/javascript" language="javascript">
        function display_status()
        { var msg = "Login..."; defaultStatus = msg; }

        function AutoLogin(event)
        { if (event.altKey && event.keyCode == 76 && window.location.href.indexOf('?') == -1) window.location.href = window.location.href + '?auto=y'; }

        function DisableLoginKeys(event) {
            if ((event.keyCode >= 112 && event.keyCode <= 115) || (event.keyCode == 91) || (event.keyCode == 93) || (event.keyCode == 19))
            { event.cancelBubble = true; event.keyCode = 0; event.returnValue = false; event.cancel = true; return false; }
        }
    </script>
    <style type="text/css">
        .style1
        {
            width: 70px;
            height: 20px;
            vertical-align: middle;
            text-align: left;
        }
        .style2
        {
            height: 20px;
        }
    </style>
</head>
<body onmousedown="javascript:rightmousebutton(window.event);" onkeydown="javascript:IgnoreTab(window.event);DisableLoginKeys(window.event);TrapEnterKey(document.Form1.btnLogin,window.event);AutoLogin(window.event);"
    onhelp="javascript:return openHelp();" onfocusin="javascript:ActivateTextBox();"
    onbeforedeactivate="javascript:DeActivateTextBox();" leftmargin="1" topmargin="1"
    rightmargin="1">
    <form id="Form1" method="post" autocomplete="on" runat="server">
    <table id="tbApplicationHeader" runat="server" cellspacing="0" cellpadding="0" class="Header">
        <tr>
            <td class="Header_left">
                <asp:Image ID="imgKey" runat="server" ImageAlign="Baseline" ImageUrl="~/images/securekeys.gif">
                </asp:Image>
                &nbsp;<asp:Label runat="server" ID="lblLoginHeader" CssClass="TitleText">Login</asp:Label>
            </td>
            <td class="Header_middle">
                <asp:Image ID="imgAPlus" runat="server" ImageUrl="~/images/APlusLogo.gif" Width="125px" />
            </td>
            <td class="Header_right">
                <asp:Image ID="Image1" runat="server" ImageUrl="Images/company_logo.png"></asp:Image>
            </td>
        </tr>
    </table>
    <table id="tbSubHeader" runat="server" class="SubHeader" cellpadding="0" cellspacing="0">
        <tr>
            <td colspan="2" class="SubHeader">
                &nbsp;<asp:Label ID="lblTime" runat="server" Text="Label" CssClass="SubLabel"></asp:Label>
                &nbsp;
            </td>
        </tr>
    </table>
    <br />
    <table width="100%">
        <tr>
            <td valign="top" style="width: 60%">
                <table id="Table1">
                    <tr>
                        <td class="style1">
                            <asp:Label runat="server" ID="lblUserName" CssClass="Label" Text="User Name:"></asp:Label>
                        </td>
                        <td class="style2">
                            <asp:TextBox ID="txtLogin" runat="server" CssClass="Textbox_Entry_UpperCase" MaxLength="15"
                                EnableViewState="False" Width="175"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td class="style1">
                            <asp:Label ID="lblPassword" runat="server" CssClass="Label" Text="Password:"></asp:Label>
                        </td>
                        <td class="style2">
                            <asp:TextBox ID="txtPwd" runat="server" CssClass="Textbox_Entry" EnableViewState="False"
                                Width="175" TextMode="Password" MaxLength="40"></asp:TextBox>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2">
                            <asp:CheckBox ID="chkWindowsLogin" runat="server" CssClass="Checkbox" EnableViewState="False"
                                Text="Use my Network Login" Width="152px" Visible="True"></asp:CheckBox>&nbsp;&nbsp;
                        </td>
                    </tr>
                    <tr>
                        <td class="style1">
                        </td>
                        <td>
                            <asp:Button ID="btnLogin" runat="server" CssClass="Button" EnableViewState="False"
                                Text="OK"></asp:Button>
                        </td>
                    </tr>
                </table>
            </td>
            <td valign="top" align="left">
                <!-- You may add new image buttons with the appropriate flags below.  Make sure that the 
                    ID of the imagebutton follows the same covention as the others in here exactly.  Make sure
                    that you include the alternate text which shows up as a tooltip in the browser.  Make sure that
                    you also include the onclick event handler to be the same as all the others.
                    The code behind will automatically pick up the new flag, create the appropriate culture, and get the
                    strings from the correct .resources file (provided you have copied the correct resources file in the 
                    resources folder)
                    -->
                <div runat="server" id="CultureButtons">
                    <asp:ImageButton ID="btn_en_GB" runat="server" ImageUrl="~/Images/FlagImages/united_kingdom.png"
                        AlternateText="British English" Height="30px" Width="30px" OnClick="ChangeLanguage" />&nbsp;
                    <asp:ImageButton ID="btn_en_US" runat="server" ImageUrl="~/images/FlagImages/usa.png"
                        AlternateText="American English" Height="30px" Width="30px" OnClick="ChangeLanguage" />&nbsp;
                    <asp:ImageButton ID="btn_de_DE" runat="server" ImageUrl="~/Images/FlagImages/germany.png"
                        AlternateText="Deutsch" Height="30px" Width="30px" OnClick="ChangeLanguage" Visible="False" />&nbsp;
                    <asp:ImageButton ID="btn_fr_FR" runat="server" ImageUrl="~/Images/FlagImages/france.png"
                        AlternateText="Francais" Height="30px" Width="30px" OnClick="ChangeLanguage"
                        Visible="True" />&nbsp;
                    <asp:ImageButton ID="btn_it_IT" runat="server" ImageUrl="~/Images/FlagImages/italy.png"
                        AlternateText="Italiano" Height="30px" Width="30px" OnClick="ChangeLanguage"
                        Visible="true" />&nbsp;
                    <asp:ImageButton ID="btn_fi_FI" runat="server" ImageUrl="~/Images/FlagImages/finland.png"
                        AlternateText="Suomeksi" Height="30px" Width="30px" OnClick="ChangeLanguage"
                        Visible="False" />&nbsp;
                    <asp:ImageButton ID="btn_sv_SE" runat="server" ImageUrl="~/Images/FlagImages/sweden.png"
                        AlternateText="Svensk" Height="30px" Width="30px" OnClick="ChangeLanguage" Visible="True" />&nbsp;
                    <asp:ImageButton ID="btn_es_ES" runat="server" ImageUrl="~/Images/FlagImages/spain.png"
                        AlternateText="Español" Height="30px" Width="30px" OnClick="ChangeLanguage" Visible="True" />&nbsp;
                    <asp:ImageButton ID="btn_pt_BR" runat="server" ImageUrl="~/Images/FlagImages/brazil.png"
                        AlternateText="Português" Height="30px" Width="30px" OnClick="ChangeLanguage"
                        Visible="True" />
                </div>
            </td>
        </tr>
    </table>
    <div style="text-align: right; padding-right: 5px;">
        <asp:Label runat="server" ID="lblVersion" CssClass="Label_Right_8PT">Version: </asp:Label></div>
    <cc1:ApplicationErrorControl ID="ErrorControl" runat="server">
    </cc1:ApplicationErrorControl>
    </form>
</body>
</html>
