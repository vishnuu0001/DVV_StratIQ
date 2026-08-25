<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIEvents2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIEvents2"
    Title="OPI Events" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/CommonFunctions.js"></script>
    <table class="Table_Default" id="Table1" cellspacing="2" cellpadding="2" border="0">
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblRouteAbbrev" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtTeam" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    MaxLength="15" Width="175px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblRoute" runat="server" Text="OPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtOPI" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    MaxLength="50" Width="175px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblEventDate" runat="server" Text="Event Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtEventDate" runat="server" Width="80px" CssClass="Textbox_Entry"></asp:TextBox>
                <cc1:CalendarExtender ID="txtEventDate_CalendarExtender" runat="server" PopupButtonID="imgEventDate"
                    TargetControlID="txtEventDate" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgEventDate" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqEventDate" runat="server" CssClass="Label_Left_8PT"
                    Display="None" ControlToValidate="txtEventDate" ErrorMessage="Enter Event Date"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpEventDate" runat="server" Display="None" ControlToValidate="txtEventDate"
                        CssClass="Label_Left_8PT" ErrorMessage="Invalid Event Date" Type="Date" Operator="DataTypeCheck"></asp:CompareValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblDescription" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDescription" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="280px"></asp:TextBox><asp:RequiredFieldValidator ID="reqDescription" runat="server"
                        CssClass="Label_Left_8PT" Display="None" ControlToValidate="txtDescription" ErrorMessage="Enter Description"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblShortDescription" runat="server" Text="Short Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtShortDescription" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="160px"></asp:TextBox><asp:RequiredFieldValidator ID="reqShortDescription"
                        CssClass="Label_Left_8PT" runat="server" Display="None" ControlToValidate="txtShortDescription"
                        ErrorMessage="Enter Short Description"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblLineWidth" runat="server" Text="Line Width:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlLineWidth" runat="server" Width="40px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="1">1</asp:ListItem>
                    <asp:ListItem Value="2">2</asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtLineWidth" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    MaxLength="50" Width="32px" Visible="False"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqWidth" runat="server" Display="None" ControlToValidate="ddlLineWidth"
                        CssClass="Label_Left_8PT" ErrorMessage="Select Line Width"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblLineStyle" runat="server" Text="Line Style:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlLineStyle" runat="server" Width="120px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="0" Text="Solid"></asp:ListItem>
                    <asp:ListItem Value="1" Text="Dashed"></asp:ListItem>
                    <asp:ListItem Value="2" Text="Dot"></asp:ListItem>
                    <asp:ListItem Value="3" Text="Dash Dot"></asp:ListItem>
                    <asp:ListItem Value="4" Text="Dash Dot Dot"></asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtLineStyle" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    MaxLength="50" Width="104px" Visible="False"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqStyle" runat="server" Display="None" ControlToValidate="ddlLineStyle"
                        CssClass="Label_Left_8PT" ErrorMessage="Select Line Style"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 114px">
                <asp:Label ID="lblLineColor" runat="server" Text="Line Color:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlLineColor" runat="server" Width="120px" CssClass="DropdownList_Entry">
                    <asp:ListItem></asp:ListItem>
                    <asp:ListItem Value="Black" Text="Black"></asp:ListItem>
                    <asp:ListItem Value="Blue" Text="Blue"></asp:ListItem>
                    <asp:ListItem Value="Green" Text="Green"></asp:ListItem>
                    <asp:ListItem Value="Orange" Text="Orange"></asp:ListItem>
                    <asp:ListItem Value="Red" Text="Red"></asp:ListItem>
                </asp:DropDownList>
                <asp:TextBox ID="txtLineColor" runat="server" ReadOnly="True" CssClass="Textbox_Display"
                    MaxLength="50" Width="104px" Visible="False"></asp:TextBox><asp:RequiredFieldValidator
                        ID="reqLineColor" runat="server" Display="None" ControlToValidate="ddlLineColor"
                        CssClass="Label_Left_8PT" ErrorMessage="Select Line Color"></asp:RequiredFieldValidator>
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
