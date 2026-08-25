<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="CalendarEvents2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CalendarEvents2"
    Title="Calendar Event" %>

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
    <table id="Table1" cellpadding="2" cellspacing="2" style="width: 100%">
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label1" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="216px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="232px" ReadOnly="True" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
                    ControlToValidate="ddlSite" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label2" runat="server" Text="Event Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlEventTypes" runat="server" CssClass="DropdownList_Entry"
                    Width="216px">
                </asp:DropDownList>
                <asp:TextBox ID="txtEventType" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="232px" ReadOnly="True" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqEventType" runat="server" ErrorMessage="Select Event Type"
                    ControlToValidate="ddlEventTypes" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Event:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEvent" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                    Width="175px"></asp:TextBox><asp:RequiredFieldValidator ID="reqEvent" runat="server"
                        ErrorMessage="Enter Event" ControlToValidate="txtEvent" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblAttribute1" runat="server" Text="Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDate" runat="server" CssClass="Textbox_Entry" MaxLength="12"
                    Width="150px"></asp:TextBox>
                <cc1:CalendarExtender ID="txtDate_CalendarExtender" runat="server" PopupButtonID="imgDate"
                    TargetControlID="txtDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqDate" runat="server" ErrorMessage="Enter Date"
                    ControlToValidate="txtDate" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="Label3" runat="server" Text="Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTime" runat="server" CssClass="Textbox_Entry" MaxLength="5" Width="56px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:Label ID="lblRoute" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandDescription" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="325px" TextMode="MultiLine" Rows="1" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 150px">
                <asp:HyperLink ID="lnkPrintPage" runat="server" Target="_blank" NavigateUrl="CalendarEvents3.aspx"
                    Visible="False" Text="Printer Friendly Version"></asp:HyperLink>
            </td>
            <td>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px" align="left">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                        Text="OK"></asp:Button>
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
                <td align="left">
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
