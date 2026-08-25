<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserSiteMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSiteMaster2"
    Title="User Site Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label1" runat="server" Text="User Name:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlUserID" runat="server" CssClass="DropdownList_Entry" Width="240px">
                </asp:DropDownList>
                <asp:TextBox ID="txtUserID" runat="server" MaxLength="15" CssClass="Textbox_Display"
                    ReadOnly="True" Width="240px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUser" runat="server" ErrorMessage="Select User"
                    ControlToValidate="ddlUserID" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
                    ControlToValidate="ddlSite" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label3" runat="server" Text="Allow Team View:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowTeamView" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label4" runat="server" Text="Allow Team Edit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowTeamEdit" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label5" runat="server" Text="Allow KPI View:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowKPIView" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="Label6" runat="server" Text="Allow KPI Edit:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowKPIEdit" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
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
                <td align="left">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="false" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
