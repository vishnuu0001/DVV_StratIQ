<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamRouteSteps2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamRouteSteps2"
    Title="Route Steps Master" %>

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
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Route:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtRoute" runat="server" Width="368px" CssClass="Textbox_Display"
                    MaxLength="60"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="lblRoute" runat="server" Text="Step Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtStepNumber" runat="server" Width="43px" CssClass="Textbox_Display"
                    MaxLength="4"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="lblRouteDefinition" runat="server" Text="Step:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 15px">
                <asp:TextBox ID="txtStep" runat="server" Width="525px" CssClass="Textbox_Display"
                    MaxLength="100" Height="18px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 100px; height: 22px" valign="top">
                <asp:Label ID="lblMasterTemplatePath" runat="server" Text="Step Definition:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 22px">
                <asp:TextBox ID="txtExpandStepDefinition" runat="server" Width="600px" CssClass="Textbox_Display"
                    MaxLength="500" Height="16px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 100px; height: 23px" valign="top">
                <asp:Label ID="Label1" runat="server" Text="Planned Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 23px">
                <asp:TextBox ID="txtPlannedStartDate" runat="server" Width="80px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtPlannedStartDate_CalendarExtender" runat="server" PopupButtonID="imgPlannedStartDate"
                    TargetControlID="txtPlannedStartDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgPlannedStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="Comparevalidator3" runat="server" Operator="DataTypeCheck"
                    Type="Date" Display="None" ControlToValidate="txtPlannedStartDate" ErrorMessage="Invalid Planned Start Date"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="Label2" runat="server" Text="Planned End Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtPlannedEndDate" runat="server" Width="80px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtPlannedEndDate_CalendarExtender" runat="server" PopupButtonID="imgPlannedEndDate"
                    TargetControlID="txtPlannedEndDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgPlannedEndDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="Comparevalidator2" runat="server" Operator="DataTypeCheck"
                    Type="Date" Display="None" ControlToValidate="txtPlannedEndDate" ErrorMessage="Invalid Planned End Date"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="Label3" runat="server" Text="Actual Start Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtActualStartDate" runat="server" Width="80px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtActualStartDate_CalendarExtender" runat="server" PopupButtonID="imgActualStartDate"
                    TargetControlID="txtActualStartDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgActualStartDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="Comparevalidator1" runat="server" Operator="DataTypeCheck"
                    Type="Date" Display="None" ControlToValidate="txtActualStartDate" ErrorMessage="Invalid Actual Start Date"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 100px" valign="top">
                <asp:Label ID="Label4" runat="server" Text="Actual End Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtActualEndDate" runat="server" Width="80px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtActualEndDate_CalendarExtender" runat="server" PopupButtonID="imgActualEndDate"
                    TargetControlID="txtActualEndDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgActualEndDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="cmpStartDate" runat="server" Operator="DataTypeCheck" Type="Date"
                    Display="None" ControlToValidate="txtActualEndDate" ErrorMessage="Invalid Actual End Date"></asp:CompareValidator>
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False"
        Translate="true" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
