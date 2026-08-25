<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPIUserNotifications2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPIUserNotifications2"
    Title="KPI User Notifications" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPI" runat="server" Text="KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlKPI" runat="server" CssClass="DropdownList_Entry" Width="350px">
                </asp:DropDownList>
                <asp:TextBox ID="txtKPI" runat="server" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True" Width="350px" Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblUser" runat="server" Text="User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlUser" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtUser" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUser" runat="server" ErrorMessage="Select User"
                    ControlToValidate="ddlUser" Display="None"></asp:RequiredFieldValidator>
                &nbsp;<asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry"
                    Width="194px" AutoPostBack="True">
                </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIValueEntry" runat="server" Text="KPI Value Entry:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPIValueEntry" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIValueReminder" runat="server" Text="KPI Value Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPIValueReminder" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPITargetEntry" runat="server" Text="KPI Target Entry:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPITargetEntry" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPITargetReminder" runat="server" Text="KPI Target Reminder:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPITargetReminder" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblKPIDeviation" runat="server" Text="KPI Deviation:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckKPIDeviation" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAnomalyPending" runat="server" Text="Anomaly Pending:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAnomalyPending" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAnomalyPendingReminder" runat="server" Text="Anomaly Pending Reminder:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAnomalyPendingReminder" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAnomalyActions" runat="server" Text="Anomaly Actions:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAnomalyActions" runat="server" />
            </td>
        </tr>
        <tr>
            <td class="style1">
                <asp:Label ID="lblAnomalyActionsReminder" runat="server" Text="Anomaly Actions Reminder:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAnomalyActionsReminder" runat="server" />
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
<asp:Content ID="Content2" runat="server" ContentPlaceHolderID="ContentHeader">
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>
</asp:Content>
