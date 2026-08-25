<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamMeetingAttendance2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamMeetingAttendance2"
    Title="Team Meeting Attendance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblMeetingDate" runat="server" Text="Meeting Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMeetingDate" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblMeetingTime" runat="server" Text="Meeting Time:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMeetingTime" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px; height: 8px">
                <asp:Label ID="lblUserName" runat="server" Text="User Name:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td style="height: 8px">
                <asp:DropDownList ID="ddlUserID" runat="server" Width="264px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtUserID" CssClass="Textbox_Display" MaxLength="15" Width="232px"
                    ReadOnly="True" runat="server"></asp:TextBox>
                &nbsp;<asp:Label ID="lblOr" runat="server" Text="or" CssClass="Label_Left_8PT"></asp:Label>
                &nbsp;<asp:TextBox ID="txtUserName" runat="server" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblInvited" runat="server" Text="Invited:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkInvited" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblAttended" runat="server" Text="Attended:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="chkAttended" runat="server"></asp:CheckBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblMaintenanceUserID" runat="server" Text="Maintenance UserID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaintenanceUserID" runat="server" CssClass="Textbox_Display"
                    MaxLength="10" Width="80px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 110px">
                <asp:Label ID="lblMaintenanceDate" runat="server" Text="Maintenance Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtMaintenanceDate" runat="server" CssClass="Textbox_Display" MaxLength="10"
                    Width="150px" ReadOnly="True"></asp:TextBox>
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
            <tr>
                <td colspan="2">
                    <asp:CheckBox ID="ckAllSites" runat="server" Text="Show Users from all Sites" AutoPostBack="True">
                    </asp:CheckBox>
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
</asp:Content>
