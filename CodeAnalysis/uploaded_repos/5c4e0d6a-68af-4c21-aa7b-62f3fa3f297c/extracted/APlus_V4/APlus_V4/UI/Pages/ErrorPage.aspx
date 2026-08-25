<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="ErrorPage.aspx.vb" Inherits="WebApp.APlus.UI.Pages.ErrorPage"
    Title="Logout" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table>
        <tr>
            <td>
                <asp:Label ID="Label1" runat="server" Text="An unrecoverable error occured.  Please describe what you doing before you were sent to this page:"
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td>
                <asp:TextBox ID="txtExpandFeedback" runat="server" TextMode="MultiLine" Height="180px"
                    Width="400px" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
    </table>
    <table id="Table1" cellspacing="0" cellpadding="4" border="0">
        <tr>
            <td>
                An error has occurred in this application.&nbsp;You will be logged out and will
                have to enter your User Name and Password again in order to use&nbsp;the application.
            </td>
        </tr>
    </table>
    <br />
    <br />
    <asp:Button ID="btnOK" runat="server" EnableViewState="False" CssClass="Button_Default"
        Text="OK"></asp:Button>&nbsp;
    <br />
    <br />
</asp:Content>
