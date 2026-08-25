<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamSelection.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamSelection"
    Title="Team Selection" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript">
        function CheckTeam(objControl) {
            if (objControl.value == '') {

                var msg = "\n You have selected a blank Team.  \n" +
						"\n\n" +
						"You will be re-directed to the last Menu.\n" +
						"\n\n";
                return confirm(msg);
            }
        }	
    </script>

    <table id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 65px; padding-top: 20px;">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="padding-top: 20px">
                <asp:DropDownList ID="ddlTeam" runat="server" Width="600px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
            </td>
        </tr>
    </table>
    <table id="Table2" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" CausesValidation="False">
                </asp:Button>
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
                </asp:Button>
            </td>
            <td>
                <asp:CheckBox ID="chkDisplayClosedTeams" runat="server" Text="Include Closed Teams"
                    AutoPostBack="True"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <cc1:ListSearchExtender ID="lsTeamSelection" runat="server" TargetControlID="ddlTeam"
        EnableViewState="false" PromptCssClass="ListSearchExtenderPrompt">
    </cc1:ListSearchExtender>
</asp:Content>
