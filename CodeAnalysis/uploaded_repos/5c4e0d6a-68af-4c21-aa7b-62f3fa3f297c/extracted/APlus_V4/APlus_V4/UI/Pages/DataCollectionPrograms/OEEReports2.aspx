<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="OEEReports2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.OEEReports2"
    Title="OEE Reports" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td>
                <asp:Label ID="lblWorkcenter" runat="server" Text="Workcenter:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtWorkcenter" runat="server" CssClass="Textbox_Entry" MaxLength="10"
                    Width="175px"></asp:TextBox><asp:RequiredFieldValidator ID="reqWorkcenter" runat="server"
                        ErrorMessage="Enter Workcenter" ControlToValidate="txtWorkcenter" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblReport" runat="server" Text="Report:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtReport" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="700px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReport" runat="server" ErrorMessage="Enter Report"
                    ControlToValidate="txtReport" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblURL" runat="server" Text="URL:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtURL" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="700px"></asp:TextBox><asp:RequiredFieldValidator ID="reqURL" runat="server"
                        ErrorMessage="Enter Report" ControlToValidate="txtURL" Display="None"></asp:RequiredFieldValidator>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
