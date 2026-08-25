<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="WorkcenterSelection.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.WorkcenterSelection"
    Title="Workcenter Selection" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/jscript" language="javascript" src="../../../Scripts/CommonFunctions.js">

        defaultStatus = "Workcenter Selection"

        function CheckWorkcenter() {
            if (document.Form1.ddlWorkcenter.value == '') {
                var msg = "\n You have selected a blank Workcenter.  \n" +
						"\n\n" +
						"You will be re-directed to the last Menu.\n" +
						"\n\n";
                return confirm(msg);
            }
        }			
    </script>

    <asp:Panel ID="pnlTeamSel" runat="server" Wrap="False" Width="78.25%">
        <table id="Table1" style="width: 664px; height: 30px" cellspacing="2" cellpadding="2"
            width="664" border="0">
            <tr>
                <td style="width: 96px">
                    <asp:Label ID="lblTeam" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlWorkcenter" runat="server" Width="352px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                </td>
            </tr>
        </table>
        <br />
        <table id="Table2" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" CausesValidation="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
