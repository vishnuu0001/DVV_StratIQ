<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamActionPlan2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamActionPlan2"
    Title="Team Action Plan Maintenance" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblActionNumber" runat="server" Text="Action Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtActionNumber" runat="server" Width="42px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlAction" runat="server">
        <table id="Table7" class="Table_Default">
            <tr>
                <td style="width: 112px; height: 21px">
                    <asp:Label ID="lblMeeting" runat="server" Text="Meeting:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td style="height: 21px">
                    <asp:DropDownList ID="ddlMeetings" runat="server" Width="328px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtTeamMeeting" runat="server" CssClass="Textbox_Display" Visible="False"
                        Width="262px"></asp:TextBox>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <table class="Table_Default" id="Table2">
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblStepNo" runat="server" Text="Step Number:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:DropDownList ID="ddlStepNo" runat="server" Width="448px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtStepNo" runat="server" Width="262px" CssClass="Textbox_Display"
                    Visible="False"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblActionItem" runat="server" Text="Action Item:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtActionItem" runat="server" Width="625px" MaxLength="100" CssClass="Textbox_Entry"></asp:TextBox><asp:RequiredFieldValidator
                    ID="reqActionItem" runat="server" Display="None" ControlToValidate="txtActionItem"
                    ErrorMessage="EnterAction Item"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 112px; height: 49px; vertical-align: top;">
                <asp:Label ID="lblActionItemDefinition" runat="server" Text="Action Item Definition:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 49px">
                <asp:TextBox ID="txtExpandActionItemDefinition" runat="server" Width="456px" MaxLength="500"
                    CssClass="Textbox_Entry" Height="48px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblAssignedTo" runat="server" Text="Assigned To:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:DropDownList ID="ddlAssignedTo" runat="server" Width="298px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqAssignedTo" runat="server" ErrorMessage="Enter Assigned To"
                    ControlToValidate="ddlAssignedTo" Display="None"></asp:RequiredFieldValidator>
                <asp:TextBox ID="txtAssignedTo" runat="server" Width="262px" Visible="False" CssClass="Textbox_Display"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px" valign="top">
                <asp:Label ID="lblAssignedToOther" runat="server" Text="Assigned To Other:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td valign="top">
                <asp:TextBox ID="txtAssignedToOther" runat="server" Width="453px" MaxLength="200"
                    CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblTargetDate" runat="server" Text="Target Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTargetDate" runat="server" Width="71px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtTargetDate_CalendarExtender" runat="server" PopupButtonID="imgTargetDate"
                    TargetControlID="txtTargetDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgTargetDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqTargetDate" runat="server" Display="None" ControlToValidate="txtTargetDate"
                    ErrorMessage="Enter Target Date" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="cmpTargetDate" runat="server" Display="None" ControlToValidate="txtTargetDate"
                    ErrorMessage="Invalid Target Date" Operator="DataTypeCheck" Type="Date"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblActions" runat="server" Text="Actions:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandActions" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="400px" Height="28px" TextMode="MultiLine"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                <asp:Label ID="lblClosedDate" runat="server" Text="Closed Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtClosedDate" runat="server" Width="71px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtClosedDate_CalendarExtender" runat="server" PopupButtonID="imgClosedDate"
                    TargetControlID="txtClosedDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgClosedDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:CompareValidator ID="compClosedDate" runat="server" ErrorMessage="Invalid Closed Date"
                    ControlToValidate="txtClosedDate" Display="None" Type="Date" Operator="DataTypeCheck"
                    CssClass="Label_Left_8PT"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 112px">
                &nbsp;
            </td>
            <td>
                <asp:RadioButtonList ID="rblCancelled" runat="server" RepeatDirection="Horizontal"
                    Width="200px">
                    <asp:ListItem Value="0">Completed</asp:ListItem>
                    <asp:ListItem Value="1">Cancelled</asp:ListItem>
                </asp:RadioButtonList>
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
