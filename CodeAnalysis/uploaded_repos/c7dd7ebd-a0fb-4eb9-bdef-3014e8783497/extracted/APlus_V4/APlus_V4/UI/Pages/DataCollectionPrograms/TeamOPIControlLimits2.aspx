<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIControlLimits2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIControlLimits2"
    Title="OPI Control Limits" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeam" runat="server" Width="175px" MaxLength="15" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblRoute" runat="server" Text="OPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOPI" runat="server" Width="175px" MaxLength="50" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblStartDate" runat="server" Text="Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStartDate" runat="server" CssClass="Textbox_Entry" Width="80px"></asp:TextBox>
                <cc1:CalendarExtender ID="txtStartDate_CalendarExtender" runat="server" PopupButtonID="imgStartDate"
                    TargetControlID="txtStartDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqStartDate" runat="server" ErrorMessage="Enter Start Date"
                    CssClass="Label_Left_8PT" ControlToValidate="txtStartDate" Display="None"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="cmpStartDate" runat="server" ErrorMessage="Invalid Start Date"
                    CssClass="Label_Left_8PT" ControlToValidate="txtStartDate" Display="None" Operator="DataTypeCheck"
                    Type="Date"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblUpperValue" runat="server" Text="Upper Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUpperValue" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                    Width="80px"></asp:TextBox>
                <asp:RegularExpressionValidator ID="reqUpperValueValid" runat="server" CssClass="Label_Left_8PT"
                    ErrorMessage="Invalid Upper Value Entry" ControlToValidate="txtUpperValue" Display="None"></asp:RegularExpressionValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblLowerValue" runat="server" Text="Lower Value:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtLowerValue" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                    Width="80px"></asp:TextBox>
                <asp:RegularExpressionValidator ID="reqLowerValueValid" runat="server" ErrorMessage="Invalid Lower Value Entry"
                    CssClass="Label_Left_8PT" ControlToValidate="txtLowerValue" Display="None"></asp:RegularExpressionValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblDescription" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" Width="325px" CssClass="Textbox_Entry"
                    MaxLength="250" TextMode="MultiLine" Rows="1"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
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
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
