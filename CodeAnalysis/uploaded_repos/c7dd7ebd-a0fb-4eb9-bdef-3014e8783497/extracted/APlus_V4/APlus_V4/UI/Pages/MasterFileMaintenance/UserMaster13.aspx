<%@ Page Language="vb" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="~/UI/Pages/MasterFileMaintenance/UserMaster13.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.UserMaster13" Title="User Master Attendance Compare" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td>
            </td>
            <td style="width: 340px">
                <asp:Label ID="Label1" runat="server" Font-Bold="True" CssClass="Label_Left_8PT"
                    Text="A Plus"></asp:Label>
            </td>
            <td align="center" width="5">
            </td>
            <td>
                <asp:Label ID="Label2" runat="server" Font-Bold="True" CssClass="Label_Left_8PT"
                    Text="Attendance Record"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="lblUserName" runat="server" CssClass="Label_Left_8PT" Text="User Name:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtUserID" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                    Width="255px"></asp:TextBox>
            </td>
            <td align="center">
            </td>
            <td>
                <asp:TextBox ID="txtITUserID" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblFirstName" runat="server" CssClass="Label_Left_8PT" Text="First Name:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtFirstName" runat="server" CssClass="Textbox_Entry" MaxLength="25"></asp:TextBox>
            </td>
            <td align="center">
                <asp:Label ID="lblDifFirstName" runat="server" ForeColor="Red" Visible="False" CssClass="Label_Left_8PT"
                    Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtITFirstName" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="lblLastName" runat="server" CssClass="Label_Left_8PT" Text="Last Name:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtLastName" runat="server" CssClass="Textbox_Entry" MaxLength="25"></asp:TextBox>
            </td>
            <td align="center">
                <asp:Label ID="lblDifLastName" CssClass="Label_Left_8PT" runat="server" ForeColor="Red"
                    Visible="False" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtITLastName" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="lblMiddleInitial" CssClass="Label_Left_8PT" runat="server" Text="Middle Initial:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtMiddleInitial" runat="server" CssClass="Textbox_Entry" MaxLength="5"
                    Width="55px"></asp:TextBox>
            </td>
            <td align="center">
                <asp:Label ID="lblDifMiddle" CssClass="Label_Left_8PT" runat="server" ForeColor="Red"
                    Visible="False" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtITMiddleInitial" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="lblSite" CssClass="Label_Left_8PT" runat="server" Text="Site:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="191px">
                </asp:DropDownList>
            </td>
            <td align="center">
                <asp:Label ID="lblDifSite" CssClass="Label_Left_8PT" runat="server" ForeColor="Red"
                    Visible="False" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtITSite" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td>
                <asp:Label ID="lblTitle" CssClass="Label_Left_8PT" runat="server" Text="Title:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtTitle" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="256px"></asp:TextBox>
            </td>
            <td align="center">
            </td>
            <td>
                <asp:TextBox ID="txtITTitle" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="lblEmailAddress" CssClass="Label_Left_8PT" runat="server" Text="Email Address:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:TextBox ID="txtEmailAddress" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="256px"></asp:TextBox>
            </td>
            <td align="center">
                <asp:Label ID="lblDifEmail" CssClass="Label_Left_8PT" runat="server" ForeColor="Red"
                    Visible="False" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtITEmailAddress" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="272px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 119px">
                <asp:Label ID="Label3" CssClass="Label_Left_8PT" runat="server" Text="Active:"></asp:Label>
            </td>
            <td style="width: 340px">
                <asp:CheckBox ID="ckActive" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
            <td align="center">
                <asp:Label ID="lblDifActive" CssClass="Label_Left_8PT" runat="server" ForeColor="Red"
                    Visible="False" Text="*"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckITActive" runat="server" Enabled="False" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
</asp:Content>
