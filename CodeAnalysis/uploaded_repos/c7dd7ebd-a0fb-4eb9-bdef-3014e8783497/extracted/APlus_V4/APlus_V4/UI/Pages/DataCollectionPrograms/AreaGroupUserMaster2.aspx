<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AreaGroupUserMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AreaGroupUserMaster2"
    Title="User Site Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="lblArea" runat="server" Text="Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqArea" runat="server" ErrorMessage="Select Area"
                    ControlToValidate="ddlArea" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblUser" runat="server" Text="User Name:" CssClass="Label_Left_8PT"></asp:Label>
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
            <td class="style1">
                <asp:Label ID="lblEvaluate" runat="server" Text="Allow Anomaly Evaluate:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowAnomalyEvaluate" runat="server" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblEdit" runat="server" Text="Allow Anomaly Edit:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowAnomalyEdit" runat="server" 
                    CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIView" runat="server" Text="Allow KPI View:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAllowKPIView" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIEdit" runat="server" Text="Allow KPI Edit:" CssClass="Label_Left_8PT"></asp:Label>
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 125px;
        }
    </style>
</asp:Content>
