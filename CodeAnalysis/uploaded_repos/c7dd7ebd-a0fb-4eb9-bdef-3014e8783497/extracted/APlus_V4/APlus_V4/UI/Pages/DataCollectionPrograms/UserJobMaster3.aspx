<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserJobMaster3.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserJobMaster3"
    Title="User Job Master" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 85px">
                <asp:Label ID="Label1" runat="server" Text="Job ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtJobID" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    Width="40px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="Label2" runat="server" Text="Job:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtJob" Width="313px" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="Label6" runat="server" Text="User ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUserID" Width="313px" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 85px">
                <asp:Label ID="Label3" runat="server" Text="User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUser" Width="313px" MaxLength="50" CssClass="Textbox_Display"
                    runat="server"></asp:TextBox>
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
        </table>
    </asp:Panel>
</asp:Content>
