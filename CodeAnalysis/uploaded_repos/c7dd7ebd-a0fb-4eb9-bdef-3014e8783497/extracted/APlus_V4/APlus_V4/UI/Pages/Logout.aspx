<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="Logout.aspx.vb" Inherits="WebApp.APlus.UI.Pages.Logout"
    Title="Logout" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table id="Table1" cellspacing="0" cellpadding="4" border="0">
        <tr>
            <td>
                <br />
                <asp:Label ID="Label1" runat="server" Text="You are about to leave the application.&nbsp;You will have to enter your User Name
                and Password again in order to use the application." CssClass="Label_Left_10PT"></asp:Label>
            </td>
        </tr>
    </table>
    <p>
    </p>
    <asp:CheckBox ID="chkAutoLogin" runat="server" Text="Remove Auto Login" Visible="False"
        CssClass="Checkbox_Default"></asp:CheckBox>
    <p>
    </p>
    <asp:Button ID="btnLogout" runat="server" EnableViewState="False" CssClass="Button_Default"
        Text="Logout"></asp:Button>&nbsp;
    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel">
    </asp:Button>
    <br />
    <br />
</asp:Content>
