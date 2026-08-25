<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamLog2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamLog2"
    Title="Team Log Maintenance" ValidateRequest="false" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>

    <script type="text/javascript" language="javascript">
        $(document).ready(function() {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>

    <table id="TABLE2" class="Table_Default">
        <tr>
            <td style="width: 804px; height: 55px" valign="top" colspan="4">
                <asp:Label ID="lblLogEntry" runat="server" Text="Log Entry:" CssClass="Label_Left_8PT"></asp:Label><br />
                <asp:TextBox ID="txtExpandLogEntry" runat="server" CssClass="Textbox_Entry" MaxLength="1000"
                    Width="656px" Height="24px" Rows="8" TextMode="MultiLine"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqLogEntry" runat="server" ErrorMessage="EnterLog Entry "
                    ControlToValidate="txtExpandLogEntry" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 804px; height: 51px" valign="top">
                <asp:Label ID="lblLogResponse" runat="server" Text="Log Response:" CssClass="Label_Left_8PT"></asp:Label><br />
                <asp:TextBox ID="txtExpandLogResponse" runat="server" CssClass="Textbox_Entry" MaxLength="1000"
                    Width="656px" Height="24px" Rows="20" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
    </table>
    <table id="TABLE4" class="Table_Default">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblCreateUserID" runat="server" Text="Create UserID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 69px">
                <asp:TextBox ID="txtCreateUserID" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="69px"></asp:TextBox>
            </td>
            <td style="width: 100px">
                <asp:Label ID="lblCreateDateTime" runat="server" Text="Create Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCreateDateTime" runat="server" CssClass="Textbox_Display" MaxLength="22"
                    Width="112px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblMaintenanceUserID" runat="server" Text="Maintenance UserID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 69px">
                <asp:TextBox ID="txtMaintenanceUserID" runat="server" CssClass="Textbox_Display"
                    MaxLength="10" Width="69px"></asp:TextBox>
            </td>
            <td>
                <asp:Label ID="lblMaintenanceDate" runat="server" Text="Maintenance Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaintenanceDate" runat="server" CssClass="Textbox_Display" MaxLength="20"
                    Width="112px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td colspan="4">
                <asp:CheckBox ID="chkSendTeamLogEmail" runat="server" Text="Send a Team Log Email when Saved"
                    Font-Bold="True"></asp:CheckBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td>
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left">
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
