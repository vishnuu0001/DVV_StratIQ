<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamMembership2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMembership2"
    Title="Team Membership" %>

<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="cc1" %>
<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblTeam" runat="server" Text="Team:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <asp:DropDownList ID="ddlTeam" runat="server" AutoPostBack="True" Width="250px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtTeam" runat="server" Width="350px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqTeam" runat="server" ErrorMessage="Select Team"
                    ControlToValidate="ddlTeam" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblUserID" runat="server" Text="User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <p>
                    <asp:DropDownList ID="ddlUserID" runat="server" Width="232px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtUserID" runat="server" Width="216px" CssClass="Textbox_Display"
                        ReadOnly="True"></asp:TextBox>
                    <asp:RequiredFieldValidator ID="reqUser" runat="server" ErrorMessage="Select User"
                        ControlToValidate="ddlUserID" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>&nbsp;<asp:DropDownList
                            ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="194px" AutoPostBack="True">
                        </asp:DropDownList>
                </p>
            </td>
        </tr>
        <tr id="rowTitle" runat="server">
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblTitle" runat="server" Text="Title:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <asp:TextBox ID="txtTitle" runat="server" Width="258px" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblRole" runat="server" Text="Role:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <p>
                    <asp:DropDownList ID="ddlRole" runat="server" Width="272px" CssClass="DropdownList_Entry">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtRole" runat="server" Width="258px" CssClass="Textbox_Display"
                        ReadOnly="True"></asp:TextBox></p>
            </td>
        </tr>
        <tr>
            <td style="width: 81px; height: 26px">
                <asp:Label ID="lblSecondaryRole" runat="server" Text="Secondary Role:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px">
                <asp:DropDownList ID="ddlSecondaryRole" runat="server" Width="272px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtSecondaryRole" runat="server" Width="258px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px; height: 26px" valign="top">
                <asp:Label ID="lblDateJoined" runat="server" Text="Date Joined:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 26px" valign="top">
                <asp:TextBox ID="txtDateJoined" runat="server" Width="81px" CssClass="Textbox_Entry"
                    MaxLength="40"></asp:TextBox>
                <cc1:CalendarExtender ID="txtDateJoined_CalendarExtender" runat="server" PopupButtonID="imgDateJoined"
                    TargetControlID="txtDateJoined" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgDateJoined" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqDateJoined" runat="server" Display="None" ControlToValidate="txtDateJoined"
                    ErrorMessage="Enter Date Joined" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator><asp:CompareValidator
                        ID="cmpDateJoined" runat="server" Display="None" ControlToValidate="txtDateJoined"
                        ErrorMessage="Invalid Date" Type="Date" Operator="DataTypeCheck" CssClass="Label_Left_8PT"></asp:CompareValidator>
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
