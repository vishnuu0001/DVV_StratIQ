<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIReportCategoryMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIReportCategoryMaster2"
    Title="KPI Group" ValidateRequest="false" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="lblReportCategoryID" runat="server" Text="KPI Group ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtReportCategoryID" runat="server" Width="50px" MaxLength="15"
                    CssClass="Textbox_Display" Height="16px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblReportGroup" runat="server" Text="Program:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlReportGroup" runat="server" Width="258px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtReportGroup" runat="server" Width="249px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReportGroup" runat="server" ErrorMessage="Select Program"
                    ControlToValidate="ddlReportGroup" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblReportName" runat="server">KPI Group:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtReportItem" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="200px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReportItem" runat="server" ErrorMessage="Enter KPI Group"
                    ControlToValidate="txtReportItem" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" Width="200px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" Width="200px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblReport" runat="server" Text="Report:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlReport" runat="server" Width="150px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="3">KPIReport 1</asp:ListItem>
                    <asp:ListItem Value="4">KPIReport 2</asp:ListItem>
                    <asp:ListItem Value="5">KPIReport 3</asp:ListItem>
                    <asp:ListItem Value="6">KPIReport 4</asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtReport" runat="server" Width="150px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px" ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqReport" runat="server" ErrorMessage="Select Report"
                    ControlToValidate="ddlReport" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblSequence" runat="server">Sequence:</asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSequence" runat="server" CssClass="Textbox_Entry" Width="43px"
                    MaxLength="2"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSequence" runat="server" ErrorMessage="Enter Sequence"
                    ControlToValidate="txtSequence" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblActive" runat="server">Active:</asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkActive" runat="server" Checked="True" />
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 107px;
        }
    </style>
</asp:Content>
