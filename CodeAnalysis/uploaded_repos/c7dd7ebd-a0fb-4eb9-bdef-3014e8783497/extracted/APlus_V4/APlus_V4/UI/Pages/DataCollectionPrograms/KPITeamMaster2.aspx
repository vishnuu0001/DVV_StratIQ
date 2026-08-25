<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPITeamMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPITeamMaster2"
    Title="KPI Team Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 81px">
                <asp:Label ID="lblKPI" runat="server" Text="KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlKPI" runat="server" CssClass="DropdownList_Entry" Width="320px">
                </asp:DropDownList>
                <asp:TextBox ID="txtKPI" runat="server" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True" Width="315px" Visible="False"></asp:TextBox>&nbsp;
                <asp:DropDownList ID="ddlKPISite" runat="server" CssClass="DropdownList_Entry" Width="194px"
                    AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlTeam" runat="server" CssClass="DropdownList_Entry" Width="320px">
                </asp:DropDownList>
                <asp:TextBox ID="txtTeam" runat="server" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True" Width="315px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblKPIView" runat="server" Text="Allow KPI View:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPIView" runat="server" />
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblKPIEdit" runat="server" Text="Allow KPI Edit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPIEdit" runat="server" />
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
