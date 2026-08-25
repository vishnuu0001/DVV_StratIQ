<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster6.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster6"
    Title="User Master Active Directory Conflicts" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 70px">
            </td>
            <td style="width: 270px">
                <asp:Label ID="Label1" runat="server" Font-Bold="True" Text="User Master"></asp:Label>
            </td>
            <td style="width: 11px; text-align: center;">
            </td>
            <td>
                <asp:Label ID="Label2" runat="server" Font-Bold="True" Text="Active Directory"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblUserName" runat="server" CssClass="Label_Left_8PT" Text="User Name:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtUserID" runat="server" Width="255px" MaxLength="15" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
            </td>
            <td>
                <asp:TextBox ID="txtADUserID" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblFirstName" runat="server" CssClass="Label_Left_8PT" Text="First Name:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtFirstName" runat="server" MaxLength="25" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifFirstName" runat="server" Visible="False" ForeColor="Red" Text="*"
                    CssClass="Label_ErrorControl"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADFirstName" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblLastName" runat="server" CssClass="Label_Left_8PT" Text="Last Name:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtLastName" runat="server" MaxLength="25" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifLastName" runat="server" Visible="False" ForeColor="Red" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADLastName" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblMiddleInitial" runat="server" CssClass="Label_Left_8PT" Text="Middle Initial:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtMiddleInitial" runat="server" Width="55px" MaxLength="5" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifMiddle" runat="server" Visible="False" ForeColor="Red" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADMiddle" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblSite" runat="server" CssClass="Label_Left_8PT" Text="Site:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:DropDownList ID="ddlSite" runat="server" Width="191px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifSite" runat="server" Visible="False" ForeColor="Red" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADSite" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblTitle" runat="server" CssClass="Label_Left_8PT" Text="Title:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtTitle" runat="server" Width="256px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
            </td>
            <td>
                <asp:TextBox ID="txtADTitle" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="lblEmailAddress" runat="server" CssClass="Label_Left_8PT" Text="Email Address:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:TextBox ID="txtEmailAddress" runat="server" Width="256px" MaxLength="50" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifEmail" runat="server" Visible="False" ForeColor="Red" Text="*"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtADEmail" runat="server" Width="272px" MaxLength="50" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 70px">
                <asp:Label ID="Label3" runat="server" CssClass="Label_Left_8PT" Text="Active:"></asp:Label>
            </td>
            <td style="width: 270px">
                <asp:CheckBox ID="ckActive" runat="server" CssClass="Checkbox_Default"></asp:CheckBox>
            </td>
            <td style="width: 11px; text-align: center;">
                <asp:Label ID="lblDifActive" runat="server" Visible="False" ForeColor="Red" Text="*"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckADActive" runat="server" Enabled="False" CssClass="Checkbox_Default">
                </asp:CheckBox>
            </td>
        </tr>
    </table>
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
</asp:Content>
