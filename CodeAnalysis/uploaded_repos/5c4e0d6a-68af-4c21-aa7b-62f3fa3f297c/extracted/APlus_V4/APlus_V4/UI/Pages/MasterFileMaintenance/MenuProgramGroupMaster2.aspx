<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MenuProgramGroupMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MenuProgramGroupMaster2"
    Title="Menu Program Group Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label4" runat="server" Text="Menu:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMenu" Width="315px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label5" runat="server" Text="Program Group:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtProgramGroup" Width="315px" ReadOnly="True" MaxLength="50" CssClass="Textbox_Display"
                    runat="server" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqProgramGroup" runat="server" ErrorMessage="Enter Program Group"
                    ControlToValidate="txtProgramGroup" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label2" runat="server" Text="Column:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtColumn" Width="23px" runat="server" CssClass="Textbox_Entry"
                    MaxLength="2"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label1" runat="server" Text="Sort Order:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSortOrder" Width="23px" runat="server" CssClass="Textbox_Entry"
                    MaxLength="2"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td align="left" class="Label_Left_8PT">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory" runat="server" InitialStateExpanded="False"
        TableName="MenuProgramGroupMaster" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
