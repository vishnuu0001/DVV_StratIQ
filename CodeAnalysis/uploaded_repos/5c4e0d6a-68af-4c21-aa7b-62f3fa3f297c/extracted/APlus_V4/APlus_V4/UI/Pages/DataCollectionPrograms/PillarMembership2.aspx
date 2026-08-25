<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PillarMembership2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.PillarMembership2"
    Title="Pillar Membership Maintenance" %>

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
            <td style="width: 81px">
                <asp:Label ID="Label2" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="width: 81px">
                <asp:DropDownList ID="ddlSites" runat="server" CssClass="DropdownList_Entry" Width="216px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" Width="256px"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="lblPillar" runat="server" Text="Pillar:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlPillar" runat="server" CssClass="DropdownList_Entry" Width="281px">
                </asp:DropDownList>
                <asp:TextBox ID="txtPillar" runat="server" CssClass="Textbox_Display" Width="297px"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="lblUserID" runat="server" Text="User:" CssClass="Label_Left_8PT"> </asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlUserID" runat="server" Width="329px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtUserID" runat="server" Width="281px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>&nbsp;<asp:DropDownList ID="ddlUserSite" runat="server"
                        CssClass="DropdownList_Entry" Width="194px" AutoPostBack="True">
                    </asp:DropDownList>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="lblRole" runat="server" Text="Role:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlRole" runat="server" Width="261px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtRole" runat="server" Width="258px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 81px">
                <asp:Label ID="Label1" runat="server" Text="Date Joined:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDateJoined" runat="server" Width="81px" CssClass="Textbox_Entry"
                    MaxLength="40"></asp:TextBox>
                <cc1:CalendarExtender ID="txtDateJoined_CalendarExtender" runat="server" PopupButtonID="imgDateJoined"
                    TargetControlID="txtDateJoined" CssClass="APlus_Calendar">
                </cc1:CalendarExtender>
                <asp:ImageButton ID="imgDateJoined" runat="server" ImageUrl="~/Images/date-time_select.gif"
                    ToolTip="Click to Select Date..." CausesValidation="False" />
                <asp:RequiredFieldValidator ID="reqDateJoined" runat="server" Display="None" ControlToValidate="txtDateJoined"
                    ErrorMessage="Enter Date Joined" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
                <asp:CompareValidator ID="cmpDateJoined" runat="server" ControlToValidate="txtDateJoined"
                    Type="Date" Display="None" Operator="DataTypeCheck" ErrorMessage="Invalid Date"
                    CssClass="Label_Left_8PT"></asp:CompareValidator><br />
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
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
