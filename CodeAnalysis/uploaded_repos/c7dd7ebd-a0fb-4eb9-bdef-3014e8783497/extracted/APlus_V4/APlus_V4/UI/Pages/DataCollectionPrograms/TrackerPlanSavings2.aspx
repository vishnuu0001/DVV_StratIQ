<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TrackerPlanSavings2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TrackerPlanSavings2"
    Title="Master Plan Maintenance" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblPeriod" runat="server" Text="Period:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPeriod" runat="server" Width="100px" MaxLength="15" CssClass="Textbox_Entry"
                    Height="16px"></asp:TextBox>
                <CC1:CalendarExtender ID="txtPeriod_CalendarExtender" runat="server" Enabled="True"
                    PopupButtonID="imgPeriod" TargetControlID="txtPeriod" CssClass="APlus_Calendar"
                    Format="MM/01/yyyy">
                </CC1:CalendarExtender>
                <asp:ImageButton ID="imgPeriod" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqPeriod" runat="server" ErrorMessage="Enter Period"
                    ControlToValidate="txtPeriod" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSavings" runat="server" Text="Plan Savings:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPlanSavings" runat="server" Width="100px" MaxLength="15" CssClass="Textbox_Entry"
                    Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSavings" runat="server" ErrorMessage="Enter Plan Savings"
                    ControlToValidate="txtPlanSavings" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblStretch" runat="server" Text="Stretch Savings:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStretchSavings" runat="server" Width="100px" MaxLength="15" CssClass="Textbox_Entry"
                    Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqStretch" runat="server" ErrorMessage="Enter Stretch Savings"
                    ControlToValidate="txtStretchSavings" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons">
            <tr>
                <td class="style1">
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
        <table id="Table3">
            <tr>
                <td style="width: 150px">
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
